import { google } from 'googleapis';
import { OAuth2Client, Credentials } from 'google-auth-library';
import { createServer, IncomingMessage, ServerResponse } from 'node:http';
import { readFileSync, existsSync } from 'node:fs';
import { exec } from 'node:child_process';
import { loadTokens, saveTokens, clearTokens, StoredTokens } from './token-store.js';

export const MONETARY_SCOPE = 'https://www.googleapis.com/auth/yt-analytics-monetary.readonly';

const SCOPES = [
  'https://www.googleapis.com/auth/youtube',
  'https://www.googleapis.com/auth/yt-analytics.readonly',
  MONETARY_SCOPE,
];

const OAUTH_TIMEOUT_MS = 120_000;

interface InstalledCredentials {
  installed?: {
    client_id: string;
    client_secret: string;
    redirect_uris?: string[];
  };
}

let cachedClient: OAuth2Client | null = null;

function loadClientCredentials(): { clientId: string; clientSecret: string } {
  if (process.env.GOOGLE_CLIENT_ID && process.env.GOOGLE_CLIENT_SECRET) {
    return {
      clientId: process.env.GOOGLE_CLIENT_ID,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET,
    };
  }

  const secretPath = process.env.GOOGLE_CLIENT_SECRET_PATH;
  if (secretPath && existsSync(secretPath)) {
    const config: InstalledCredentials = JSON.parse(readFileSync(secretPath, 'utf8'));
    if (config.installed) {
      return {
        clientId: config.installed.client_id,
        clientSecret: config.installed.client_secret,
      };
    }
  }

  throw new Error(
    'OAuth 2.0 credentials not configured. Set GOOGLE_CLIENT_SECRET_PATH to your client_secret.json, ' +
    'or set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables.'
  );
}

export function hasOAuthCredentials(): boolean {
  try {
    loadClientCredentials();
    return true;
  } catch {
    return false;
  }
}

export function isAuthenticated(): boolean {
  return Boolean(loadTokens()?.refresh_token);
}

export function getGrantedScopes(): string[] {
  const tokens = loadTokens();
  if (!tokens?.scope) return [];
  return tokens.scope.split(/\s+/).filter(Boolean);
}

export function hasMonetaryScope(): boolean {
  return getGrantedScopes().includes(MONETARY_SCOPE);
}

export function requireMonetaryScope(): void {
  if (!hasMonetaryScope()) {
    throw new Error(
      'Revenue metrics require the yt-analytics-monetary.readonly OAuth scope, ' +
      'which is not present on the current token. Run auth_reauthenticate to grant it. ' +
      'Reminder: the Cloud Console OAuth consent screen must also list this scope.'
    );
  }
}

function getRedirectUri(port: number): string {
  return `http://localhost:${port}/oauth2callback`;
}

function createClientForPort(port: number): OAuth2Client {
  const { clientId, clientSecret } = loadClientCredentials();
  return new google.auth.OAuth2(clientId, clientSecret, getRedirectUri(port));
}

export function getOAuth2Client(): OAuth2Client {
  if (cachedClient) {
    return cachedClient;
  }

  // Port doesn't matter for token refresh; only needed during the initial auth flow.
  const { clientId, clientSecret } = loadClientCredentials();
  const client = new google.auth.OAuth2(clientId, clientSecret, 'http://localhost');

  client.on('tokens', (tokens) => {
    saveTokens(tokens as StoredTokens);
  });

  cachedClient = client;
  return client;
}

export async function getAuthenticatedClient(): Promise<OAuth2Client> {
  const client = getOAuth2Client();

  const stored = loadTokens();
  if (stored?.refresh_token) {
    client.setCredentials(stored as Credentials);
    return client;
  }

  throw new Error(
    'Not authenticated. Call the auth_authenticate tool first to authorise via OAuth 2.0.'
  );
}

function openBrowser(url: string): void {
  const cmd = process.platform === 'darwin' ? 'open'
    : process.platform === 'win32' ? 'start'
    : 'xdg-open';

  exec(`${cmd} "${url}"`, (error) => {
    if (error) {
      console.error(`[OAuth] Could not open browser: ${error.message}`);
    }
  });
}

function htmlPage(title: string, body: string): string {
  return `<!DOCTYPE html><html><head><meta charset="utf-8"><title>${title}</title>
<style>body{font-family:system-ui,sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;margin:0;background:#f8f9fa}
.card{background:#fff;border-radius:12px;padding:48px;box-shadow:0 2px 8px rgba(0,0,0,.1);text-align:center;max-width:480px}
h1{margin:0 0 12px;font-size:24px}p{color:#666;margin:0}</style>
</head><body><div class="card"><h1>${title}</h1><p>${body}</p></div></body></html>`;
}

export async function authenticate(): Promise<{ success: boolean; message: string }> {
  return new Promise((resolve) => {
    const server = createServer(async (req: IncomingMessage, res: ServerResponse) => {
      const url = new URL(req.url || '/', `http://localhost:${port}`);

      if (url.pathname !== '/oauth2callback') {
        res.writeHead(404, { 'Content-Type': 'text/html' });
        res.end(htmlPage('Not Found', ''));
        return;
      }

      const error = url.searchParams.get('error');
      if (error) {
        res.writeHead(400, { 'Content-Type': 'text/html' });
        res.end(htmlPage('Authentication failed', error));
        cleanup();
        resolve({ success: false, message: `Authentication denied: ${error}` });
        return;
      }

      const code = url.searchParams.get('code');
      if (!code) {
        res.writeHead(400, { 'Content-Type': 'text/html' });
        res.end(htmlPage('Error', 'No authorization code received.'));
        cleanup();
        resolve({ success: false, message: 'No authorization code received.' });
        return;
      }

      try {
        const oauthClient = createClientForPort(port);
        const { tokens } = await oauthClient.getToken(code);
        saveTokens(tokens as StoredTokens);

        // Update the cached client with fresh tokens
        cachedClient = null;
        const client = getOAuth2Client();
        client.setCredentials(tokens as Credentials);

        res.writeHead(200, { 'Content-Type': 'text/html' });
        res.end(htmlPage('Authentication successful', 'You can close this tab and return to Cursor.'));
        cleanup();
        resolve({
          success: true,
          message: `OAuth 2.0 authentication successful. Tokens saved. Granted scopes: ${tokens.scope || SCOPES.join(' ')}`,
        });
      } catch (err) {
        const msg = err instanceof Error ? err.message : String(err);
        res.writeHead(500, { 'Content-Type': 'text/html' });
        res.end(htmlPage('Token exchange failed', msg));
        cleanup();
        resolve({ success: false, message: `Token exchange failed: ${msg}` });
      }
    });

    let port = 0;
    let timer: ReturnType<typeof setTimeout>;

    function cleanup() {
      clearTimeout(timer);
      server.close();
    }

    timer = setTimeout(() => {
      server.close();
      resolve({ success: false, message: 'Authentication timed out after 2 minutes. Try again.' });
    }, OAUTH_TIMEOUT_MS);

    // Bind to port 0 so the OS picks an available port.
    server.listen(0, '127.0.0.1', () => {
      const addr = server.address();
      port = typeof addr === 'object' && addr ? addr.port : 0;

      const oauthClient = createClientForPort(port);
      const authUrl = oauthClient.generateAuthUrl({
        access_type: 'offline',
        scope: SCOPES,
        prompt: 'consent',
      });

      console.error(`[OAuth] Listening on http://127.0.0.1:${port}`);
      console.error(`[OAuth] Auth URL: ${authUrl}`);
      openBrowser(authUrl);
    });
  });
}

export async function reauthenticate(): Promise<{
  cleared: boolean;
  reauthSuccess: boolean;
  grantedScopes: string[];
  message: string;
  warnings: string[];
}> {
  const warnings: string[] = [];
  const previousScopes = getGrantedScopes();

  clearTokens();
  cachedClient = null;

  const result = await authenticate();

  const grantedScopes = getGrantedScopes();
  const missingMonetary = !grantedScopes.includes(MONETARY_SCOPE);

  if (missingMonetary) {
    warnings.push(
      'yt-analytics-monetary.readonly was not granted. ' +
      'Make sure this scope is listed on your project OAuth consent screen in Google Cloud Console.'
    );
  }

  if (previousScopes.length > 0 && grantedScopes.length === 0) {
    warnings.push('Re-authentication failed; previous tokens were cleared but no new tokens were stored.');
  }

  return {
    cleared: true,
    reauthSuccess: result.success,
    grantedScopes,
    message: result.message,
    warnings,
  };
}

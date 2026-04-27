import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { homedir } from 'node:os';
import { join, dirname } from 'node:path';

const DEFAULT_TOKEN_DIR = join(homedir(), '.youtube-mcp');
const DEFAULT_TOKEN_FILE = 'tokens.json';

export interface StoredTokens {
  access_token?: string;
  refresh_token?: string;
  scope?: string;
  token_type?: string;
  expiry_date?: number;
}

function getTokenPath(): string {
  return process.env.YOUTUBE_OAUTH_TOKEN_PATH || join(DEFAULT_TOKEN_DIR, DEFAULT_TOKEN_FILE);
}

export function loadTokens(): StoredTokens | null {
  const tokenPath = getTokenPath();
  try {
    if (!existsSync(tokenPath)) {
      return null;
    }
    const raw = readFileSync(tokenPath, 'utf8');
    const parsed = JSON.parse(raw);
    return parsed?.refresh_token ? parsed : null;
  } catch {
    return null;
  }
}

export function saveTokens(tokens: StoredTokens): void {
  const tokenPath = getTokenPath();
  const dir = dirname(tokenPath);

  if (!existsSync(dir)) {
    mkdirSync(dir, { recursive: true, mode: 0o700 });
  }

  const existing = loadTokens();
  const merged = { ...existing, ...tokens };

  writeFileSync(tokenPath, JSON.stringify(merged, null, 2), { mode: 0o600 });
}

export function clearTokens(): void {
  const tokenPath = getTokenPath();
  try {
    if (existsSync(tokenPath)) {
      writeFileSync(tokenPath, '{}', { mode: 0o600 });
    }
  } catch {
    // best-effort
  }
}

// The youtube-transcript package has broken ESM/CJS resolution on Node >=25.
// Import the ESM bundle directly to bypass the faulty "main" field.
import { fetchTranscript } from "youtube-transcript/dist/youtube-transcript.esm.js";
import { TranscriptParams, SearchTranscriptParams } from '../types.js';

export class TranscriptService {
  private langConfig(language?: string) {
    const lang = language || process.env.YOUTUBE_TRANSCRIPT_LANG;
    return lang ? { lang } : undefined;
  }

  async getTranscript({
    videoId,
    language,
  }: TranscriptParams): Promise<any> {
    try {
      const config = this.langConfig(language);
      const transcript = await fetchTranscript(videoId, config);

      return {
        videoId,
        language: config?.lang ?? 'auto',
        transcript,
      };
    } catch (error) {
      throw new Error(`Failed to get transcript: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  async searchTranscript({
    videoId,
    query,
    language,
  }: SearchTranscriptParams): Promise<any> {
    try {
      const config = this.langConfig(language);
      const transcript = await fetchTranscript(videoId, config);

      const lowerQuery = query.toLowerCase();
      const matches = transcript.filter((item) =>
        item.text.toLowerCase().includes(lowerQuery)
      );

      return {
        videoId,
        query,
        matches,
        totalMatches: matches.length,
      };
    } catch (error) {
      throw new Error(`Failed to search transcript: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  async getTimestampedTranscript({
    videoId,
    language,
  }: TranscriptParams): Promise<any> {
    try {
      const config = this.langConfig(language);
      const transcript = await fetchTranscript(videoId, config);

      const timestampedTranscript = transcript.map((item) => {
        const seconds = item.offset / 1000;
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = Math.floor(seconds % 60);

        return {
          timestamp: `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`,
          text: item.text,
          startTimeMs: item.offset,
          durationMs: item.duration,
        };
      });

      return {
        videoId,
        language: config?.lang ?? 'auto',
        timestampedTranscript,
      };
    } catch (error) {
      throw new Error(`Failed to get timestamped transcript: ${error instanceof Error ? error.message : String(error)}`);
    }
  }
}
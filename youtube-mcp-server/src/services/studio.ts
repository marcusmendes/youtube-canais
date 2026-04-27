import { google } from 'googleapis';
import { getAuthenticatedClient } from '../auth/oauth-client.js';
import {
  ListOwnVideosParams,
  UpdateVideoParams,
  ListCommentsParams,
  ListChannelCommentsParams,
  AddCommentParams,
  ReplyToCommentParams,
  UpdateCommentParams,
  DeleteCommentParams,
  ModerateCommentParams,
} from '../types.js';

export class StudioService {
  private async getYouTubeClient() {
    const auth = await getAuthenticatedClient();
    return google.youtube({ version: 'v3', auth });
  }

  async getOwnChannel() {
    const youtube = await this.getYouTubeClient();
    const response = await youtube.channels.list({
      part: ['snippet', 'statistics', 'contentDetails', 'brandingSettings', 'status'],
      mine: true,
    });

    return response.data.items?.[0] || null;
  }

  async listOwnVideos({
    maxResults = 20,
    status,
    pageToken,
  }: ListOwnVideosParams) {
    const youtube = await this.getYouTubeClient();

    const channelResponse = await youtube.channels.list({
      part: ['contentDetails'],
      mine: true,
    });

    const uploadsPlaylistId =
      channelResponse.data.items?.[0]?.contentDetails?.relatedPlaylists?.uploads;
    if (!uploadsPlaylistId) {
      throw new Error('Could not find uploads playlist for your channel.');
    }

    const playlistResponse = await youtube.playlistItems.list({
      part: ['snippet', 'contentDetails', 'status'],
      playlistId: uploadsPlaylistId,
      maxResults,
      ...(pageToken ? { pageToken } : {}),
    });

    let items: any[] = playlistResponse.data.items || [];

    if (items.length > 0) {
      const videoIds = items
        .map((item) => item.contentDetails?.videoId)
        .filter(Boolean) as string[];

      const videosResponse = await youtube.videos.list({
        part: ['snippet', 'statistics', 'status', 'contentDetails'],
        id: videoIds,
      });

      const videoMap = new Map(
        (videosResponse.data.items || []).map((v) => [v.id, v])
      );

      items = items.map((item) => {
        const videoId = item.contentDetails?.videoId;
        const full = videoId ? videoMap.get(videoId) : null;
        return {
          videoId,
          title: full?.snippet?.title || item.snippet?.title,
          description: full?.snippet?.description || item.snippet?.description,
          publishedAt: full?.snippet?.publishedAt || item.snippet?.publishedAt,
          privacyStatus: full?.status?.privacyStatus || item.status?.privacyStatus,
          tags: full?.snippet?.tags || [],
          statistics: full?.statistics || null,
          duration: full?.contentDetails?.duration || null,
          thumbnails: full?.snippet?.thumbnails || item.snippet?.thumbnails,
        };
      });

      if (status) {
        items = items.filter((item) => item.privacyStatus === status);
      }
    }

    return {
      items,
      nextPageToken: playlistResponse.data.nextPageToken || null,
      totalResults: playlistResponse.data.pageInfo?.totalResults || 0,
    };
  }

  async updateVideo({
    videoId,
    title,
    description,
    tags,
    categoryId,
    privacyStatus,
    defaultLanguage,
  }: UpdateVideoParams) {
    const youtube = await this.getYouTubeClient();

    const currentResponse = await youtube.videos.list({
      part: ['snippet', 'status'],
      id: [videoId],
    });

    const current = currentResponse.data.items?.[0];
    if (!current) {
      throw new Error(`Video ${videoId} not found or you don't have access.`);
    }

    const snippet = { ...current.snippet };
    const videoStatus = { ...current.status };

    if (title !== undefined) snippet.title = title;
    if (description !== undefined) snippet.description = description;
    if (tags !== undefined) snippet.tags = tags;
    if (categoryId !== undefined) snippet.categoryId = categoryId;
    if (defaultLanguage !== undefined) snippet.defaultLanguage = defaultLanguage;
    if (privacyStatus !== undefined) videoStatus.privacyStatus = privacyStatus as any;

    const response = await youtube.videos.update({
      part: ['snippet', 'status'],
      requestBody: { id: videoId, snippet, status: videoStatus },
    });

    return response.data;
  }

  async listComments({
    videoId,
    maxResults = 20,
    order = 'relevance',
  }: ListCommentsParams) {
    const youtube = await this.getYouTubeClient();

    const response = await youtube.commentThreads.list({
      part: ['snippet', 'replies'],
      videoId,
      maxResults,
      order: order as 'time' | 'relevance',
    });

    return {
      items: (response.data.items || []).map((thread) => {
        const top = thread.snippet?.topLevelComment?.snippet;
        return {
          commentId: thread.id,
          author: top?.authorDisplayName,
          authorChannelId: top?.authorChannelId?.value,
          text: top?.textDisplay,
          likeCount: top?.likeCount,
          publishedAt: top?.publishedAt,
          totalReplyCount: thread.snippet?.totalReplyCount,
          replies: (thread.replies?.comments || []).map((reply) => ({
            commentId: reply.id,
            author: reply.snippet?.authorDisplayName,
            text: reply.snippet?.textDisplay,
            likeCount: reply.snippet?.likeCount,
            publishedAt: reply.snippet?.publishedAt,
          })),
        };
      }),
      nextPageToken: response.data.nextPageToken || null,
      totalResults: response.data.pageInfo?.totalResults || 0,
    };
  }

  async listOwnPlaylists({ maxResults = 50, pageToken }: { maxResults?: number; pageToken?: string }) {
    const youtube = await this.getYouTubeClient();

    const response = await youtube.playlists.list({
      part: ['snippet', 'contentDetails', 'status'],
      mine: true,
      maxResults,
      ...(pageToken ? { pageToken } : {}),
    });

    return {
      items: response.data.items || [],
      nextPageToken: response.data.nextPageToken || null,
      totalResults: response.data.pageInfo?.totalResults || 0,
    };
  }

  async listChannelComments({
    channelId,
    maxResults = 20,
    order = 'relevance',
  }: ListChannelCommentsParams) {
    const youtube = await this.getYouTubeClient();

    const response = await youtube.commentThreads.list({
      part: ['snippet', 'replies'],
      allThreadsRelatedToChannelId: channelId,
      maxResults,
      order: order as 'time' | 'relevance',
    });

    return {
      items: (response.data.items || []).map((thread) => {
        const top = thread.snippet?.topLevelComment?.snippet;
        return {
          commentId: thread.id,
          videoId: thread.snippet?.videoId,
          author: top?.authorDisplayName,
          authorChannelId: top?.authorChannelId?.value,
          text: top?.textDisplay,
          likeCount: top?.likeCount,
          publishedAt: top?.publishedAt,
          totalReplyCount: thread.snippet?.totalReplyCount,
          replies: (thread.replies?.comments || []).map((reply) => ({
            commentId: reply.id,
            author: reply.snippet?.authorDisplayName,
            text: reply.snippet?.textDisplay,
            likeCount: reply.snippet?.likeCount,
            publishedAt: reply.snippet?.publishedAt,
          })),
        };
      }),
      nextPageToken: response.data.nextPageToken || null,
      totalResults: response.data.pageInfo?.totalResults || 0,
    };
  }

  async addComment({ videoId, text }: AddCommentParams) {
    const youtube = await this.getYouTubeClient();

    const channelResponse = await youtube.channels.list({
      part: ['id'],
      mine: true,
    });
    const channelId = channelResponse.data.items?.[0]?.id;
    if (!channelId) {
      throw new Error('Could not determine your channel ID.');
    }

    const response = await youtube.commentThreads.insert({
      part: ['snippet'],
      requestBody: {
        snippet: {
          channelId,
          videoId,
          topLevelComment: { snippet: { textOriginal: text } },
        },
      },
    });

    return response.data;
  }

  async replyToComment({ commentId, text }: ReplyToCommentParams) {
    const youtube = await this.getYouTubeClient();

    const response = await youtube.comments.insert({
      part: ['snippet'],
      requestBody: {
        snippet: { parentId: commentId, textOriginal: text },
      },
    });

    return response.data;
  }

  async updateComment({ commentId, text }: UpdateCommentParams) {
    const youtube = await this.getYouTubeClient();

    const response = await youtube.comments.update({
      part: ['snippet'],
      requestBody: {
        id: commentId,
        snippet: { textOriginal: text },
      },
    });

    return response.data;
  }

  async deleteComment({ commentId }: DeleteCommentParams) {
    const youtube = await this.getYouTubeClient();
    await youtube.comments.delete({ id: commentId });
    return { deleted: true, commentId };
  }

  async moderateComment({
    commentId,
    moderationStatus,
    banAuthor = false,
  }: ModerateCommentParams) {
    const youtube = await this.getYouTubeClient();

    await youtube.comments.setModerationStatus({
      id: [commentId],
      moderationStatus,
      banAuthor,
    });

    return { commentId, moderationStatus, banAuthor };
  }
}

"""Channel memory — read/write operations for persistent video history."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import desc, select

from yt_agent.memory.models import TagPerformance, Video, WorkflowRun

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class ChannelMemory:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_last_video(self) -> Video | None:
        result = await self._session.execute(
            select(Video).order_by(desc(Video.published_at)).limit(1)
        )
        return result.scalar_one_or_none()

    async def get_last_n_videos(self, n: int) -> list[Video]:
        result = await self._session.execute(
            select(Video).order_by(desc(Video.published_at)).limit(n)
        )
        return list(result.scalars().all())

    async def get_all_videos(self) -> list[Video]:
        result = await self._session.execute(
            select(Video).order_by(desc(Video.published_at))
        )
        return list(result.scalars().all())

    async def get_video(self, video_id: str) -> Video | None:
        return await self._session.get(Video, video_id)

    async def save_video(self, video: Video) -> None:
        self._session.add(video)
        await self._session.commit()

    async def update_video(self, video_id: str, **kwargs: object) -> None:
        video = await self._session.get(Video, video_id)
        if video is None:
            msg = f"Video {video_id!r} not found"
            raise ValueError(msg)
        for key, value in kwargs.items():
            setattr(video, key, value)
        await self._session.commit()

    async def save_tags(self, tags: list[TagPerformance]) -> None:
        self._session.add_all(tags)
        await self._session.commit()

    async def get_tags_by_performance(self) -> list[TagPerformance]:
        result = await self._session.execute(
            select(TagPerformance).order_by(desc(TagPerformance.video_views_7d))
        )
        return list(result.scalars().all())

    async def save_workflow_run(self, run: WorkflowRun) -> None:
        self._session.add(run)
        await self._session.commit()

    async def get_workflow_run(self, run_id: str) -> WorkflowRun | None:
        return await self._session.get(WorkflowRun, run_id)

    async def update_workflow_run(self, run_id: str, **kwargs: object) -> None:
        run = await self._session.get(WorkflowRun, run_id)
        if run is None:
            msg = f"WorkflowRun {run_id!r} not found"
            raise ValueError(msg)
        for key, value in kwargs.items():
            setattr(run, key, value)
        await self._session.commit()

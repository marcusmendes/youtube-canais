"""SQLAlchemy ORM models — channel memory & workflow tracking."""

import datetime

from sqlalchemy import ForeignKey, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Video(Base):
    __tablename__ = "videos"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    title: Mapped[str] = mapped_column(Text)
    sub_niche: Mapped[str] = mapped_column(Text)
    published_at: Mapped[datetime.date]
    format: Mapped[str] = mapped_column(Text, default="long")
    thumbnail_aesthetic: Mapped[str | None] = mapped_column(Text, default=None)
    thumbnail_composition: Mapped[str | None] = mapped_column(Text, default=None)
    thumbnail_palette: Mapped[str | None] = mapped_column(Text, default=None)
    thumbnail_expression: Mapped[str | None] = mapped_column(Text, default=None)
    views_7d: Mapped[int | None] = mapped_column(default=None)
    avg_retention_pct: Mapped[float | None] = mapped_column(default=None)
    like_ratio_pct: Mapped[float | None] = mapped_column(default=None)

    tags: Mapped[list["TagPerformance"]] = relationship(back_populates="video")


class TagPerformance(Base):
    __tablename__ = "tags_performance"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tag: Mapped[str] = mapped_column(Text, index=True)
    video_id: Mapped[str] = mapped_column(ForeignKey("videos.id"))
    volume_at_use: Mapped[int] = mapped_column(default=0)
    video_views_7d: Mapped[int | None] = mapped_column(default=None)

    video: Mapped["Video"] = relationship(back_populates="tags")


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    started_at: Mapped[datetime.datetime] = mapped_column(insert_default=func.now())
    status: Mapped[str] = mapped_column(Text, default="created")
    current_node: Mapped[str | None] = mapped_column(Text, default=None)
    state_json: Mapped[str | None] = mapped_column(Text, default=None)
    topic: Mapped[str | None] = mapped_column(Text, default=None)
    sub_niche: Mapped[str | None] = mapped_column(Text, default=None)
    format: Mapped[str | None] = mapped_column(Text, default=None)
    editorial_angle: Mapped[str | None] = mapped_column(Text, default=None)
    dominant_emotion: Mapped[str | None] = mapped_column(Text, default=None)
    technical_detail: Mapped[str | None] = mapped_column(Text, default=None)
    reference_period: Mapped[str | None] = mapped_column(Text, default=None)

import uuid

from sqlalchemy import (
    UUID,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import declarative_base, relationship

from api_server.services.time import utc_datetime

Base = declarative_base()


class Batch(Base):
    __tablename__ = "batches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    status = Column(String, nullable=False)
    total_in_tokens = Column(Integer, nullable=True)
    total_out_tokens = Column(Integer, nullable=True)
    tokens_per_second = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_datetime)
    finished_at = Column(DateTime(timezone=True), nullable=True)


class BatchPrompt(Base):
    __tablename__ = "batch_prompts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    batch_id = Column(ForeignKey("batches.id"), nullable=False, index=True)
    prompt = Column(String, nullable=False)
    in_tokens_cnt = Column(Integer, nullable=False)
    answer = Column(Text, nullable=True)
    out_tokens_cnt = Column(Integer, nullable=True)
    finish_reason = Column(String, nullable=True)

    batch = relationship("Batch")

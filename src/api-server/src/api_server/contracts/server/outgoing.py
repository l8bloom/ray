import datetime
import uuid

from pydantic import BaseModel

from api_server.contracts.services.incoming import BatchJobStatus


class BatchData(BaseModel):
    prompt: str
    in_tokens_cnt: int
    answer: str | None
    out_tokens_cnt: int | None
    finish_reason: str | None


class BatchStatus(BaseModel):
    id: uuid.UUID
    status: BatchJobStatus
    created_at: datetime.datetime
    finished_at: datetime.datetime | None
    total_in_tokens: int | None
    total_out_tokens: int | None
    tokens_per_second: float | None
    data: list[BatchData]

import uuid
from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, Field

from api_server.contracts.server.incoming import Batch
from api_server.database.db import get_db
from api_server.database.orm_models import Batch as BatchORM
from api_server.services.env import get_env


class BatchJobStatus(StrEnum):
    PENDING = "PENDING"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    COMPLETE = "COMPLETED"


class _Batch(BaseModel):
    id: Annotated[uuid.UUID, Field(default_factory=uuid.uuid4)]
    status: BatchJobStatus


class InferenceRepo:
    """Convenient inference service layer"""

    def __init__(self):
        self.db = get_db(get_env())

    def create_inference_batch(self, batch: Batch):
        b = _Batch(status=BatchJobStatus.PENDING)

        with self.db.session_factory() as session:
            session.add(BatchORM(**b.model_dump()))
            session.commit()

        return b.id


def get_inference_service() -> InferenceRepo:
    return InferenceRepo()

import uuid
from typing import Annotated

from pydantic import BaseModel, Field

from api_server.contracts.server.incoming import Batch
from api_server.contracts.server.outgoing import BatchData, BatchStatus
from api_server.database.db import get_db
from api_server.database.orm_models import Batch as BatchORM
from api_server.database.orm_models import BatchPrompt as BatchPromptORM
from api_server.exceptions import BatchNotFound
from api_server.services.env import get_env

from .incoming import BatchJobStatus


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

    def get_batch_results(self, batch_id: uuid.UUID) -> BatchStatus:
        """Returns info on a batch."""
        with self.db.session_factory() as session:
            batch = session.query(BatchORM).filter(BatchORM.id == batch_id).first()

            if not batch:
                raise BatchNotFound(f"Job {str(batch_id)!r} does not exist.")

            prompts_data = []
            if batch.status == BatchJobStatus.COMPLETE:
                prompts = (
                    session.query(BatchPromptORM)
                    .filter(BatchPromptORM.batch_id == batch_id)
                    .all()
                )
                prompts_data = [
                    BatchData.model_validate(p, from_attributes=True) for p in prompts
                ]

            return BatchStatus(
                id=batch.id,
                status=batch.status,
                created_at=batch.created_at,
                finished_at=batch.finished_at,
                total_in_tokens=batch.total_in_tokens,
                total_out_tokens=batch.total_out_tokens,
                tokens_per_second=batch.tokens_per_second,
                data=prompts_data,
            )


def get_inference_service() -> InferenceRepo:
    return InferenceRepo()

from enum import StrEnum


class BatchJobStatus(StrEnum):
    PENDING = "PENDING"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    COMPLETE = "COMPLETED"

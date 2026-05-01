from typing import Annotated

from pydantic import BaseModel, Field


# TODO: think about limits
class BatchPrompt(BaseModel):
    """Represents a prompt in a batch."""

    prompt: Annotated[
        str,
        Field(
            min_length=1,
            max_length=1_000_000,
            description="AI Prompt",
        ),
    ]


class Batch(BaseModel):
    """Represents incoming batch to process."""

    model: Annotated[str, Field(description="Qwen5B model")]
    input: Annotated[
        list[BatchPrompt],
        Field(min_length=1, description="List of prompts for AI."),
    ]
    max_tokens: Annotated[
        int,
        Field(
            gt=0,
            lt=1_000_000,
            description="How many output tokens can be generated for each prompt.",
        ),
    ]

from typing import Annotated

from pydantic import BaseModel, Field

chatML = """
<|im_start|>system
You are a helpful assistant.<|im_end|>
<|im_start|>user
{}<|im_end|>
<|im_start|>assistant
"""


# TODO: think about limits
class BatchPrompt(BaseModel):
    """Represents a prompt in a batch."""

    prompt: Annotated[
        str,
        Field(
            min_length=1,
            max_length=1_000_000,
            description="AI Prompt",
            examples=["What is 2+2?", "Hello world"],
        ),
    ]


class Batch(BaseModel):
    """Represents incoming batch to process."""

    model: Annotated[
        str,
        Field(
            description="Qwen5B model",
            examples=["Qwen/Qwen2.5-0.5B-Instruct"],
        ),
    ]
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
            examples=[50],
        ),
    ]

    @property
    def prompts(self):
        """Extracts prompts and adjust for Qwen chat template style."""
        return [chatML.format(p.prompt) for p in self.input]

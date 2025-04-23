from pydantic import BaseModel, Field


class LLMWordDefinition(BaseModel):
    word: str = Field(max_length=128, description="Definition of a word")

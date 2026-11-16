from pydantic import BaseModel, ConfigDict, Field


class DocumentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=200)


class DocumentOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    title: str = Field(min_length=1, max_length=200)

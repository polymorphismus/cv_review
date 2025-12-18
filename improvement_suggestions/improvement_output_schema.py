from pydantic import BaseModel, Field
from typing import List, Optional

class UpdatedCvResult(BaseModel):
    updated_cv_text: str = Field(description="Full rewritten CV in clean Markdown format, optimized for ATS parsing and human review")

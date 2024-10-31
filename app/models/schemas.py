from pydantic import BaseModel
from typing import Any, List, Optional

class ProcessRequestBody(BaseModel):
    industry: str
    course_topic_area: Optional[str] = None

class ProcessResponse(BaseModel):
    status: str
    message: str
    data: Any

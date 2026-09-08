from pydantic import BaseModel, ConfigDict
from typing import Optional, Any

class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str

class GenericResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    model_config = ConfigDict(from_attributes=True)

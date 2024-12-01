from typing import Dict, Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    """Custom type for MongoDB ObjectId to work with Pydantic"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, field=None):
        if not ObjectId.is_valid(v):
            raise ValueError('Invalid ObjectId')
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema: Any, handler):
        """Modify JSON schema for Pydantic v2"""
        return {'type': 'string'}

class IAModel(BaseModel):
    """Pydantic model for IB Internal Assessment (IA) or Extended Essay (EE)"""
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "title": "Math AI SL Internal Assessment Sample",
                "subject": "Math AI SL",
                "description": "Sample IA exploring mathematical modeling",
                "word_count": 2500,
                "read_time": "12 mins read"
            }
        },
        arbitrary_types_allowed=True
    )

    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    title: str = Field(..., description="Title of the IA/EE")
    subject: str = Field(..., description="IB Subject (e.g., Math AI SL)")
    description: Optional[str] = Field(None, description="Brief description or overview")
    sections: Dict[str, str] = Field(default_factory=dict, description="Extracted sections with content")
    word_count: int = Field(0, description="Total word count of the document")
    read_time: Optional[str] = Field(None, description="Estimated reading time")
    file_link: Optional[str] = Field(None, description="Link to downloadable resource")
    publication_date: datetime = Field(default_factory=datetime.now, description="Date of publication/scraping")
    source_url: Optional[str] = Field(None, description="Original source URL")

def convert_model_to_dict(model: IAModel) -> dict:
    """Convert Pydantic model to dictionary for MongoDB insertion"""
    return {k: v for k, v in model.model_dump(by_alias=True).items() if v is not None}
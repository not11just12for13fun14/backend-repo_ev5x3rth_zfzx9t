"""
Database Schemas for SamacharAI

Each Pydantic model maps to a MongoDB collection with the lowercase class name.
"""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field

Tone = Literal["formal", "neutral", "emotional", "journalistic"]
Audience = Literal["general", "youth", "rural", "urban", "business"]
Language = Literal[
    "English", "Hindi", "Bengali", "Tamil", "Marathi"
]

class ArticleInput(BaseModel):
    title: str = Field(..., description="Primary headline or topic")
    bullets: List[str] = Field(default_factory=list, description="Key points to cover")
    tone: Tone = Field("journalistic")
    audience: Audience = Field("general")
    language: Language = Field("English")
    source: Optional[str] = Field(default=None, description="Optional source or attribution")

class Article(BaseModel):
    title: str
    content: str
    language: Language
    tone: Tone
    audience: Audience
    headlines: List[str] = Field(default_factory=list)
    subheads: List[str] = Field(default_factory=list)

class LayoutBlock(BaseModel):
    type: Literal["headline", "subhead", "image", "body", "ad"] = Field("body")
    x: int = Field(0, ge=0)
    y: int = Field(0, ge=0)
    w: int = Field(12, ge=1, le=12)
    h: int = Field(2, ge=1)

class LayoutTemplate(BaseModel):
    name: str
    description: Optional[str] = None
    page_size: Literal["A4", "Letter", "A3"] = "A4"
    columns: int = Field(3, ge=1, le=6)
    margin_mm: int = Field(12, ge=5, le=30)
    blocks: List[LayoutBlock] = Field(default_factory=list)

class EpaperExport(BaseModel):
    article_ids: List[str] = Field(default_factory=list)
    layout_template_id: Optional[str] = None

# Note: The built-in database helper expects these models to be used for validation

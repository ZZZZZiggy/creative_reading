from typing import List, Optional, Dict, Tuple
from pydantic import BaseModel, Field


class DocumentMeta(BaseModel):
    """document metadata"""
    difficulty: Optional[str] = None
    domain: Optional[str] = None
    language: Optional[str] = "en-US"


class BilingualAnchor(BaseModel):
    """bilingual anchor - for intensive reading mode"""
    term: str = Field(..., description="term")
    range: Tuple[int, int] = Field(..., description="the range of the term in the text [start, end]")
    translation: str = Field(..., description="translation")
    nuance_note: Optional[str] = Field(None, description="nuance note")
    trigger_threshold_ms: Optional[int] = Field(None, description="the required gaze duration to trigger this anchor (milliseconds)")


class BlockAnnotations(BaseModel):
    """block annotations - contains all metadata required for UI rendering"""
    # [Skim Mode] Core: the range of the topic sentence
    topic_sentence_range: Optional[Tuple[int, int]] = Field(None, description="the range of the topic sentence [start, end]")

    # [Skim Mode] Advanced: syntax structure highlighting (S-V-O)
    svo_structure: Optional[Dict[str, Tuple[int, int]]] = Field(
        None,
        description="syntax structure, key is 'subject', 'verb', 'object', value is the range of the corresponding position"
    )

    # [Intensive Mode] bilingual anchors and terminology explanation
    bilingual_anchors: Optional[List[BilingualAnchor]] = Field(None, description="bilingual anchor list")


class Block(BaseModel):
    """document block"""
    id: str = Field(..., description="block ID")
    type: str = Field(..., description="block type, e.g. 'paragraph', 'heading', 'table'")
    content: str = Field(..., description="block content")
    annotations: Optional[BlockAnnotations] = Field(None, description="block annotations")


class DocumentResponse(BaseModel):
    """document response model"""
    doc_id: str = Field(..., description="document ID")
    title: str = Field(..., description="document title")
    meta: Optional[DocumentMeta] = Field(None, description="document metadata")
    blocks: List[Block] = Field(default_factory=list, description="document block list")

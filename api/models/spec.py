from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class Behavior(BaseModel):
    validation: List[str] = []
    actions: List[str] = []
    api_calls: List[str] = []
    responses: Dict[str, str] = {}

class ArchitectSpec(BaseModel):
    goal: str = ""
    type_hypothesis: List[str] = []
    inputs: List[str] = []
    outputs: List[str] = []
    ui: List[str] = []
    state: List[str] = []
    behavior: Behavior = Field(default_factory=Behavior)

class MapRequest(BaseModel):
    user_text: str
    current_field: str
    current_spec: ArchitectSpec

class MapResponse(BaseModel):
    updated_spec: ArchitectSpec
    next_field: str
    next_question: str
    suggestions: List[str]
    is_complete: bool

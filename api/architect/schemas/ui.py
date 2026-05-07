from pydantic import BaseModel, Field
from typing import List
from .base import Node, NodeType

class ScreenData(BaseModel):
    name: str = ""
    # UNIFIED: components are now children of the Screen Node

class UISystem(BaseModel):
    screens: List[Node[ScreenData]] = Field(default_factory=list)
    layout_mode: str = "responsive"

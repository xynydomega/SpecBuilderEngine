import sys
import os
from architect.compiler.manager import SchemaManager

class SchemaEngine:
    def __init__(self):
        self.manager = SchemaManager()

    def get_schema(self):
        return self.manager.export_schema()

    def reset_schema(self):
        self.manager = SchemaManager()
        return self.get_schema()

    def apply_patch(self, patch, mark_confirmed=False):
        """Merges a patch into the Pydantic-based schema manager."""
        self.manager.apply_patch(patch)
        if mark_confirmed:
            # Metadata updates are handled inside manager.py, 
            # but we could add a confirmation flag if needed.
            pass
        return self.get_schema()

    def get_current_stage(self):
        return self.manager.get_current_stage()

schema_engine = SchemaEngine()

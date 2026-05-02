from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sys

# Add the current directory to sys.path to ensure imports work on Vercel
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from models.spec import MapRequest, MapResponse, ArchitectSpec
    from services.sequencer import get_next_field, get_question, get_suggestions
    from services.mapper import map_intent
except ImportError:
    from .models.spec import MapRequest, MapResponse, ArchitectSpec
    from .services.sequencer import get_next_field, get_question, get_suggestions
    from .services.mapper import map_intent

app = FastAPI(title="SpecBuilderEngine Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/map", response_model=MapResponse)
async def map_endpoint(request: MapRequest):
    # 1. Map user intent to current field
    patch = map_intent(
        request.user_text, 
        request.current_field, 
        request.current_spec.goal
    )
    
    # 2. Update Spec
    updated_spec = request.current_spec.model_copy(deep=True)
    field = request.current_field
    
    if field == 'goal':
        updated_spec.goal = str(patch) if isinstance(patch, str) else patch.get('goal', str(patch))
    elif field in ['actions', 'validation', 'api']:
        key = 'api_calls' if field == 'api' else field
        setattr(updated_spec.behavior, key, patch)
    elif field == 'responses':
        updated_spec.behavior.responses = patch
    elif field == 'type':
        updated_spec.type_hypothesis = patch
    else:
        setattr(updated_spec, field, patch)
    
    # 3. Determine next state
    next_field = get_next_field(updated_spec)
    
    if next_field:
        return MapResponse(
            updated_spec=updated_spec,
            next_field=next_field,
            next_question=get_question(next_field, updated_spec.goal),
            suggestions=get_suggestions(next_field),
            is_complete=False
        )
    else:
        return MapResponse(
            updated_spec=updated_spec,
            next_field="complete",
            next_question="Specification complete!",
            suggestions=[],
            is_complete=True
        )

@app.get("/api/health")
async def health():
    return {"status": "alive"}

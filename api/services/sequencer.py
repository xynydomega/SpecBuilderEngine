from typing import Optional
try:
    from models.spec import ArchitectSpec
except ImportError:
    try:
        from ..models.spec import ArchitectSpec
    except ImportError:
        from api.models.spec import ArchitectSpec

PRIORITY_ORDER = [
    'goal',
    'type',
    'inputs',
    'ui',
    'actions',
    'state',
    'validation',
    'api',
    'responses',
    'outputs'
]

def get_next_field(spec: ArchitectSpec) -> Optional[str]:
    if not spec.goal: return 'goal'
    if not spec.type_hypothesis: return 'type'
    if not spec.inputs: return 'inputs'
    if not spec.ui: return 'ui'
    if not spec.behavior.actions: return 'actions'
    if not spec.state: return 'state'
    if not spec.behavior.validation: return 'validation'
    if not spec.behavior.api_calls: return 'api'
    if not spec.behavior.responses: return 'responses'
    if not spec.outputs: return 'outputs'
    return None

def get_question(field: str, goal: str) -> str:
    goal_label = goal if goal else "your project"
    questions = {
        'goal': "What are you trying to build today?",
        'type': f"Is '{goal_label}' a screen, a feature, or a full system?",
        'inputs': f"For {goal_label}, what data does the user provide?",
        'ui': f"How should the user interact with {goal_label}?",
        'actions': "What should happen step-by-step when they interact?",
        'state': "What are the key states (e.g., loading, success)?",
        'validation': "What checks should be performed on the inputs?",
        'api': "Does this need to talk to any external services?",
        'responses': "How should the system respond to success or failure?",
        'outputs': "What is the final result or data produced?"
    }
    return questions.get(field, "What's next?")

def get_suggestions(field: str) -> list[str]:
    suggestions = {
        'type': ['Screen', 'Feature', 'System', 'API'],
        'inputs': ['Email', 'Password', 'Username', 'Title'],
        'ui': ['Form', 'Button', 'Modal', 'List'],
        'state': ['Idle', 'Loading', 'Success', 'Error'],
        'actions': ['Validate', 'Save', 'Redirect', 'Notify']
    }
    return suggestions.get(field, [])

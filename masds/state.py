# -----------------------------
# File: devagents/state.py
# -----------------------------
from typing import TypedDict, List, Dict


class AnalyzerState(TypedDict):
    reasoning: str
    messages: List[Dict[str, str]]
    prd: str
    is_clear: bool = False


class ImplementerState(TypedDict):
    reasoning: str
    implementation: str


class PlannerState(TypedDict):
    reasoning: str
    tasks: List[Dict[str, str | int]]


class ProjectState(TypedDict):
    description: str
    analyzer: AnalyzerState
    planner: PlannerState
    implementer: ImplementerState

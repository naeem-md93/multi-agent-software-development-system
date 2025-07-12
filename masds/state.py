from typing_extensions import TypedDict

from .agents import (
    AnalyzerState,
    PlannerState,
    ImplementerState
)


class ProjectState(TypedDict):
    description: str
    analyzer: AnalyzerState
    planner: PlannerState
    implementer: ImplementerState

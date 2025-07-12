from langgraph.graph import StateGraph, END, START

from .state import ProjectState
from .agents import (
    analysis_agent,
    implementation_agent,
    planning_agent
)


def build_graph():

    graph = StateGraph(ProjectState)

    graph.add_node("analyzer", analysis_agent)
    graph.add_node("planner", planning_agent)
    graph.add_node("implementer", implementation_agent)

    graph.add_edge(START, "analyzer")
    graph.add_edge("analyzer", "planner")
    graph.add_edge("planner", "implementer")
    graph.add_edge("implementer", END)

    return graph.compile()



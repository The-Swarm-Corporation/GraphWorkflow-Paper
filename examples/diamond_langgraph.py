"""
Diamond workflow in LangGraph.

Listing (b) of Figure 2 in the paper:
"GraphWorkflow: A Low-Overhead Compile-Once Graph Execution Engine for
 Multi-Agent Systems" (Gomez, 2026).

The same diamond workflow (analyst -> {writer, researcher} -> editor)
expressed in LangGraph 1.0.4. LangGraph routes all inter-node communication
through typed channel state, so the user must:

  * design a State schema,
  * choose a reducer for every key that concurrent branches write
    (omitting it raises a concurrent-update error on the diamond's fan-in),
  * wrap each agent as a state function,
  * declare explicit START/END edges,
  * call compile() explicitly, and
  * raise recursion_limit for any graph deeper than the default 25
    supersteps (the benchmark chains require it at N >= 50).
"""

import operator
from typing import Annotated, TypedDict

from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    # fan-in needs a reducer to merge concurrent writes
    results: Annotated[list, operator.add]


def as_node(agent):
    # wrap each agent as a state function
    def node(state: State):
        out = agent.run(str(state["results"]))
        return {"results": [out]}

    return node


builder = StateGraph(State)
for name, ag in [
    ("analyst", analyst),
    ("writer", writer),
    ("researcher", researcher),
    ("editor", editor),
]:
    builder.add_node(name, as_node(ag))

builder.add_edge(START, "analyst")
builder.add_edge("analyst", "writer")
builder.add_edge("analyst", "researcher")
builder.add_edge("writer", "editor")
builder.add_edge("researcher", "editor")
builder.add_edge("editor", END)

graph = builder.compile()

task = "Produce a market report."
out = graph.invoke(
    {"results": [task]},
    {"recursion_limit": 100},
)
# outputs interleaved in one shared list

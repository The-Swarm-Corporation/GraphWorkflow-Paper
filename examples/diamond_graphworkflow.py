"""
Diamond workflow in GraphWorkflow.

Listing (a) of Figure 2 in the paper:
"GraphWorkflow: A Low-Overhead Compile-Once Graph Execution Engine for
 Multi-Agent Systems" (Gomez, 2026).

A single analyst fans out to a writer and a researcher whose outputs an
editor merges. GraphWorkflow treats agents as nodes and infers everything
else (entry/exit points, compilation, deep-graph recursion) from the
graph structure.
"""

from swarms import Agent, GraphWorkflow

analyst = Agent(
    agent_name="Analyst",
    model_name="gpt-5.4",
)
writer = Agent(
    agent_name="Writer",
    model_name="gpt-5.4",
)
researcher = Agent(
    agent_name="Researcher",
    model_name="gpt-5.4",
)
editor = Agent(
    agent_name="Editor",
    model_name="gpt-5.4",
)

wf = GraphWorkflow()
for a in (analyst, writer, researcher, editor):
    wf.add_node(a)

wf.add_edge(analyst, writer)
wf.add_edge(analyst, researcher)
wf.add_edge(writer, editor)
wf.add_edge(researcher, editor)

task = "Produce a market report."
results = wf.run(task)
# {"Analyst": ..., "Writer": ..., "Researcher": ..., "Editor": ...}

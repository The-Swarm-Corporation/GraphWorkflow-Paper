"""
Full-agent-execution benchmark: GraphWorkflow vs LangGraph, one page.

Unlike ``graph_workflow_bench.py`` (no-op nodes, orchestration overhead only),
this harness executes real LLM agents on both frameworks with the identical
model (``gpt-5.4``), prompts, and topology, so the reported numbers are
end-to-end wall-clock latency. Requires OPENAI_API_KEY. Real calls cost
tokens: sizes and repeats default small.

Usage:
    python benchmarks/agent_execution_bench.py \
        --topologies diamond,chain --sizes 4,8 --repeats 3
"""

import argparse
import json
import statistics
import time

MODEL = "gpt-5.4"
TASK = "In one sentence, state one interesting fact about graph theory."
SYSTEM = "You are a benchmark agent. Reply in at most one short sentence."


# --- topologies (same families as the paper) --------------------------------
def chain(n):
    return [(f"n{i}", f"n{i + 1}") for i in range(n - 1)]


def wide(n):
    return [("n0", f"n{i}") for i in range(1, n)]


def diamond(n):
    if n < 3:
        return chain(n)
    mid = [f"n{i}" for i in range(1, n - 1)]
    return [("n0", m) for m in mid] + [(m, f"n{n - 1}") for m in mid]


def layered(n, w=4):
    layers = [[f"n{i}" for i in range(s, min(s + w, n))] for s in range(0, n, w)]
    return [(a, b) for x, y in zip(layers, layers[1:]) for a in x for b in y]


def tree(n):
    return [
        (f"n{i}", f"n{c}") for i in range(n) for c in (2 * i + 1, 2 * i + 2) if c < n
    ]


TOPOLOGIES = {
    "chain": chain,
    "wide": wide,
    "diamond": diamond,
    "layered": layered,
    "tree": tree,
}


def make_agents(n, model):
    """Identical real agents for both frameworks: same model, prompt, budget."""
    from swarms import Agent

    return [
        Agent(
            agent_name=f"n{i}",
            model_name=model,
            system_prompt=SYSTEM,
            max_loops=1,
            max_tokens=64,
            temperature=0,
        )
        for i in range(n)
    ]


# --- GraphWorkflow ----------------------------------------------------------
def gw_build(n, edges, model, backend):
    from swarms import GraphWorkflow

    wf = GraphWorkflow(auto_compile=True, backend=backend)
    for a in make_agents(n, model):
        wf.add_node(a)
    for src, dst in edges:
        wf.add_edge(src, dst)
    return wf


def gw_run(wf):
    wf.run(TASK)


# --- LangGraph --------------------------------------------------------------
def lg_build(n, edges, model):
    import operator
    from typing import Annotated, List

    from langgraph.graph import END, START, StateGraph
    from typing_extensions import TypedDict

    class State(TypedDict):
        out: Annotated[List[str], operator.add]  # fan-in needs a reducer

    def as_node(agent):
        def node(state):
            return {"out": [agent.run("\n".join(state["out"]))]}

        return node

    g = StateGraph(State)
    for a in make_agents(n, model):
        g.add_node(a.agent_name, as_node(a))
    targets = {d for _, d in edges}
    sources = {s for s, _ in edges}
    for i in range(n):
        name = f"n{i}"
        if name not in targets:
            g.add_edge(START, name)
        if name not in sources:
            g.add_edge(name, END)
    for src, dst in edges:
        g.add_edge(src, dst)
    return g.compile()


def lg_run(app):
    app.invoke({"out": [TASK]}, config={"recursion_limit": 100_000})


# --- timing -----------------------------------------------------------------
def bench(fn, repeats, warmup=1):
    for _ in range(warmup):
        fn()
    samples = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        fn()
        samples.append((time.perf_counter() - t0) * 1000.0)
    return {
        "median_ms": statistics.median(samples),
        "mean_ms": statistics.fmean(samples),
        "samples_ms": samples,
    }


def plot(results, prefix):
    """Write grouped-bar latency and speedup charts next to the JSON."""
    import matplotlib.pyplot as plt

    # Same entity->color assignment as plot_results.py (validated palette):
    # GraphWorkflow blue, LangGraph green. Order is fixed, never cycled.
    GW, LG = "#2a78d6", "#1baf7a"
    plt.rcParams.update(
        {
            "figure.facecolor": "#fcfcfb",
            "axes.facecolor": "#fcfcfb",
            "savefig.facecolor": "#fcfcfb",
            "text.color": "#0b0b0b",
            "axes.labelcolor": "#52514e",
            "axes.edgecolor": "#c3c2b7",
            "xtick.color": "#898781",
            "ytick.color": "#898781",
            "grid.color": "#e1e0d9",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "font.size": 10,
        }
    )
    runs = results["runs"]
    labels = [f"{r['topology']}\nn={r['n']}" for r in runs]
    xs = range(len(runs))

    fig, ax = plt.subplots(figsize=(max(6, 1.4 * len(runs)), 4))
    for off, key, color, name in (
        (-0.2, "graphworkflow", GW, "GraphWorkflow"),
        (0.2, "langgraph", LG, "LangGraph"),
    ):
        vals = [r[key]["median_ms"] for r in runs]
        bars = ax.bar([x + off for x in xs], vals, 0.38, color=color, label=name)
        ax.bar_label(bars, fmt="%.0f", padding=2, fontsize=8)
    ax.set_xticks(list(xs), labels)
    ax.set_ylabel("median end-to-end latency (ms)")
    ax.set_title(
        f"Full agent execution ({results['config']['model']}): "
        "GraphWorkflow vs LangGraph"
    )
    ax.grid(axis="y", linewidth=0.5)
    ax.set_axisbelow(True)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(f"{prefix}_latency.png", dpi=200)

    fig, ax = plt.subplots(figsize=(max(6, 1.2 * len(runs)), 3.5))
    bars = ax.bar(xs, [r["speedup"] for r in runs], 0.5, color=GW)
    ax.bar_label(bars, fmt="%.2fx", padding=2, fontsize=8)
    ax.axhline(1.0, color="#898781", linewidth=1, linestyle="--")
    ax.set_xticks(list(xs), labels)
    ax.set_ylabel("LangGraph / GraphWorkflow")
    ax.set_title("End-to-end speedup (>1 favors GraphWorkflow)")
    ax.grid(axis="y", linewidth=0.5)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(f"{prefix}_speedup.png", dpi=200)
    print(f"wrote {prefix}_latency.png and {prefix}_speedup.png")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--backend", default="networkx")
    ap.add_argument("--sizes", default="4,8")
    ap.add_argument("--topologies", default=",".join(TOPOLOGIES))
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--warmup", type=int, default=1)
    ap.add_argument("--out", default="benchmarks/results/agent_execution.json")
    args = ap.parse_args()

    results = {"config": vars(args), "runs": []}
    print(f"model={args.model}  repeats={args.repeats}  warmup={args.warmup}\n")
    print("| topology | n | GraphWorkflow ms | LangGraph ms | speedup |")
    print("|---|---|---|---|---|")

    for topo in args.topologies.split(","):
        edges_of = TOPOLOGIES[topo.strip()]
        for n in (int(s) for s in args.sizes.split(",")):
            edges = edges_of(n)
            # fresh graphs per sample: swarms agents accumulate conversation
            # history, which would grow prompts across repeats
            gw = bench(
                lambda: gw_run(gw_build(n, edges, args.model, args.backend)),
                args.repeats,
                args.warmup,
            )
            lg = bench(
                lambda: lg_run(lg_build(n, edges, args.model)),
                args.repeats,
                args.warmup,
            )
            speedup = lg["median_ms"] / gw["median_ms"]
            print(
                f"| {topo} | {n} | {gw['median_ms']:.0f} "
                f"| {lg['median_ms']:.0f} | {speedup:.2f}x |"
            )
            results["runs"].append(
                {
                    "topology": topo,
                    "n": n,
                    "graphworkflow": gw,
                    "langgraph": lg,
                    "speedup": speedup,
                }
            )

    with open(args.out, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nwrote {args.out}")
    plot(results, args.out.rsplit(".", 1)[0])


if __name__ == "__main__":
    main()

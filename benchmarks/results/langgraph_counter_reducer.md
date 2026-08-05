# GraphWorkflow benchmark — swarms vs LangGraph

*2026-08-05T09:33:55 · macOS-15.7.7-arm64-arm-64bit · 12 cores · Python 3.12.3 · swarms @ daa3368f*

Versions: swarms 14.0.0, langgraph 1.0.4, networkx 3.5, rustworkx 0.17.1

Timing: median of 9 samples after 2 warmup iterations, GC disabled inside each timed region. LangGraph reducer: `counter`.

All nodes are no-ops — every number is orchestration overhead, not LLM latency.

## Topology: chain

| nodes | phase | langgraph |
| ---: | --- | ---: |
| 10 | build | 0.272 |
| 10 | compile | 0.656 |
| 10 | first_run | 1.910 |
| 10 | steady_run | 0.775 |
| 50 | build | 0.661 |
| 50 | compile | 2.734 |
| 50 | first_run | 7.402 |
| 50 | steady_run | 3.378 |
| 200 | build | 1.887 |
| 200 | compile | 9.918 |
| 200 | first_run | 33.515 |
| 200 | steady_run | 16.804 |

## Topology: wide

| nodes | phase | langgraph |
| ---: | --- | ---: |
| 10 | build | 0.248 |
| 10 | compile | 0.622 |
| 10 | first_run | 2.204 |
| 10 | steady_run | 1.134 |
| 50 | build | 0.644 |
| 50 | compile | 2.648 |
| 50 | first_run | 11.663 |
| 50 | steady_run | 4.313 |
| 200 | build | 1.987 |
| 200 | compile | 10.836 |
| 200 | first_run | 37.106 |
| 200 | steady_run | 23.475 |

## Topology: diamond

| nodes | phase | langgraph |
| ---: | --- | ---: |
| 10 | build | 0.314 |
| 10 | compile | 0.760 |
| 10 | first_run | 2.275 |
| 10 | steady_run | 1.187 |
| 50 | build | 0.646 |
| 50 | compile | 2.920 |
| 50 | first_run | 8.738 |
| 50 | steady_run | 4.270 |
| 200 | build | 2.036 |
| 200 | compile | 13.265 |
| 200 | first_run | 41.662 |
| 200 | steady_run | 24.291 |

## Topology: layered

| nodes | phase | langgraph |
| ---: | --- | ---: |
| 10 | build | 0.302 |
| 10 | compile | 0.835 |
| 10 | first_run | 2.891 |
| 10 | steady_run | 1.224 |
| 50 | build | 0.696 |
| 50 | compile | 5.402 |
| 50 | first_run | 11.273 |
| 50 | steady_run | 4.434 |
| 200 | build | 2.042 |
| 200 | compile | 13.751 |
| 200 | first_run | 42.966 |
| 200 | steady_run | 20.944 |

## Topology: tree

| nodes | phase | langgraph |
| ---: | --- | ---: |
| 10 | build | 0.346 |
| 10 | compile | 0.847 |
| 10 | first_run | 2.728 |
| 10 | steady_run | 1.549 |
| 50 | build | 0.682 |
| 50 | compile | 2.773 |
| 50 | first_run | 8.093 |
| 50 | steady_run | 4.452 |
| 200 | build | 2.275 |
| 200 | compile | 10.263 |
| 200 | first_run | 31.138 |
| 200 | steady_run | 16.738 |

# GraphWorkflow benchmark — swarms vs LangGraph

*2026-11-03T13:47:41 · macOS-15.7.7-arm64-arm-64bit · 12 cores · Python 3.12.3 · swarms @ 7033297*

Versions: swarms 17.0.0, langgraph 1.0.4, networkx 3.5, rustworkx 0.17.1

Timing: median of 9 samples after 2 warmup iterations, GC disabled inside each timed region. LangGraph reducer: `list`.

All nodes are no-ops — every number is orchestration overhead, not LLM latency.

## Import (cold interpreter, baseline-subtracted)

| target | median ms |
| --- | ---: |
| `swarms (top-level)` | 232.3 |
| `swarms.GraphWorkflow` | 230.7 |
| `langgraph.StateGraph` | 291.0 |

## Topology: chain

| nodes | phase | swarms-networkx | swarms-rustworkx | langgraph |
| ---: | --- | ---: | ---: | ---: |
| 10 | build | 0.150 | 0.141 | 0.420 |
| 10 | compile | 0.080 | 0.041 | 1.027 |
| 10 | first_run | 0.215 | 0.196 | 2.394 |
| 10 | steady_run | 0.039 | 0.038 | 0.946 |
| 50 | build | 0.281 | 0.228 | 0.710 |
| 50 | compile | 0.148 | 0.103 | 3.310 |
| 50 | first_run | 0.466 | 0.395 | 8.231 |
| 50 | steady_run | 0.098 | 0.091 | 3.337 |
| 200 | build | 0.616 | 0.501 | 2.005 |
| 200 | compile | 0.431 | 0.290 | 12.623 |
| 200 | first_run | 1.293 | 1.277 | 37.189 |
| 200 | steady_run | 0.285 | 0.333 | 17.140 |

## Topology: wide

| nodes | phase | swarms-networkx | swarms-rustworkx | langgraph |
| ---: | --- | ---: | ---: | ---: |
| 10 | build | 0.143 | 0.117 | 0.290 |
| 10 | compile | 0.062 | 0.043 | 0.843 |
| 10 | first_run | 0.594 | 0.545 | 2.453 |
| 10 | steady_run | 0.385 | 0.388 | 1.146 |
| 50 | build | 0.233 | 0.209 | 0.646 |
| 50 | compile | 0.126 | 0.092 | 3.246 |
| 50 | first_run | 1.796 | 1.690 | 8.593 |
| 50 | steady_run | 1.378 | 1.391 | 4.527 |
| 200 | build | 0.687 | 0.527 | 2.072 |
| 200 | compile | 0.361 | 0.184 | 12.455 |
| 200 | first_run | 6.130 | 5.741 | 38.987 |
| 200 | steady_run | 5.114 | 5.119 | 23.574 |

## Topology: diamond

| nodes | phase | swarms-networkx | swarms-rustworkx | langgraph |
| ---: | --- | ---: | ---: | ---: |
| 10 | build | 0.152 | 0.150 | 0.319 |
| 10 | compile | 0.059 | 0.054 | 0.960 |
| 10 | first_run | 0.596 | 0.570 | 2.548 |
| 10 | steady_run | 0.371 | 0.355 | 1.198 |
| 50 | build | 0.295 | 0.242 | 0.701 |
| 50 | compile | 0.138 | 0.086 | 3.776 |
| 50 | first_run | 1.824 | 1.764 | 9.748 |
| 50 | steady_run | 1.389 | 1.380 | 4.641 |
| 200 | build | 0.843 | 0.745 | 2.206 |
| 200 | compile | 0.411 | 0.251 | 15.408 |
| 200 | first_run | 6.527 | 5.911 | 43.573 |
| 200 | steady_run | 4.934 | 4.349 | 24.082 |

## Topology: layered

| nodes | phase | swarms-networkx | swarms-rustworkx | langgraph |
| ---: | --- | ---: | ---: | ---: |
| 10 | build | 0.156 | 0.167 | 0.275 |
| 10 | compile | 0.057 | 0.051 | 0.985 |
| 10 | first_run | 0.617 | 0.624 | 2.946 |
| 10 | steady_run | 0.431 | 0.406 | 1.275 |
| 50 | build | 0.395 | 0.357 | 0.684 |
| 50 | compile | 0.166 | 0.115 | 4.195 |
| 50 | first_run | 1.412 | 1.270 | 11.413 |
| 50 | steady_run | 0.865 | 0.855 | 4.589 |
| 200 | build | 1.255 | 1.183 | 2.141 |
| 200 | compile | 0.502 | 0.287 | 16.100 |
| 200 | first_run | 4.339 | 3.883 | 43.892 |
| 200 | steady_run | 2.750 | 2.530 | 19.057 |

## Topology: tree

| nodes | phase | swarms-networkx | swarms-rustworkx | langgraph |
| ---: | --- | ---: | ---: | ---: |
| 10 | build | 0.148 | 0.131 | 0.306 |
| 10 | compile | 0.070 | 0.047 | 0.893 |
| 10 | first_run | 0.613 | 0.578 | 2.626 |
| 10 | steady_run | 0.420 | 0.399 | 1.239 |
| 50 | build | 0.246 | 0.260 | 0.727 |
| 50 | compile | 0.127 | 0.080 | 3.559 |
| 50 | first_run | 1.781 | 1.661 | 8.869 |
| 50 | steady_run | 1.408 | 1.280 | 4.331 |
| 200 | build | 0.662 | 0.586 | 2.091 |
| 200 | compile | 0.430 | 0.229 | 12.840 |
| 200 | first_run | 5.878 | 5.000 | 34.145 |
| 200 | steady_run | 5.282 | 4.321 | 17.287 |

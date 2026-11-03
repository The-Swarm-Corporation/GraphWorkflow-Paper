# GraphWorkflow benchmark — swarms vs LangGraph

*2026-08-05T09:30:29 · macOS-15.7.7-arm64-arm-64bit · 12 cores · Python 3.12.3 · swarms @ daa3368f*

Versions: swarms 14.0.0, langgraph 1.0.4, networkx 3.5, rustworkx 0.17.1

Timing: median of 9 samples after 2 warmup iterations, GC disabled inside each timed region. LangGraph reducer: `list`.

All nodes are no-ops — every number is orchestration overhead, not LLM latency.

## Import (cold interpreter, baseline-subtracted)

| target | median ms |
| --- | ---: |
| `swarms (top-level)` | 1320.0 |
| `swarms.GraphWorkflow` | 1583.9 |
| `langgraph.StateGraph` | 343.3 |

## Topology: chain

| nodes | phase | swarms-networkx | swarms-rustworkx | langgraph |
| ---: | --- | ---: | ---: | ---: |
| 10 | build | 0.178 | 0.186 | 0.384 |
| 10 | compile | 0.077 | 0.066 | 0.940 |
| 10 | first_run | 0.370 | 0.284 | 2.216 |
| 10 | steady_run | 0.059 | 0.061 | 1.187 |
| 50 | build | 0.290 | 0.250 | 0.716 |
| 50 | compile | 0.156 | 0.115 | 3.517 |
| 50 | first_run | 0.486 | 0.410 | 8.692 |
| 50 | steady_run | 0.119 | 0.111 | 3.459 |
| 200 | build | 0.679 | 0.477 | 2.077 |
| 200 | compile | 0.439 | 0.264 | 12.569 |
| 200 | first_run | 1.227 | 1.063 | 36.010 |
| 200 | steady_run | 0.290 | 0.325 | 18.148 |

## Topology: wide

| nodes | phase | swarms-networkx | swarms-rustworkx | langgraph |
| ---: | --- | ---: | ---: | ---: |
| 10 | build | 0.160 | 0.154 | 0.327 |
| 10 | compile | 0.071 | 0.055 | 0.822 |
| 10 | first_run | 0.659 | 0.607 | 2.641 |
| 10 | steady_run | 0.464 | 0.454 | 1.265 |
| 50 | build | 0.263 | 0.230 | 0.714 |
| 50 | compile | 0.139 | 0.087 | 3.346 |
| 50 | first_run | 1.411 | 1.341 | 8.694 |
| 50 | steady_run | 1.048 | 1.036 | 4.315 |
| 200 | build | 0.595 | 0.510 | 2.189 |
| 200 | compile | 0.351 | 0.220 | 12.512 |
| 200 | first_run | 2.995 | 2.680 | 40.900 |
| 200 | steady_run | 2.096 | 1.947 | 24.508 |

## Topology: diamond

| nodes | phase | swarms-networkx | swarms-rustworkx | langgraph |
| ---: | --- | ---: | ---: | ---: |
| 10 | build | 0.186 | 0.198 | 0.370 |
| 10 | compile | 0.073 | 0.063 | 0.940 |
| 10 | first_run | 0.718 | 0.602 | 2.613 |
| 10 | steady_run | 0.460 | 0.412 | 1.308 |
| 50 | build | 0.304 | 0.279 | 0.783 |
| 50 | compile | 0.150 | 0.101 | 3.824 |
| 50 | first_run | 1.420 | 1.375 | 9.977 |
| 50 | steady_run | 1.008 | 1.043 | 4.380 |
| 200 | build | 0.785 | 0.678 | 2.074 |
| 200 | compile | 0.410 | 0.220 | 13.366 |
| 200 | first_run | 3.299 | 2.889 | 41.746 |
| 200 | steady_run | 2.041 | 1.990 | 23.229 |

## Topology: layered

| nodes | phase | swarms-networkx | swarms-rustworkx | langgraph |
| ---: | --- | ---: | ---: | ---: |
| 10 | build | 0.165 | 0.149 | 0.321 |
| 10 | compile | 0.061 | 0.056 | 0.942 |
| 10 | first_run | 0.675 | 0.664 | 2.890 |
| 10 | steady_run | 0.460 | 0.447 | 1.340 |
| 50 | build | 0.368 | 0.329 | 0.671 |
| 50 | compile | 0.154 | 0.105 | 4.200 |
| 50 | first_run | 1.505 | 1.390 | 11.187 |
| 50 | steady_run | 0.973 | 0.942 | 4.627 |
| 200 | build | 1.204 | 0.975 | 2.125 |
| 200 | compile | 0.489 | 0.285 | 15.980 |
| 200 | first_run | 4.399 | 4.265 | 44.414 |
| 200 | steady_run | 2.746 | 2.950 | 19.075 |

## Topology: tree

| nodes | phase | swarms-networkx | swarms-rustworkx | langgraph |
| ---: | --- | ---: | ---: | ---: |
| 10 | build | 0.138 | 0.159 | 0.338 |
| 10 | compile | 0.072 | 0.053 | 0.843 |
| 10 | first_run | 0.623 | 0.654 | 2.568 |
| 10 | steady_run | 0.499 | 0.482 | 1.410 |
| 50 | build | 0.247 | 0.219 | 0.711 |
| 50 | compile | 0.128 | 0.092 | 3.281 |
| 50 | first_run | 1.477 | 1.401 | 8.737 |
| 50 | steady_run | 1.105 | 1.147 | 4.434 |
| 200 | build | 0.629 | 0.542 | 2.027 |
| 200 | compile | 0.398 | 0.232 | 12.554 |
| 200 | first_run | 3.451 | 2.927 | 35.566 |
| 200 | steady_run | 2.922 | 2.076 | 17.193 |

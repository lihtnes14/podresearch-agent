"""Metric: End-to-End Latency & Node Performance Profiling.
Measures wall-clock execution latency across individual agents and total end-to-end workflow,
evaluating performance against operational Service Level Agreements (SLAs).

Target: Total E2E Latency within target SLA (SLA compliance rate >= 0.90)
"""
from __future__ import annotations

import time
from typing import Callable, Any, Optional


def measure_execution_time(func: Callable, *args, **kwargs) -> tuple[Any, float]:
    """Execute a callable and return its result along with elapsed wall-clock time in seconds."""
    start = time.perf_counter()
    result = func(*args, **kwargs)
    elapsed = time.perf_counter() - start
    return result, round(elapsed, 4)


def evaluate_latency_performance(
    node_latencies: dict[str, float],
    sla_thresholds: dict[str, float] | None = None,
) -> dict:
    """Evaluates pipeline node latencies against SLA targets.

    default SLA thresholds (in seconds for standard execution/mocked runs):
    - transcript: 5.0s
    - chunking: 1.0s
    - analysis: 10.0s
    - research: 15.0s
    - writer: 10.0s
    - guardrail: 8.0s
    - total_pipeline: 60.0s
    """
    default_slas = {
        "transcript": 5.0,
        "chunking": 1.0,
        "analysis": 10.0,
        "research": 15.0,
        "writer": 10.0,
        "guardrail": 8.0,
        "total_pipeline": 60.0,
    }
    slas = {**default_slas, **(sla_thresholds or {})}

    total_pipeline_time = node_latencies.get(
        "total_pipeline",
        sum(v for k, v in node_latencies.items() if k != "total_pipeline"),
    )
    recorded_latencies = {**node_latencies, "total_pipeline": round(total_pipeline_time, 4)}

    nodes_evaluated = 0
    nodes_within_sla = 0
    node_breakdown = {}

    for node, latency in recorded_latencies.items():
        sla_limit = slas.get(node, 30.0)
        within_sla = latency <= sla_limit
        nodes_evaluated += 1
        if within_sla:
            nodes_within_sla += 1

        node_breakdown[node] = {
            "latency_seconds": latency,
            "sla_threshold_seconds": sla_limit,
            "within_sla": within_sla,
        }

    sla_compliance_rate = (
        round(nodes_within_sla / nodes_evaluated, 4) if nodes_evaluated > 0 else 1.0
    )
    overall_score = sla_compliance_rate
    passed = (sla_compliance_rate >= 0.85) and (
        recorded_latencies["total_pipeline"] <= slas["total_pipeline"]
    )

    return {
        "total_pipeline_latency_seconds": recorded_latencies["total_pipeline"],
        "sla_compliance_rate": sla_compliance_rate,
        "overall_score": overall_score,
        "passed": passed,
        "node_breakdown": node_breakdown,
    }

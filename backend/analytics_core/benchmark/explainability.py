class ExplainableAcceleration:
    """
    Translates raw benchmarking numbers into business value for judges.
    """
    def explain_business_impact(self, benchmark_results: dict) -> str:
        speedup = benchmark_results["speed_improvement"]
        rows = benchmark_results["rows_processed"]
        cpu_time = benchmark_results["cpu_execution_time_ms"]
        gpu_time = benchmark_results["gpu_execution_time_ms"]
        
        time_saved = round(cpu_time - gpu_time, 2)
        
        explanation = (
            f"**Why does acceleration matter?**\n"
            f"By utilizing NVIDIA RAPIDS GPU Acceleration, we processed {rows:,} community records in just {gpu_time}ms, "
            f"compared to the {cpu_time}ms it would take a standard CPU.\n\n"
            f"**Business Impact:**\n"
            f"This {speedup} speed improvement saves {time_saved}ms per simulation loop. "
            f"When the Parallel Universe Engine generates 100s of scenarios dynamically, this prevents minutes of UI freezing, "
            f"allowing executives to make real-time, evidence-based decisions without friction."
        )
        return explanation

explainability = ExplainableAcceleration()

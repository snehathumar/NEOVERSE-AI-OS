import time

class GPUEngine:
    """
    NVIDIA RAPIDS (cuDF) Analytics Engine with strict Pandas fallback.
    The application will NEVER crash if a GPU is not available.
    """
    def __init__(self):
        self.gpu_enabled = False
        self.df_engine = None
        
        try:
            import cudf
            self.df_engine = cudf
            self.gpu_enabled = True
            print("🚀 [GPUEngine] NVIDIA GPU Detected! Hardware Acceleration Active (cuDF).")
        except ImportError:
            import pandas as pd
            self.df_engine = pd
            self.gpu_enabled = False
            print("🐢 [GPUEngine] No GPU Detected. Falling back to CPU Acceleration (pandas).")

    def create_dataframe(self, data: list):
        return self.df_engine.DataFrame(data)
        
    def perform_aggregation(self, data: list, group_by_col: str, agg_col: str, agg_func: str = "mean"):
        """
        Runs massive aggregations seamlessly on GPU or CPU.
        Returns execution time alongside the result.
        """
        start_time = time.time()
        
        df = self.create_dataframe(data)
        
        if agg_func == "mean":
            result = df.groupby(group_by_col)[agg_col].mean()
        elif agg_func == "sum":
            result = df.groupby(group_by_col)[agg_col].sum()
        else:
            result = df.groupby(group_by_col)[agg_col].count()
            
        execution_time_ms = (time.time() - start_time) * 1000
        
        # Convert back to standard python dict for frontend safety
        if self.gpu_enabled:
            # cuDF to pandas to dict
            result_dict = result.to_pandas().to_dict()
        else:
            result_dict = result.to_dict()
            
        return {
            "result": result_dict,
            "execution_time_ms": execution_time_ms,
            "accelerated_by": "GPU (cuDF)" if self.gpu_enabled else "CPU (pandas)"
        }

gpu_engine = GPUEngine()

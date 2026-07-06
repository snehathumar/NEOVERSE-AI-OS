from backend.analytics_core.gpu.gpu_engine import gpu_engine

class DataPipeline:
    """
    Modular Data Processing Pipeline.
    Raw Data -> Cleaning -> Transformation -> Feature Engineering -> Analytics
    """
    def process_community_dataset(self, raw_data: list):
        print(f"⚙️ [Pipeline] Ingesting {len(raw_data)} raw records.")
        # 1. Cleaning
        cleaned = [r for r in raw_data if r.get("revenue") is not None]
        
        # 2. Transformation (Delegated to Hardware Layer)
        print("⚙️ [Pipeline] Delegating massive aggregation to Hardware Layer...")
        analytics_result = gpu_engine.perform_aggregation(
            data=cleaned,
            group_by_col="industry",
            agg_col="revenue",
            agg_func="mean"
        )
        
        return analytics_result

data_pipeline = DataPipeline()

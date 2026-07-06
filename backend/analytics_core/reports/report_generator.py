import json
import csv
import io

class ReportGenerator:
    """
    Generates downloadable Benchmark and Analytics Reports.
    """
    def generate_json_report(self, data: dict) -> str:
        return json.dumps(data, indent=4)
        
    def generate_csv_report(self, data: list) -> str:
        if not data:
            return ""
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        return output.getvalue()

report_generator = ReportGenerator()

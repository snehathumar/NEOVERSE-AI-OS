from backend.reports.generator import EnterpriseReportGenerator

try:
    report_gen = EnterpriseReportGenerator(output_dir="exports/reports")
    mock_data = {
        "prompt": "Test",
        "facts": ["Fact 1"],
        "confidence": 89,
        "recommendation": "Do it",
        "universes": {"Best Case": "Money"}
    }
    path = report_gen.generate_decision_report("DEC-123", mock_data)
    print("Success:", path)
except Exception as e:
    print("Error:", e)

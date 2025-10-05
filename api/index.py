from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import statistics

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Telemetry data from q-vercel-latency.json
TELEMETRY_DATA = [
    {"region": "apac", "service": "catalog", "latency_ms": 187.07, "uptime_pct": 98.829, "timestamp": 20250301},
    {"region": "apac", "service": "recommendations", "latency_ms": 137.62, "uptime_pct": 98.681, "timestamp": 20250302},
    {"region": "apac", "service": "catalog", "latency_ms": 135.9, "uptime_pct": 98.704, "timestamp": 20250303},
    {"region": "apac", "service": "payments", "latency_ms": 138, "uptime_pct": 97.296, "timestamp": 20250304},
    {"region": "apac", "service": "payments", "latency_ms": 128.18, "uptime_pct": 99.372, "timestamp": 20250305},
    {"region": "apac", "service": "recommendations", "latency_ms": 198.86, "uptime_pct": 98.227, "timestamp": 20250306},
    {"region": "apac", "service": "support", "latency_ms": 112.09, "uptime_pct": 97.858, "timestamp": 20250307},
    {"region": "apac", "service": "checkout", "latency_ms": 227.07, "uptime_pct": 98.912, "timestamp": 20250308},
    {"region": "apac", "service": "checkout", "latency_ms": 138.31, "uptime_pct": 97.273, "timestamp": 20250309},
    {"region": "apac", "service": "analytics", "latency_ms": 220.33, "uptime_pct": 97.615, "timestamp": 20250310},
    {"region": "apac", "service": "recommendations", "latency_ms": 218.8, "uptime_pct": 97.126, "timestamp": 20250311},
    {"region": "apac", "service": "catalog", "latency_ms": 186.75, "uptime_pct": 97.359, "timestamp": 20250312},
    {"region": "emea", "service": "payments", "latency_ms": 149.92, "uptime_pct": 97.554, "timestamp": 20250301},
    {"region": "emea", "service": "payments", "latency_ms": 216.93, "uptime_pct": 97.991, "timestamp": 20250302},
    {"region": "emea", "service": "support", "latency_ms": 139.06, "uptime_pct": 97.192, "timestamp": 20250303},
    {"region": "emea", "service": "payments", "latency_ms": 133.51, "uptime_pct": 97.475, "timestamp": 20250304},
    {"region": "emea", "service": "support", "latency_ms": 123.86, "uptime_pct": 99.352, "timestamp": 20250305},
    {"region": "emea", "service": "analytics", "latency_ms": 202.14, "uptime_pct": 97.502, "timestamp": 20250306},
    {"region": "emea", "service": "support", "latency_ms": 226.12, "uptime_pct": 97.759, "timestamp": 20250307},
    {"region": "emea", "service": "checkout", "latency_ms": 111.34, "uptime_pct": 99.488, "timestamp": 20250308},
    {"region": "emea", "service": "checkout", "latency_ms": 188.38, "uptime_pct": 98.215, "timestamp": 20250309},
    {"region": "emea", "service": "analytics", "latency_ms": 178.52, "uptime_pct": 97.539, "timestamp": 20250310},
    {"region": "emea", "service": "catalog", "latency_ms": 182.01, "uptime_pct": 97.488, "timestamp": 20250311},
    {"region": "emea", "service": "analytics", "latency_ms": 217.21, "uptime_pct": 98.469, "timestamp": 20250312},
    {"region": "amer", "service": "checkout", "latency_ms": 143.4, "uptime_pct": 97.259, "timestamp": 20250301},
    {"region": "amer", "service": "analytics", "latency_ms": 146.22, "uptime_pct": 98.399, "timestamp": 20250302},
    {"region": "amer", "service": "support", "latency_ms": 143.78, "uptime_pct": 99.056, "timestamp": 20250303},
    {"region": "amer", "service": "support", "latency_ms": 205, "uptime_pct": 98.61, "timestamp": 20250304},
    {"region": "amer", "service": "payments", "latency_ms": 209.81, "uptime_pct": 98.82, "timestamp": 20250305},
    {"region": "amer", "service": "analytics", "latency_ms": 196.39, "uptime_pct": 98.351, "timestamp": 20250306},
    {"region": "amer", "service": "support", "latency_ms": 158.91, "uptime_pct": 98.837, "timestamp": 20250307},
    {"region": "amer", "service": "recommendations", "latency_ms": 127.71, "uptime_pct": 99.448, "timestamp": 20250308},
    {"region": "amer", "service": "support", "latency_ms": 217.22, "uptime_pct": 98.237, "timestamp": 20250309},
    {"region": "amer", "service": "support", "latency_ms": 234.09, "uptime_pct": 98.511, "timestamp": 20250310},
    {"region": "amer", "service": "catalog", "latency_ms": 215.24, "uptime_pct": 97.267, "timestamp": 20250311},
    {"region": "amer", "service": "analytics", "latency_ms": 196.91, "uptime_pct": 99.052, "timestamp": 20250312}
]

class TelemetryRequest(BaseModel):
    regions: list[str]
    threshold_ms: int

def calculate_p95(values):
    """Calculate 95th percentile"""
    sorted_values = sorted(values)
    index = int(len(sorted_values) * 0.95)
    return round(sorted_values[min(index, len(sorted_values) - 1)], 2)

@app.get("/")
def read_root():
    return {
        "message": "eShopCo Telemetry Analysis API",
        "usage": "POST /api/analyze with {\"regions\": [\"emea\", \"amer\"], \"threshold_ms\": 154}"
    }

@app.post("/api/analyze")
def analyze_telemetry(request: TelemetryRequest):
    """Analyze telemetry data for specified regions"""
    results = {}
    
    for region in request.regions:
        # Filter data for this region
        region_data = [r for r in TELEMETRY_DATA if r["region"] == region]
        
        if not region_data:
            results[region] = {"error": f"Region '{region}' not found"}
            continue
        
        # Extract metrics
        latencies = [r["latency_ms"] for r in region_data]
        uptimes = [r["uptime_pct"] for r in region_data]
        
        # Calculate required metrics
        avg_latency = round(statistics.mean(latencies), 2)
        p95_latency = calculate_p95(latencies)
        avg_uptime = round(statistics.mean(uptimes), 2)
        breaches = sum(1 for lat in latencies if lat > request.threshold_ms)
        
        results[region] = {
            "avg_latency": avg_latency,
            "p95_latency": p95_latency,
            "avg_uptime": avg_uptime,
            "breaches": breaches
        }
    
    return results
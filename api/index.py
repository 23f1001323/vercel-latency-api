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

# Sample telemetry data (replace with actual data from the bundle)
TELEMETRY_DATA = {
    "emea": [
        {"latency_ms": 120, "uptime": 99.9},
        {"latency_ms": 145, "uptime": 99.8},
        {"latency_ms": 160, "uptime": 99.7},
        {"latency_ms": 130, "uptime": 99.9},
        {"latency_ms": 170, "uptime": 99.6},
        {"latency_ms": 155, "uptime": 99.8},
        {"latency_ms": 140, "uptime": 99.9},
        {"latency_ms": 165, "uptime": 99.7},
        {"latency_ms": 150, "uptime": 99.8},
        {"latency_ms": 180, "uptime": 99.5},
    ],
    "amer": [
        {"latency_ms": 110, "uptime": 99.9},
        {"latency_ms": 125, "uptime": 99.8},
        {"latency_ms": 140, "uptime": 99.9},
        {"latency_ms": 155, "uptime": 99.7},
        {"latency_ms": 160, "uptime": 99.8},
        {"latency_ms": 145, "uptime": 99.9},
        {"latency_ms": 130, "uptime": 99.8},
        {"latency_ms": 170, "uptime": 99.6},
        {"latency_ms": 150, "uptime": 99.9},
        {"latency_ms": 165, "uptime": 99.7},
    ],
    "apac": [
        {"latency_ms": 200, "uptime": 99.5},
        {"latency_ms": 210, "uptime": 99.6},
        {"latency_ms": 195, "uptime": 99.7},
        {"latency_ms": 220, "uptime": 99.4},
        {"latency_ms": 205, "uptime": 99.6},
        {"latency_ms": 190, "uptime": 99.7},
        {"latency_ms": 215, "uptime": 99.5},
        {"latency_ms": 200, "uptime": 99.6},
        {"latency_ms": 225, "uptime": 99.4},
        {"latency_ms": 210, "uptime": 99.5},
    ]
}

class TelemetryRequest(BaseModel):
    regions: list[str]
    threshold_ms: int

def calculate_p95(values):
    """Calculate 95th percentile"""
    sorted_values = sorted(values)
    index = int(len(sorted_values) * 0.95)
    return sorted_values[index] if sorted_values else 0

@app.get("/")
def read_root():
    return {
        "message": "eShopCo Telemetry Analysis API",
        "endpoint": "POST /api/analyze",
        "usage": {
            "body": {
                "regions": ["emea", "amer"],
                "threshold_ms": 154
            }
        }
    }

@app.post("/api/analyze")
def analyze_telemetry(request: TelemetryRequest):
    """Analyze telemetry data for specified regions"""
    results = {}
    
    for region in request.regions:
        if region not in TELEMETRY_DATA:
            results[region] = {
                "error": f"Region '{region}' not found"
            }
            continue
        
        data = TELEMETRY_DATA[region]
        latencies = [record["latency_ms"] for record in data]
        uptimes = [record["uptime"] for record in data]
        
        # Calculate metrics
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
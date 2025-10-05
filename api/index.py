# api/index.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import json
import statistics

app = FastAPI()

# Enable CORS for POST requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Load telemetry data from the data file
import os
with open(os.path.join(os.path.dirname(__file__), "..", "telemetry_data.json"), "r") as f:
    telemetry_data = json.load(f)

class LatencyRequest(BaseModel):
    regions: List[str]
    threshold_ms: int

class RegionMetrics(BaseModel):
    avg_latency: float
    p95_latency: float
    avg_uptime: float
    breaches: int

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.post("/latency-metrics")
def get_latency_metrics(request: LatencyRequest) -> Dict[str, RegionMetrics]:
    """
    Calculate latency metrics for specified regions.
    
    Returns per-region metrics including:
    - avg_latency: mean latency
    - p95_latency: 95th percentile latency
    - avg_uptime: mean uptime percentage
    - breaches: count of records above threshold
    """
    results = {}
    
    for region in request.regions:
        # Filter data for this region
        region_data = [record for record in telemetry_data if record["region"] == region]
        
        if not region_data:
            # If no data for region, return zeros
            results[region] = RegionMetrics(
                avg_latency=0.0,
                p95_latency=0.0,
                avg_uptime=0.0,
                breaches=0
            )
            continue
        
        # Extract latencies and uptimes
        latencies = [record["latency_ms"] for record in region_data]
        uptimes = [record["uptime_pct"] for record in region_data]
        
        # Calculate metrics
        avg_latency = statistics.mean(latencies)
        p95_latency = statistics.quantiles(latencies, n=20)[18]  # 95th percentile (19th out of 20)
        avg_uptime = statistics.mean(uptimes)
        breaches = sum(1 for latency in latencies if latency > request.threshold_ms)
        
        results[region] = RegionMetrics(
            avg_latency=round(avg_latency, 2),
            p95_latency=round(p95_latency, 2),
            avg_uptime=round(avg_uptime, 2),
            breaches=breaches
        )
    
    return results
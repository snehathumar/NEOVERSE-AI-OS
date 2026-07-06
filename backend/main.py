import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

from backend.orchestrator.router import EnterpriseRouter
from backend.deployment.observability.metrics import HTTP_REQUEST_LATENCY, HTTP_REQUEST_COUNT
from backend.billing.stripe_provider import StripeProvider
import time

try:
    from prometheus_client import make_asgi_app
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize the global EnterpriseRouter
    app.state.router = EnterpriseRouter()
    await app.state.router.initialize_system()
    yield
    # Shutdown: Cleanup resources
    pass

app = FastAPI(
    title="NEOVERSE AI OS API",
    description="Enterprise API Gateway for NEOVERSE Intelligence Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this via Ingress or env vars
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Prometheus metrics endpoint if available
if PROMETHEUS_AVAILABLE:
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)

@app.middleware("http")
async def track_metrics(request: Request, call_next):
    """Middleware to track HTTP request latency and counts for Prometheus."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    if PROMETHEUS_AVAILABLE:
        HTTP_REQUEST_LATENCY.labels(
            method=request.method, 
            endpoint=request.url.path
        ).observe(process_time)
        
        HTTP_REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            http_status=response.status_code
        ).inc()
        
    return response

@app.get("/health")
async def health_check():
    """Liveness probe for Kubernetes."""
    return {"status": "ok", "service": "neoverse-api"}

@app.get("/ready")
async def readiness_check():
    """Readiness probe for Kubernetes."""
    # Ensure router is initialized
    if hasattr(app.state, "router"):
        return {"status": "ready"}
    raise HTTPException(status_code=503, detail="Router not initialized")

@app.post("/api/v1/decisions")
async def process_decision(request: Request):
    """
    Main entrypoint for the Enterprise Intelligence Pipeline.
    Passes the raw request payload and HTTP headers (for SecurityModule) to the Router.
    """
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
    context = {
        "user_request": payload,
        "http_headers": dict(request.headers) # Passed directly to SecurityModule
    }
    
    # Execute the synchronous pipeline
    result = await app.state.router.process_request(context)
    
    return {"status": "success", "data": result}

@app.post("/api/v1/billing/checkout")
async def create_checkout_session(request: Request):
    try:
        payload = await request.json()
        org_id = payload.get("org_id")
        plan_id = payload.get("plan_id")
        
        provider = StripeProvider()
        url = provider.create_checkout_session(
            org_id=org_id,
            plan_id=plan_id,
            success_url="https://neoverse.ai/dashboard/billing/success",
            cancel_url="https://neoverse.ai/dashboard/billing/cancel"
        )
        return {"status": "success", "checkout_url": url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/billing/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        provider = StripeProvider()
        event = provider.verify_webhook_signature(payload, sig_header)
        
        if event["type"] == "checkout.session.completed":
            # Handle successful subscription
            data = event["data"]["object"]
            org_id = data.get("client_reference_id")
            # Update database logic here (e.g., set status="active")
            pass
            
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail="Webhook handler failed")

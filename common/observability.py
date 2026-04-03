from fastapi import FastAPI
from prometheus_client import make_asgi_app
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

def instrument_app(app: FastAPI, service_name: str):
    # Set up basic OpenTelemetry tracing 
    # (In a real production environment, you would use an OTLP exporter to Jaeger/Zipkin here)
    provider = TracerProvider()
    trace.set_tracer_provider(provider)
    
    # Instrument FastAPI for traces
    FastAPIInstrumentor.instrument_app(app)
    
    # Add Prometheus metrics /metrics endpoint
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)
    
    # Optionally, we can also inject logging configurations here

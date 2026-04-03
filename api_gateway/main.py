from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
import httpx
import os
from common.logging_utils import setup_logging
from common.middleware import CorrelationIdMiddleware
from common.auth_utils import decode_token
from common.observability import instrument_app

logger = setup_logging("api-gateway")
app = FastAPI(title="API Gateway")
app.add_middleware(CorrelationIdMiddleware)
instrument_app(app, "api-gateway")

SERVICES = {
    "auth": {"url": "http://auth-service:8000", "prefix": "/auth"},
    "users": {"url": "http://user-service:8000", "prefix": "/users"},
    "orchestrator": {"url": "http://orchestrator:8000", "prefix": "/api"},
    "audit": {"url": "http://audit-service:8000", "prefix": "/audit"},
}

async def validate_token(request: Request):
    if request.url.path.startswith("/auth/login") or request.url.path.startswith("/auth/register") or request.url.path == "/health":
        return
    
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    token = auth_header.split(" ")[1]
    try:
        decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(service: str, path: str, request: Request, _ = Depends(validate_token)):
    if service not in SERVICES:
        raise HTTPException(status_code=404, detail="Service not found")
    
    svc = SERVICES[service]
    url = f"{svc['url']}{svc['prefix']}/{path}"
    logger.info(f"Proxying {request.method} /{service}/{path} -> {url}")
    async with httpx.AsyncClient() as client:
        method = request.method
        # Filter out hop-by-hop headers that shouldn't be forwarded
        excluded_headers = {"host", "content-length", "transfer-encoding", "connection"}
        headers = {k: v for k, v in request.headers.items() if k.lower() not in excluded_headers}
        # Propagate correlation ID
        headers["X-Correlation-ID"] = request.headers.get("X-Correlation-ID", "")
        
        content = await request.body()
        
        try:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                content=content,
                params=request.query_params,
                timeout=30.0
            )
            resp_headers = {k: v for k, v in response.headers.items() 
                           if k.lower() not in {"content-length", "content-encoding", "transfer-encoding"}}
            return JSONResponse(
                status_code=response.status_code,
                content=response.json() if response.content else None,
                headers=resp_headers
            )
        except Exception as e:
            logger.error(f"Proxy error for {url}: {type(e).__name__}: {str(e)}")
            raise HTTPException(status_code=502, detail="Service unreachable")

@app.get("/health")
async def health():
    return {"status": "gateway healthy"}

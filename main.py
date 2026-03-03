from fastapi import FastAPI, Request , Response
import random 
import string 
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from typing import Dict, Tuple
import time

app = FastAPI()

class AdvancedMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

        # Track last request time per (client_ip, path) instead of only IP.
        # This avoids blocking follow-up browser requests to different endpoints
        # like /openapi.json or /favicon.ico after loading /docs or /.
        self.rate_limit_records: Dict[Tuple[str, str], float] = {}
    
    async def log_message(self, message):
        print(message)
    
    async def dispatch(self, request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path
        rate_limit_key = (client_ip, path)
        current_time = time.time()

        last_time = self.rate_limit_records.get(rate_limit_key)
        if last_time is not None and current_time - last_time < 1:
            return Response(
                content="Rate Limit Exceeded",
                status_code=429,
                headers={"Retry-After": "1"},
            )

        # record the time of this request
        self.rate_limit_records[rate_limit_key] = current_time

        await self.log_message(f"Request to {path}")
        
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        custom_header = {"X-process_time": str(process_time)}
        for header, value in custom_header.items():
            response.headers.append(header, value)
    
        await self.log_message(f"Response for {path} took {process_time} seconds")

        return response

# @app.middleware("http")
# async def request_id_logging(request: Request, call_next):
#     response = await call_next(request)
#     random_letters = ''.join(random.choices(string.ascii_uppercase, k=5))
#     print(f"Request ID: {random_letters}")
#     response.headers["X-Request-ID"] = random_letters
#     return response

app.add_middleware(AdvancedMiddleware)

@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}

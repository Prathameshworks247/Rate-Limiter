from fastapi import FastAPI, Request , Response
import random 
import string 
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from typing import Dict, Any
import time

app = FastAPI()

class AdvancedMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

        self.rate_limit_records: Dict[str, float] = {}
    
    async def log_message(self, message):
        print(message)
    
    async def dispatch(self, request, call_next):
        client_ip = request.client.host
        current_time = time.time()

        last_time = self.rate_limit_records.get(client_ip)
        if last_time is not None and current_time - last_time < 1:
            return Response(content="Rate Limit Exceeded", status_code=429)

        # record the time of this request
        self.rate_limit_records[client_ip] = current_time

        path = request.url.path
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

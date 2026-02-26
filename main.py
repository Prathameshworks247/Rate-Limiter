from fastapi import FastAPI, Request 
import random 
import string 

app = FastAPI()

@app.middleware("http")
async def request_id_logging(request: Request, call_next):
    response = await call_next(request)
    random_letters = ''.join(random.choices(string.ascii_uppercase, k=5))
    print(f"Request ID: {random_letters}")
    response.headers["X-Request-ID"] = random_letters
    return response

@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}

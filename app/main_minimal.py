from fastapi import FastAPI
import os
app = FastAPI()
@app.get("/health")
def health():
    return {"status":"ok","minimal":True}
@app.get("/")
def root():
    return {"status":"running","minimal":True}

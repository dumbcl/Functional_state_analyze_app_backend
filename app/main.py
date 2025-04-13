from fastapi import FastAPI
from app.routes import auth, health, escal_results

app = FastAPI()
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(health.router, tags=["health"])
app.include_router(escal_results.router, tags=["escal_results"])
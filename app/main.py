from fastapi import FastAPI
from app.routes import auth, health, escal_results, escal_daily_results, gench_test, personal_report, reactions_test, rufie_test, strup_test

app = FastAPI()
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(health.router, tags=["health"])
app.include_router(escal_results.router, tags=["escal_results"])
app.include_router(escal_daily_results.router, tags=["escal_daily_results"])
app.include_router(gench_test.router, tags=["gench_test"])
app.include_router(personal_report.router, tags=["personal_report"])
app.include_router(reactions_test.router, tags=["reactions_test"])
app.include_router(rufie_test.router, tags=["rufie_test"])
app.include_router(strup_test.router, tags=["strup_test"])
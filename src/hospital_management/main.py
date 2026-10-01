from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from hospital_management.database.session import initialize_database
from hospital_management.routes import auth, health, patients, staff

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
	initialize_database()
	yield


app = FastAPI(title="Hospital Management System", lifespan=lifespan)
app.add_middleware(
	CORSMiddleware,
	allow_origins=["http://localhost:5173"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)
app.include_router(health.router)
app.include_router(staff.router)
app.include_router(auth.router)
app.include_router(patients.router)

if FRONTEND_DIR.exists():
	app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/", include_in_schema=False)
def frontend() -> FileResponse:
	return FileResponse(FRONTEND_DIR / "index.html")

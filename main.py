import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from app.database import Base, engine
from app.routers import auth_routes, receptionist, doctor, dashboard

# Automatically create local SQLite tables on boot
Base.metadata.create_all(bind=engine)

# Ensure upload directory exists for ECG/X-Ray files
os.makedirs("static/uploads", exist_ok=True)

app = FastAPI(title="MediCare Hospital Management System")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include Modular Routers
app.include_router(auth_routes.router)
app.include_router(receptionist.router)
app.include_router(doctor.router)
app.include_router(dashboard.router)

@app.get("/")
def home():
    return RedirectResponse(url="/login")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
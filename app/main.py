from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import auth, users, notes, files

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Vuln Notes API",
    version="0.1.0",
    description="Учебное API с намеренными уязвимостями (SAST/SCA/DAST practice).",
)

# CORS открыт всем — упрощает подключение будущего фронта,
# но и это тоже слабое место (в реальности так делать нельзя).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(notes.router)
app.include_router(files.router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"name": "Vuln Notes API v3", "docs": "/docs"}

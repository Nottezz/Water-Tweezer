import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from water_tweezer.web_app.api import router as api_router
from water_tweezer.web_app.auth.router import router as auth_router

app = FastAPI(title="Water Tweezer", description="Water Tweezer API for mini-app")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://web.telegram.org",
        "https://telegram.org",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

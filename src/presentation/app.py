from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Browser / cross-origin WebSocket clients often need this; avoids some rejected upgrades.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes (side-effect imports).
import src.presentation.api.publish  # noqa: E402,F401
from fastapi import WebSocket

from src.presentation.dependencies import get_robot_commander
from src.presentation.app import app


@app.websocket("/v1/ws/publish")
async def publish(websocket: WebSocket):
    """
    Receive base64 JPEG frames over WebSocket, optional local preview, and publish the
    same payload string to Redis (subscribers must use the same ``channel`` query param).
    """
    await websocket.accept()

    robot_commander = get_robot_commander()
    await robot_commander.handle_socket(websocket)

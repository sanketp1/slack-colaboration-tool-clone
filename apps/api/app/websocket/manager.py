from fastapi import WebSocket
from typing import List, Dict
import json
import redis.asyncio as redis
from app.core.config import settings

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[str, WebSocket] = {}
        self.redis_client = redis.from_url(settings.redis_url)

    async def connect(self, websocket: WebSocket, user_id: str = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        if user_id:
            self.user_connections[user_id] = websocket
            # Publish user online event
            await self.redis_client.publish(
                "presence",
                json.dumps({
                    "type": "user_online",
                    "user_id": user_id
                })
            )

    async def disconnect(self, websocket: WebSocket, user_id: str = None):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if user_id and user_id in self.user_connections:
            del self.user_connections[user_id]
            # Publish user offline event
            await self.redis_client.publish(
                "presence",
                json.dumps({
                    "type": "user_offline",
                    "user_id": user_id
                })
            )

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def send_personal_json(self, data: dict, websocket: WebSocket):
        await websocket.send_text(json.dumps(data))

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove broken connections
                self.active_connections.remove(connection)

    async def broadcast_json(self, data: dict):
        message = json.dumps(data)
        await self.broadcast(message)

    async def send_to_user(self, user_id: str, data: dict):
        if user_id in self.user_connections:
            try:
                await self.send_personal_json(data, self.user_connections[user_id])
            except:
                # Remove broken connection
                del self.user_connections[user_id]

    async def broadcast_to_channel(self, channel_id: str, data: dict):
        # Publish to Redis for channel-specific broadcasting
        await self.redis_client.publish(
            f"channel:{channel_id}",
            json.dumps(data)
        )

    async def subscribe_to_channel(self, channel_id: str, websocket: WebSocket):
        # Subscribe to Redis channel for real-time updates
        pubsub = self.redis_client.pubsub()
        await pubsub.subscribe(f"channel:{channel_id}")
        
        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    await websocket.send_text(message["data"].decode())
                except:
                    break
        
        await pubsub.unsubscribe(f"channel:{channel_id}")
        await pubsub.close() 
import asyncio
import websockets
import json
from datetime import datetime

async def test_websocket():
    uri = "ws://localhost:8000/ws/test-client-123"
    
    async with websockets.connect(uri) as websocket:
        print("Connected to WebSocket")
        
        # Send a chat message
        message = {
            "type": "chat",
            "data": {
                "message": "Hello, I'm looking for a sports t-shirt",
                "timestamp": datetime.now().isoformat()
            }
        }
        
        await websocket.send(json.dumps(message))
        print(f"Sent: {message}")
        
        # Receive response
        response = await websocket.recv()
        print(f"Received: {response}")
        
        # Send ping
        ping = {"type": "ping", "data": {}}
        await websocket.send(json.dumps(ping))
        
        # Receive pong
        pong = await websocket.recv()
        print(f"Pong: {pong}")

# Run the test
asyncio.run(test_websocket())
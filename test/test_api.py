import requests
import base64
import json

BASE_URL = "http://localhost:8000"

def test_health():
    response = requests.get(f"{BASE_URL}/health")
    print("Health Check:", response.json())

def test_chat():
    payload = {
        "message": "What can you help me with?",
        "session_id": None
    }
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    print("Chat Response:", response.json())

def test_chat_with_image():
    # Read and encode a test image (create a small test image first)
    # with open("test_image.jpg", "rb") as image_file:
    #     encoded_string = base64.b64encode(image_file.read()).decode()
    
    payload = {
        "message": "Find me products similar to this",
        "image": "base64_encoded_image_here",  # Replace with actual base64
        "session_id": None
    }
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    print("Image Chat Response:", response.json())

def test_session_creation():
    response = requests.post(f"{BASE_URL}/session/create")
    print("Session Created:", response.json())

if __name__ == "__main__":
    print("Testing AI Commerce Agent API...")
    test_health()
    test_chat()
    test_session_creation()
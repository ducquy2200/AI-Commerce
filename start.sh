#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Check if port is already in use
PORT=8000
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "Port $PORT is already in use. Stopping existing process..."
    kill $(lsof -Pi :$PORT -sTCP:LISTEN -t)
    sleep 2
fi

# Start the API server
echo "Starting AI Commerce Agent API Gateway on port $PORT..."
python run.py
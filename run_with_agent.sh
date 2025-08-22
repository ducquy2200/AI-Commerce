#!/bin/bash

echo "Starting AI Commerce Agent with LangChain..."

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ] && ! grep -q "OPENAI_API_KEY" .env; then
    echo "❌ Error: OPENAI_API_KEY not found in environment or .env file"
    echo "Please set your OpenAI API key in the .env file"
    exit 1
fi

# Activate virtual environment
source ./venv/bin/activate

# Initialize vector store if needed
if [ ! -d "./chroma_db" ]; then
    echo "📦 Initializing product vector store..."
    python init_agent.py
fi

# Start the server
echo "🚀 Starting API Gateway with LangChain Agent..."
python run.py
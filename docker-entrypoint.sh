#!/bin/bash
set -e

echo "Starting AI Commerce Agent with Docker..."

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Error: OPENAI_API_KEY environment variable is not set"
    exit 1
fi

# Initialize vector store if it doesn't exist
if [ ! -d "./chroma_db" ] || [ -z "$(ls -A ./chroma_db)" ]; then
    echo "Initializing product vector store..."
    python init_agent.py
fi

# Start the application
echo "Starting API Gateway with LangChain Agent..."
exec python run.py
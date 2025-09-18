#!/bin/bash

# Capstone RAG System Setup Script
echo "🚀 Setting up Capstone RAG System..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Start required services
echo "📦 Starting PostgreSQL and Ollama services..."
docker-compose up -d postgres ollama

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
if ! docker ps | grep -q postgres; then
    echo "❌ PostgreSQL container failed to start"
    exit 1
fi

if ! docker ps | grep -q ollama; then
    echo "❌ Ollama container failed to start"
    exit 1
fi

echo "✅ Services started successfully"

# Setup backend
echo "🐍 Setting up Python backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
if [ ! -f ".env" ]; then
    cat > .env << EOF
DATABASE_URL=postgresql://postgres:postgres@localhost:5050/pgvector
OLLAMA_URL=http://localhost:11434
OPENAI_API_KEY=your-openai-api-key-here
PROJECT_TYPE=literature
EOF
    echo "📝 Created .env file. Please update with your API keys."
fi

cd ..

# Setup frontend
echo "⚛️ Setting up React frontend..."
cd frontend

# Install dependencies
if [ ! -d "node_modules" ]; then
    npm install
fi

# Create .env file
if [ ! -f ".env" ]; then
    cat > .env << EOF
VITE_API_BASE=http://localhost:5000/api
EOF
    echo "📝 Created frontend .env file."
fi

cd ..

echo "🎉 Setup complete!"
echo ""
echo "To start the system:"
echo "1. Backend: cd backend && source venv/bin/activate && python app.py"
echo "2. Frontend: cd frontend && npm run dev"
echo ""
echo "The system will be available at:"
echo "- Frontend: http://localhost:3000"
echo "- Backend API: http://localhost:5000"
echo "- Database: localhost:5050"
echo ""
echo "Don't forget to:"
echo "- Update API keys in backend/.env"
echo "- Choose your project type (literature/documentation/research)"
echo "- Add sample data to the database"

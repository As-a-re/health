#!/bin/bash

echo "🚀 Starting Akan Health Assistant..."

# Check if MongoDB is running
if ! pgrep -x "mongod" > /dev/null; then
    echo "⚠️ MongoDB is not running. Please start MongoDB first."
    echo "On macOS: brew services start mongodb-community"
    echo "On Ubuntu: sudo systemctl start mongod"
    echo "On Windows: net start MongoDB"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

# Setup database
echo "🗄️ Setting up database..."
python scripts/setup_database.py
python scripts/train_akan_model.py

# Go back to root directory
cd ..

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
npm install

# Setup MongoDB collections
echo "🗄️ Setting up MongoDB collections..."
npm run setup-db

# Create .env file if it doesn't exist
if [ ! -f ".env.local" ]; then
    echo "📝 Creating .env.local file..."
    cat > .env.local << EOL
NEXT_PUBLIC_API_URL=http://localhost:8000/api
MONGODB_URL=mongodb://localhost:27017/akan_health_db
EOL
fi

# Create backend .env file if it doesn't exist
if [ ! -f "backend/.env" ]; then
    echo "📝 Creating backend .env file..."
    cat > backend/.env << EOL
MONGODB_URL=mongodb://localhost:27017/akan_health_db
SECRET_KEY=your-super-secret-jwt-key-change-in-production-2024
DEBUG=True
ENABLE_WEB_SEARCH=True
EOL
fi

echo "✅ Setup completed!"
echo ""
echo "🚀 Starting the application..."
echo "Backend will run on: http://localhost:8000"
echo "Frontend will run on: http://localhost:3000"
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both services"
echo ""

# Start both backend and frontend
npm run dev-full

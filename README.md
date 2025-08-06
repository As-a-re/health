# Akan Health Assistant

A comprehensive AI-powered health assistant with support for English and Akan languages. Features a 3D AI doctor interface, real-time health consultations, and comprehensive health record management.

## Features

- 🤖 **3D AI Doctor Interface** - Interactive 3D avatars with speech synthesis
- 🌍 **Multilingual Support** - English and Akan language support
- 🔍 **Internet Search Integration** - Real-time health information from web sources
- 📊 **Health Records Management** - Complete query history and analytics
- 🔐 **User Authentication** - Secure user accounts with JWT tokens
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile
- 🎤 **Voice Input** - Audio query support (planned)
- 📈 **Analytics Dashboard** - Usage statistics and insights

## Technology Stack

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - Modern UI components
- **React Three Fiber** - 3D graphics and animations
- **Lucide React** - Beautiful icons

### Backend
- **FastAPI** - Modern Python web framework
- **MongoDB** - NoSQL database for all data storage
- **Motor** - Async MongoDB driver
- **JWT Authentication** - Secure token-based auth
- **Pydantic** - Data validation and serialization
- **aiohttp** - Async HTTP client for web search

## Prerequisites

- **Node.js** 18 or higher
- **Python** 3.8 or higher
- **MongoDB** 4.4 or higher

## Quick Start

1. **Clone the repository**
   \`\`\`bash
   git clone <repository-url>
   cd akan-health-assistant
   \`\`\`

2. **Make the start script executable**
   \`\`\`bash
   chmod +x start.sh
   \`\`\`

3. **Run the setup and start script**
   \`\`\`bash
   ./start.sh
   \`\`\`

This will:
- Install all dependencies
- Set up the database
- Create sample data
- Start both backend and frontend servers

## Manual Setup

If you prefer to set up manually:

### 1. Backend Setup

\`\`\`bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database
python scripts/setup_database.py
python scripts/train_akan_model.py

# Start backend server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
\`\`\`

### 2. Frontend Setup

\`\`\`bash
# Install dependencies
npm install

# Setup MongoDB collections
npm run setup-db

# Create environment file
cp .env.example .env.local

# Start frontend server
npm run dev
\`\`\`

## Environment Variables

### Frontend (.env.local)
\`\`\`env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
\`\`\`

### Backend (backend/.env)
\`\`\`env
MONGODB_URL=mongodb://localhost:27017/akan_health_db
SECRET_KEY=your-super-secret-jwt-key-change-in-production-2024
DEBUG=True
ENABLE_WEB_SEARCH=True
\`\`\`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user

### Health Queries
- `POST /api/ask` - Ask health question
- `POST /api/ask-audio` - Ask health question via audio

### User Management
- `GET /api/user/profile` - Get user profile
- `PUT /api/user/profile` - Update user profile
- `GET /api/user/history` - Get query history
- `GET /api/user/stats` - Get user statistics

### Analytics
- `GET /api/logs/analytics` - Get usage analytics
- `GET /api/logs/query-logs` - Get detailed query logs

## Default Test Accounts

After running the setup, you can use these test accounts:

- **Admin**: admin@akanhealth.com / admin123
- **Test User**: test@example.com / testpass123
- **Akan User**: akan@example.com / akanpass123

## Project Structure

\`\`\`
akan-health-assistant/
├── app/                    # Next.js app directory
├── components/             # React components
├── lib/                   # Utility libraries
├── hooks/                 # Custom React hooks
├── backend/               # FastAPI backend
│   ├── app/              # Application code
│   ├── scripts/          # Setup scripts
│   └── requirements.txt  # Python dependencies
├── scripts/              # Setup scripts
└── README.md
\`\`\`

## Key Features Explained

### 3D AI Doctor Interface
- Interactive 3D avatars (male/female options)
- Speech synthesis for responses
- Visual feedback during conversations
- Realistic animations and gestures

### Multilingual Support
- Automatic language detection
- English and Akan language support
- Real-time translation capabilities
- Language-specific medical knowledge

### Health Records Management
- Complete query history
- Confidence scores for responses
- Model usage tracking
- Export capabilities

### Internet Search Integration
- DuckDuckGo API integration (no API key required)
- Real-time health information retrieval
- Enhanced responses with web data
- Fallback to local knowledge base

## Development

### Adding New Languages
1. Update the medical knowledge base in `backend/scripts/train_akan_model.py`
2. Add language detection logic in `backend/app/core/ai_models.py`
3. Update the frontend language toggle component

### Extending Medical Knowledge
1. Edit the `MEDICAL_KNOWLEDGE_BASE` in `backend/scripts/train_akan_model.py`
2. Run `python scripts/train_akan_model.py` to update the database
3. Restart the backend server

### Adding New AI Models
1. Implement model integration in `backend/app/core/ai_models.py`
2. Update the response generation logic
3. Add model-specific configuration options

## Deployment

### Frontend (Vercel)
1. Connect your repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy automatically on push

### Backend (Railway/Heroku)
1. Create a new app on your platform
2. Set environment variables
3. Deploy the backend directory

### Database (MongoDB Atlas)
1. Create a MongoDB Atlas cluster
2. Update the `MONGODB_URL` environment variable
3. Run the setup scripts to initialize data

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue on GitHub or contact the development team.

## Acknowledgments

- Built with modern web technologies
- Inspired by the need for accessible healthcare information
- Supports the Akan language community
- Uses free and open-source AI models

# Censorly - AI Profanity Filter SaaS Platform

A production-ready SaaS platform for AI-powered video content moderation and profanity filtering.

## Technology Stack

**Backend:**
- Flask 2.3.3 with Supabase database
- Deployed on Render: https://ai-profanity-filter.onrender.com

**Frontend:**
- React + TypeScript with Vite
- Deployed on Vercel: https://censorly.vercel.app

## Features

- **AI Video Processing**: Upload and process videos for profanity detection
- **User Authentication**: Secure login/signup with Supabase Auth
- **API Key Management**: Generate and manage API keys with usage limits
- **Usage Analytics**: Track processing limits and subscription tiers
- **Responsive Dashboard**: Complete user interface for managing content

## Development

**Backend Setup:**
```bash
cd backend
pip install -r requirements.txt
python app.py
```

**Frontend Setup:**
```bash
cd frontend
npm install
npm run dev
```

## Environment Configuration

Create `.env` files with your production credentials (never commit to GitHub):

**Backend `.env`:**
```
SECRET_KEY=your_secret_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key
```

**Frontend `.env`:**
```
VITE_API_BASE_URL=https://ai-profanity-filter.onrender.com
```

## Deployment

- Backend: Auto-deployed to Render on push to main
- Frontend: Auto-deployed to Vercel on push to main

## License

Private Commercial Project

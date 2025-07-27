# 🚀 Deployment Guide

## Vercel Deployment

### Prerequisites
- GitHub repository
- Vercel account
- Razorpay account (for payments)

### Quick Deploy

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/kushagra88/ai-profanity-filter)

### Manual Deployment

1. **Install Vercel CLI**
```bash
npm install -g vercel
```

2. **Login to Vercel**
```bash
vercel login
```

3. **Deploy from project root**
```bash
vercel --prod
```

### Environment Variables

Set these in your Vercel dashboard:

```
RAZORPAY_KEY_ID=your_key_here
RAZORPAY_KEY_SECRET=your_secret_here
NODE_ENV=production
```

### Project Structure for Vercel

```
├── vercel.json         # Vercel configuration
├── frontend/           # Main application
│   ├── app.js         # Entry point
│   ├── package.json   # Dependencies
│   └── vercel.json    # Frontend config
└── backend/           # Python API (separate deployment)
```

### Backend Deployment

The Python backend should be deployed separately to a service like:
- Railway
- Heroku  
- DigitalOcean App Platform
- AWS Lambda

Update the frontend environment variables to point to your backend URL.

## Production Checklist

- [ ] Set environment variables in Vercel
- [ ] Configure custom domain
- [ ] Set up Razorpay webhooks
- [ ] Deploy backend API
- [ ] Test payment flow
- [ ] Monitor performance

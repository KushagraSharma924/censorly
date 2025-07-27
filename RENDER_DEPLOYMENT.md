# 🚀 Deploy Backend to Render

## Step-by-Step Render Deployment

### 1. Prerequisites
- ✅ GitHub repository with backend code
- ✅ Render account (free tier available)

### 2. Prepare Repository
Make sure these files exist in your `backend/` folder:
- ✅ `server.py` (main Flask app)
- ✅ `requirements.txt` (Python dependencies)
- ✅ `Procfile` (tells Render how to run your app)
- ✅ `runtime.txt` (Python version specification)
- ✅ `build.sh` (build script)

### 3. Deploy to Render

#### Option A: Deploy via GitHub (Recommended)

1. **Push to GitHub** (if not done already)
```bash
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

2. **Go to Render Dashboard**
   - Visit https://render.com
   - Sign up/Login with GitHub

3. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select your repository: `ai-profanity-filter`

4. **Configure Service Settings**
```
Name: moviecensorai-backend
Environment: Python 3
Region: Oregon (US West) or closest to you
Branch: main
Root Directory: backend
Build Command: ./build.sh
Start Command: python server.py
```

5. **Set Environment Variables**
```
FLASK_ENV=production
PYTHON_VERSION=3.11.9
```

6. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (5-10 minutes)
   - Your API will be live at: `https://moviecensorai-backend.onrender.com`

#### Option B: Deploy via Render CLI

1. **Install Render CLI**
```bash
npm install -g @render/cli
```

2. **Login to Render**
```bash
render login
```

3. **Deploy**
```bash
cd backend
render deploy
```

### 4. Test Your Deployment

Once deployed, test your API endpoints:

```bash
# Health check
curl https://your-app-name.onrender.com/health

# Get supported formats
curl https://your-app-name.onrender.com/formats
```

### 5. Update Frontend Configuration

Update your frontend to use the Render backend URL:

In `frontend/.env`:
```env
BACKEND_URL=https://your-app-name.onrender.com
```

In `frontend/public/js/main.js`, update the API base URL:
```javascript
const API_BASE_URL = 'https://your-app-name.onrender.com';
```

### 6. Custom Domain (Optional)

1. In Render dashboard → Settings → Custom Domains
2. Add your domain: `api.moviecensorai.com`
3. Configure DNS with your domain provider

## 📋 Render Configuration Files

### `backend/Procfile`
```
web: python server.py
```

### `backend/runtime.txt`
```
python-3.11.9
```

### `backend/build.sh`
```bash
#!/usr/bin/env bash
pip install -r requirements.txt
mkdir -p uploads outputs temp processed
```

## 🔧 Environment Variables for Production

Set these in Render dashboard:

| Variable | Value | Description |
|----------|-------|-------------|
| `FLASK_ENV` | `production` | Flask environment |
| `PYTHON_VERSION` | `3.11.9` | Python version |
| `PORT` | (auto-set) | Render sets this automatically |

## 🎯 Free Tier Limitations

Render free tier includes:
- ✅ 512MB RAM
- ✅ 1 vCPU
- ✅ Auto-sleep after 15min inactivity
- ✅ 750 hours/month (enough for development)

For production, consider upgrading to paid tier for:
- No auto-sleep
- More resources
- Faster builds

## 🐛 Troubleshooting

### Build Fails
- Check `requirements.txt` has all dependencies
- Ensure `build.sh` is executable
- Check Python version compatibility

### App Won't Start
- Verify `Procfile` syntax
- Check server.py uses `PORT` environment variable
- Review build logs in Render dashboard

### FFmpeg Issues
Render includes FFmpeg by default, but if you encounter issues:
```bash
# Add to build.sh
apt-get update && apt-get install -y ffmpeg
```

## 🚀 Ready for Production!

Once deployed:
1. ✅ Backend API running on Render
2. ✅ Frontend can connect to backend
3. ✅ File processing works
4. ✅ Health checks pass

Your MovieCensorAI backend is now live and scalable! 🎬

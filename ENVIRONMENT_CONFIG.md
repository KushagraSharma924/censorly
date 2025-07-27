# Environment Configuration Guide

## Switching Between Local and Deployed Backend

The MovieCensorAI frontend is now configured to use environment variables for the backend API URL, making it easy to switch between local development and production deployment.

### Configuration Files

- **`.env`** - Current environment configuration
- **`.env.example`** - Template with examples for both environments

### Backend URL Options

#### Local Development
```bash
BACKEND_URL=http://localhost:5000
```

#### Production (Deployed Backend)
```bash
BACKEND_URL=https://ai-profanity-filter.onrender.com
```

### How to Switch Environments

1. **For Local Development:**
   ```bash
   # Edit .env file
   BACKEND_URL=http://localhost:5000
   ```

2. **For Production:**
   ```bash
   # Edit .env file
   BACKEND_URL=https://ai-profanity-filter.onrender.com
   ```

3. **Restart the frontend server** after changing the environment variable:
   ```bash
   npm restart
   # or
   node app.js
   ```

### How It Works

1. **Server-side (app.js):**
   - Reads `BACKEND_URL` from environment variables
   - Uses it for backend API calls (health checks, video processing)

2. **Client-side (main.js):**
   - Fetches configuration from `/api/config` endpoint
   - Uses the backend URL for direct API calls from the browser

### Benefits

- **Easy switching** between environments
- **No code changes** required when deploying
- **Centralized configuration** management
- **Environment-specific settings** support

### Testing the Configuration

You can verify the current backend URL by visiting:
```
http://localhost:3000/api/config
```

This will return:
```json
{
  "backendUrl": "https://ai-profanity-filter.onrender.com"
}
```

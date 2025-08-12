# Censorly Backend Documentation

This document provides an overview of the Censorly backend, including its structure, API endpoints, and deployment instructions.

## Project Structure

```
backend/
├── app.py                   # Main Flask application
├── app_supabase.py          # Supabase integration
├── app_debug.py             # Lightweight debug app for troubleshooting
├── config.py                # Configuration settings
├── requirements.txt         # Full dependencies
├── requirements-minimal.txt  # Minimal dependencies
├── requirements-debug.txt   # Debug-only dependencies
├── Dockerfile               # Main Docker configuration
├── Dockerfile.debug         # Debug Docker configuration
├── start.sh                 # Start script for main app
├── start-debug.sh           # Start script for debug app
├── api/                     # API routes
│   ├── __init__.py
│   └── supabase_routes.py   # Supabase-related endpoints
├── decorators/              # Custom decorators
│   ├── __init__.py
│   ├── api_security.py      # API key security
│   └── rate_limiting.py     # Rate limiting implementation
├── models/                  # Data models
│   ├── __init__.py
│   └── data_models.py       # Database models
├── services/                # Business logic services
│   ├── __init__.py
│   ├── abuse_classifier.py  # Content moderation
│   ├── rate_limiter.py      # Rate limiting service
│   └── supabase_service.py  # Supabase integration service
└── utils/                   # Utility functions
    ├── __init__.py
    ├── audio_utils.py       # Audio processing utilities
    ├── censor_utils.py      # Censoring utilities
    ├── ffmpeg_tools.py      # FFmpeg integration
    └── security_utils.py    # Security utilities
```

## API Endpoints

### Authentication Endpoints

#### Register User
- **URL**: `/api/register`
- **Method**: `POST`
- **Description**: Registers a new user
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "secure_password",
    "name": "User Name"
  }
  ```
- **Response**: User information and authentication token

#### Login User
- **URL**: `/api/login`
- **Method**: `POST`
- **Description**: Authenticates a user
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "secure_password"
  }
  ```
- **Response**: User information and authentication token

### API Key Management

#### Generate API Key
- **URL**: `/api/generate-api-key`
- **Method**: `POST`
- **Description**: Generates a new API key for the authenticated user
- **Authentication**: Required
- **Response**: API key information

#### Verify API Key
- **URL**: `/api/verify-api-key`
- **Method**: `POST`
- **Description**: Verifies an API key
- **Request Body**:
  ```json
  {
    "api_key": "your_api_key"
  }
  ```
- **Response**: API key validity status

### Content Processing

#### Upload Video
- **URL**: `/api/upload-video`
- **Method**: `POST`
- **Description**: Uploads a video for processing
- **Authentication**: Required (API Key or JWT)
- **Content-Type**: `multipart/form-data`
- **Form Fields**:
  - `video`: Video file
  - `options`: JSON string with processing options
- **Response**: Processing job information

#### Check Processing Status
- **URL**: `/api/processing-status/<job_id>`
- **Method**: `GET`
- **Description**: Checks the status of a processing job
- **Authentication**: Required (API Key or JWT)
- **Response**: Current processing status

#### Get Processed Video
- **URL**: `/api/processed-video/<job_id>`
- **Method**: `GET`
- **Description**: Downloads the processed video
- **Authentication**: Required (API Key or JWT)
- **Response**: Processed video file

### User Management

#### Get User Profile
- **URL**: `/api/profile`
- **Method**: `GET`
- **Description**: Retrieves the user's profile information
- **Authentication**: Required
- **Response**: User profile information

#### Update User Profile
- **URL**: `/api/profile`
- **Method**: `PUT`
- **Description**: Updates the user's profile information
- **Authentication**: Required
- **Request Body**: Profile information to update
- **Response**: Updated user profile information

## Security Features

### API Key Authentication

The system uses secure API keys with the following security features:
- Constant-time comparison to prevent timing attacks
- Secure hashing with HMAC-SHA256
- API key rotation capabilities

Implementation in `decorators/api_security.py` and `utils/security_utils.py`.

### Rate Limiting

The system implements rate limiting to prevent abuse:
- Per-user and per-IP rate limiting
- Configurable limits and time windows
- Redis-backed storage for distributed deployments

Implementation in `decorators/rate_limiting.py` and `services/rate_limiter.py`.

## Deployment Instructions

### Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   ./start.sh
   ```

### Docker Deployment

1. Build the Docker image:
   ```bash
   docker build -t censorly-backend .
   ```

2. Run the container:
   ```bash
   docker run -p 5000:5000 censorly-backend
   ```

### Debug Mode Deployment

For troubleshooting deployment issues:

1. Install minimal dependencies:
   ```bash
   pip install -r requirements-debug.txt
   ```

2. Run the debug application:
   ```bash
   ./start-debug.sh
   ```

3. Or use Docker:
   ```bash
   docker build -t censorly-debug -f Dockerfile.debug .
   docker run -p 8000:8000 censorly-debug
   ```

### Docker Compose

You can also use Docker Compose to run both the main and debug applications:

```bash
docker-compose up
```

### Deployment to Render

1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Use the following settings:
   - Build Command: `cd backend && pip install -r requirements.txt`
   - Start Command: `cd backend && gunicorn --bind 0.0.0.0:$PORT app:app`
   - Environment Variables:
     - `FLASK_ENV=production`
     - Add your Supabase credentials

4. For troubleshooting deployment issues, you can use the debug version:
   - Build Command: `cd backend && pip install -r requirements-debug.txt`
   - Start Command: `cd backend && gunicorn --bind 0.0.0.0:$PORT app_debug:app`

## Troubleshooting

### CORS Issues

If you're experiencing CORS issues:
- Ensure the frontend URL is added to the CORS_ORIGINS list in the appropriate app configuration
- Check that credentials are properly handled with `supports_credentials=True`
- Verify that the frontend is using the correct credentials setting in fetch requests

### Render Deployment Timeouts

If you're experiencing timeouts during deployment:
- Try using the debug version with minimal dependencies
- Check that all external service connections have appropriate timeouts
- Ensure that initialization code doesn't block the application startup

### API Key Issues

If API key authentication is not working:
- Verify that the API key is being sent in the Authorization header with the 'ApiKey ' prefix
- Check that the API key exists and is active in the database
- Ensure the constant-time comparison function is being used for verification

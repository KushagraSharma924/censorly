# MovieCensorAI Frontend - Next.js

A modern Next.js frontend application for MovieCensorAI - AI-powered video profanity filter.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Installation

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env.local
   ```
   Edit `.env.local` with your actual values.

3. **Run development server**
   ```bash
   npm run dev
   ```

4. **Open your browser**
   Navigate to [http://localhost:3000](http://localhost:3000)

## 📝 Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## 🏗️ Project Structure

```
frontend/
├── pages/
│   ├── api/           # API routes
│   ├── _app.js        # App component
│   └── index.js       # Home page
├── public/
│   ├── processed/     # Processed videos
│   └── static/        # Static assets
├── uploads/           # Temporary uploads
├── next.config.js     # Next.js configuration
└── package.json       # Dependencies
```

## 🌐 API Endpoints

- `POST /api/upload` - Upload and process video
- `GET /api/health` - Health check
- `GET /api/pricing` - Get pricing plans
- `POST /api/create-order` - Create payment order
- `POST /api/verify-payment` - Verify payment

## 🎯 Features

- **Modern React UI** - Built with Next.js and Tailwind CSS
- **File Upload** - Drag & drop video upload with validation
- **Real-time Processing** - AI-powered video processing
- **Payment Integration** - Razorpay payment gateway
- **Responsive Design** - Mobile-first responsive layout
- **API Routes** - Server-side API endpoints

## 🔧 Configuration

### Environment Variables

```bash
# Backend URL
BACKEND_URL=http://localhost:5000

# Razorpay Configuration
RAZORPAY_KEY_ID=your_razorpay_key
RAZORPAY_KEY_SECRET=your_razorpay_secret
```

### Next.js Configuration

The `next.config.js` file includes:
- Environment variable mapping
- Static file routing
- Server actions configuration

## 🚀 Deployment

### Vercel (Recommended)

1. **Connect repository** to Vercel
2. **Set environment variables** in Vercel dashboard
3. **Deploy** automatically on push

### Manual Deployment

1. **Build application**
   ```bash
   npm run build
   ```

2. **Start production server**
   ```bash
   npm start
   ```

## 🔗 Backend Integration

This frontend connects to the Python Flask backend for video processing:
- Default: `http://localhost:5000`
- Production: `https://ai-profanity-filter.onrender.com`

## 📱 Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 🛠️ Technology Stack

- **Framework**: Next.js 14
- **UI**: React 18, Tailwind CSS
- **File Upload**: Multer, FormData
- **HTTP Client**: Axios
- **Payment**: Razorpay
- **Deployment**: Vercel

## 🐛 Troubleshooting

### Common Issues

1. **Upload fails**: Check backend URL and ensure Flask server is running
2. **Payment errors**: Verify Razorpay credentials
3. **Build errors**: Check Node.js version (18+ required)

### Development

- Ensure backend is running on port 5000
- Check browser console for client-side errors
- Verify API endpoints are accessible

## 📄 License

MIT License - see LICENSE file for details.

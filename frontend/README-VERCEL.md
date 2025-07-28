# CleanCast AI Frontend

A modern, dark-themed AI-powered video content moderation platform built with Next.js and Tailwind CSS.

## 🚀 Vercel Deployment

### One-Click Deploy

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/your-username/ai-profanity-filter&project-name=cleancast-ai&repository-name=ai-profanity-filter&env=BACKEND_URL,RAZORPAY_KEY_ID,RAZORPAY_KEY_SECRET&envDescription=Required%20environment%20variables)

### Manual Deployment

1. **Fork/Clone the repository**
2. **Connect to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Import your GitHub repository
   - Select the `frontend` folder as the project root

3. **Set Environment Variables**
   ```bash
   BACKEND_URL=https://your-backend-url.com
   RAZORPAY_KEY_ID=your_razorpay_key_id
   RAZORPAY_KEY_SECRET=your_razorpay_key_secret
   ```

4. **Deploy**
   - Vercel will automatically build and deploy your application

## 🛠️ Local Development

### Prerequisites

- Node.js 18+ 
- npm/yarn/pnpm

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/ai-profanity-filter.git
cd ai-profanity-filter/frontend

# Install dependencies
npm install

# Copy environment variables
cp .env.example .env.local

# Edit .env.local with your actual values
# BACKEND_URL=http://localhost:5000
# RAZORPAY_KEY_ID=your_key
# RAZORPAY_KEY_SECRET=your_secret

# Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## 🏗️ Build & Deploy

```bash
# Build for production
npm run build

# Start production server
npm start

# Type checking
npm run type-check

# Linting
npm run lint
```

## 📁 Project Structure

```
frontend/
├── pages/
│   ├── api/          # API routes
│   ├── _app.tsx      # App component
│   ├── _document.tsx # Document component
│   └── index.tsx     # Home page
├── public/           # Static assets
├── styles/           # Global styles
├── vercel.json       # Vercel configuration
└── next.config.js    # Next.js configuration
```

## 🎨 Features

- **Dark Theme**: Modern Gen Z-friendly design
- **Glassmorphism UI**: Backdrop blur effects and transparency
- **API Integration**: Dynamic pricing and health monitoring
- **Real-time Status**: System health indicators
- **Responsive Design**: Mobile-first approach
- **Type Safety**: Full TypeScript implementation

## 🔧 Configuration

### Vercel Environment Variables

Set these in your Vercel dashboard under Settings > Environment Variables:

- `BACKEND_URL` - Your backend API URL
- `RAZORPAY_KEY_ID` - Razorpay public key
- `RAZORPAY_KEY_SECRET` - Razorpay secret key

### API Routes

- `/api/pricing` - Fetch pricing plans
- `/api/health` - System health check
- `/api/upload` - Video upload and processing
- `/api/create-order` - Razorpay order creation
- `/api/verify-payment` - Payment verification

## 🚀 Performance

- **Lighthouse Score**: 90+ 
- **Core Web Vitals**: Optimized
- **Bundle Size**: Minimized with tree shaking
- **Loading**: Lazy loading and code splitting

## 📱 Browser Support

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## 🔒 Security

- Environment variables for sensitive data
- CORS headers configured
- Input validation on all forms
- Secure API communication

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

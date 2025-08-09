# Frontend Deployment Guide

## Quick Start
The fastest way to deploy the frontend is using Vercel:

1. **Fork/Clone the repository**
2. **Go to [vercel.com](https://vercel.com) and sign in with GitHub**
3. **Click "Add New" → "Project"**
4. **Import your repository**
5. **Configure settings:**
   - Root Directory: `frontend`
   - Framework: Vite
   - Build Command: `npm run build`
   - Output Directory: `dist`
6. **Set environment variable:**
   - `VITE_API_BASE_URL`: `https://ai-profanity-filter-production.onrender.com`
7. **Deploy!**

## Deployment Options

### 1. Vercel (Recommended) ⭐
**Best for:** Production deployments, automatic previews, custom domains

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy from frontend directory
cd frontend
vercel --prod
```

**Advantages:**
- Automatic deployments on git push
- Free SSL certificates
- Global CDN
- Preview deployments for PRs
- Built-in analytics

### 2. Netlify
**Best for:** Static sites, form handling, edge functions

```bash
# Install Netlify CLI
npm i -g netlify-cli

# Deploy from frontend directory
cd frontend
npm run build
netlify deploy --prod --dir=dist
```

### 3. GitHub Pages
**Best for:** Open source projects, documentation sites

```bash
# Build and deploy
npm run build
npm i -g gh-pages
gh-pages -d dist
```

### 4. Self-hosted (Docker)
**Best for:** Custom infrastructure, full control

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Environment Variables

Set these in your deployment platform:

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Backend API URL | `https://your-backend.onrender.com` |
| `VITE_GA_TRACKING_ID` | Google Analytics | `G-XXXXXXXXXX` |
| `VITE_SENTRY_DSN` | Error tracking | `https://xxx@sentry.io/xxx` |

## Build Commands

```bash
# Development
npm run dev              # Start dev server on http://localhost:3000

# Production
npm run build            # Build for production
npm run preview          # Preview production build locally

# Quality
npm run lint             # Run ESLint
npm run type-check       # TypeScript type checking
```

## Performance Optimization

### Bundle Analysis
```bash
npm run build
npx vite-bundle-analyzer dist
```

### Code Splitting
The app automatically splits code by routes. Large components should be lazy-loaded:

```typescript
const HeavyComponent = lazy(() => import('./HeavyComponent'));
```

### Image Optimization
- Use WebP format when possible
- Implement lazy loading for images
- Compress images before deployment

## CI/CD Setup

### GitHub Actions (Vercel)
The repository includes a GitHub Actions workflow (`.github/workflows/deploy-frontend.yml`) that automatically deploys to Vercel on push to main.

**Required Secrets:**
- `VERCEL_TOKEN`: Your Vercel API token
- `VERCEL_ORG_ID`: Organization ID from Vercel
- `VERCEL_PROJECT_ID`: Project ID from Vercel
- `VITE_API_BASE_URL`: Production API URL

### Manual Deployment Script
Use the included deployment script:

```bash
cd frontend
chmod +x deploy.sh
./deploy.sh
```

## Domain Configuration

### Custom Domain (Vercel)
1. Go to Vercel Dashboard → Settings → Domains
2. Add your domain (e.g., `app.yoursite.com`)
3. Configure DNS records as shown

### SSL Certificate
SSL is automatically handled by Vercel, Netlify, and other modern platforms.

## Monitoring & Analytics

### Built-in Analytics
- **Vercel**: Built-in Web Vitals and analytics
- **Netlify**: Site analytics available in dashboard
- **Google Analytics**: Add tracking ID to environment variables

### Error Tracking
Consider adding Sentry for error tracking:

```bash
npm install @sentry/react @sentry/tracing
```

## Troubleshooting

### Common Issues

**Build Failures:**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check for TypeScript errors
npm run type-check
```

**API Connection Issues:**
- Verify `VITE_API_BASE_URL` is set correctly
- Check backend CORS configuration
- Test API endpoints manually

**Performance Issues:**
- Analyze bundle size: `npm run build`
- Check for large dependencies
- Implement code splitting

### Debug Mode
```bash
# Build with source maps for debugging
npm run build -- --mode development
```

## Security Considerations

- Never commit API keys or secrets
- Use environment variables for configuration
- Enable HTTPS (automatic with Vercel/Netlify)
- Implement Content Security Policy
- Regular dependency updates: `npm audit fix`

## Scaling Considerations

- Use CDN for static assets
- Implement caching strategies
- Consider server-side rendering (SSR) with Next.js for better SEO
- Monitor Core Web Vitals

## Support

For deployment issues:
1. Check the deployment logs in your platform dashboard
2. Verify environment variables are set correctly
3. Test the build locally: `npm run build && npm run preview`
4. Check API connectivity from the deployed URL

## Links

- [Vercel Documentation](https://vercel.com/docs)
- [Netlify Documentation](https://docs.netlify.com)
- [Vite Deployment Guide](https://vitejs.dev/guide/static-deploy.html)
- [React Deployment Guide](https://create-react-app.dev/docs/deployment/)

# Vercel Deployment Checklist ✅

## Pre-Deployment Setup

### 1. Environment Variables
Set these in your Vercel dashboard:

- [ ] `BACKEND_URL` - Your backend API URL (e.g., https://your-backend.onrender.com)
- [ ] `RAZORPAY_KEY_ID` - Your Razorpay public key
- [ ] `RAZORPAY_KEY_SECRET` - Your Razorpay secret key

### 2. Repository Setup
- [ ] Push code to GitHub repository
- [ ] Ensure `frontend` folder contains all necessary files
- [ ] Remove any sensitive data from code

### 3. Build Verification
- [ ] ✅ Build passes (`npm run build`)
- [ ] ✅ TypeScript compilation successful
- [ ] ✅ ESLint passes with no errors
- [ ] ✅ All API routes properly configured

## Deployment Steps

### Option 1: One-Click Deploy
1. Click the "Deploy with Vercel" button in README
2. Connect your GitHub account
3. Set environment variables
4. Deploy!

### Option 2: Manual Deploy
1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import your GitHub repository
4. Set **Root Directory** to `frontend`
5. Configure environment variables
6. Deploy

## Post-Deployment

### 1. Test Functionality
- [ ] Homepage loads correctly
- [ ] Dark theme applied properly
- [ ] Pricing data loads from API
- [ ] Health status indicators work
- [ ] Upload modal functions
- [ ] Mobile responsiveness

### 2. Performance Check
- [ ] Run Lighthouse audit (target: 90+ score)
- [ ] Check Core Web Vitals
- [ ] Verify fast loading times

### 3. API Integration
- [ ] Backend connectivity working
- [ ] Pricing API returns data
- [ ] Health API responds (may show degraded if backend down)
- [ ] Upload functionality works

## Common Issues & Solutions

### Build Failures
- **Issue**: Page without valid React component
- **Solution**: Remove unused files (like `index_new.tsx`)

### Environment Variables Not Working
- **Issue**: Variables not loading in production
- **Solution**: Set in Vercel dashboard, not in code

### API Calls Failing
- **Issue**: CORS or network errors
- **Solution**: Check BACKEND_URL and ensure backend allows requests

### Styling Issues
- **Issue**: Tailwind classes not applied
- **Solution**: Verify `tailwind.config.js` and `postcss.config.js`

## Vercel Configuration Files

### ✅ Files Created/Updated:
- `vercel.json` - Deployment configuration
- `next.config.js` - Next.js optimizations
- `_document.tsx` - External resources (fonts, scripts)
- `package.json` - Updated metadata and scripts
- `.env.example` - Environment variable template

### ✅ Optimizations Applied:
- SWC minification enabled
- React strict mode enabled
- CORS headers configured
- Build optimization settings
- TypeScript strict checking

## Success Indicators
- ✅ Green build status in Vercel dashboard
- ✅ Website loads at your `.vercel.app` domain
- ✅ All features work as expected
- ✅ No console errors in browser
- ✅ Mobile and desktop responsive

## Support
If you encounter issues:
1. Check Vercel build logs
2. Verify environment variables
3. Test locally with `npm run build`
4. Check browser console for errors

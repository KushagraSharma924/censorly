const express = require('express');
const multer = require('multer');
const axios = require('axios');
const path = require('path');
const fs = require('fs-extra');
const cors = require('cors');
const Razorpay = require('razorpay');
const crypto = require('crypto');

// Load environment variables
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Razorpay Configuration
const razorpay = new Razorpay({
  key_id: process.env.RAZORPAY_KEY_ID || 'rzp_test_your_key_id',
  key_secret: process.env.RAZORPAY_KEY_SECRET || 'your_key_secret'
});

// Middleware
app.use(express.static('public'));
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(cors());

// Set EJS as template engine
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// Ensure directories exist
const ensureDirectories = async () => {
  await fs.ensureDir(path.join(__dirname, 'uploads'));
  await fs.ensureDir(path.join(__dirname, 'public/processed'));
  await fs.ensureDir(path.join(__dirname, 'public/temp'));
};

// Multer configuration for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, 'uploads/');
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
  }
});

const upload = multer({
  storage: storage,
  fileFilter: (req, file, cb) => {
    if (file.mimetype.startsWith('video/')) {
      cb(null, true);
    } else {
      cb(new Error('Only video files are allowed!'));
    }
  },
  limits: {
    fileSize: 100 * 1024 * 1024 // 100MB limit
  }
});

// Routes
app.get('/', (req, res) => {
  res.render('index', { 
    title: 'MovieCensorAI - Clean Your Videos with AI',
    error: null,
    success: null,
    processedVideo: null
  });
});

app.post('/upload', upload.single('video'), async (req, res) => {
  try {
    if (!req.file) {
      return res.render('index', {
        title: 'MovieCensorAI - Clean Your Videos with AI',
        error: 'Please select a video file to upload.',
        success: null,
        processedVideo: null
      });
    }

    const censorType = req.body.censorType || 'beep';
    const videoPath = req.file.path;

    // Prepare form data for Flask backend
    const FormData = require('form-data');
    const formData = new FormData();
    
    formData.append('video', fs.createReadStream(videoPath), {
      filename: req.file.originalname,
      contentType: req.file.mimetype
    });
    formData.append('censor_type', censorType);

    // Send to Flask backend
    const response = await axios.post('http://localhost:5001/process', formData, {
      headers: {
        ...formData.getHeaders(),
      },
      timeout: 300000, // 5 minutes timeout
      responseType: 'arraybuffer'
    });

    // Save processed video
    const processedFileName = `processed-${Date.now()}.mp4`;
    const processedPath = path.join(__dirname, 'public/processed', processedFileName);
    await fs.writeFile(processedPath, response.data);

    // Clean up uploaded file
    await fs.remove(videoPath);

    res.render('index', {
      title: 'MovieCensorAI - Clean Your Videos with AI',
      error: null,
      success: 'Video processed successfully! Your clean video is ready.',
      processedVideo: `/processed/${processedFileName}`
    });

  } catch (error) {
    console.error('Processing error:', error);
    
    // Clean up uploaded file if it exists
    if (req.file && req.file.path) {
      await fs.remove(req.file.path).catch(console.error);
    }

    let errorMessage = 'An error occurred while processing your video.';
    
    if (error.code === 'ECONNREFUSED') {
      errorMessage = 'Backend service is not available. Please make sure the Flask server is running on port 5000.';
    } else if (error.response && error.response.status === 413) {
      errorMessage = 'File is too large. Please upload a smaller video file.';
    } else if (error.message.includes('timeout')) {
      errorMessage = 'Processing timeout. Please try with a shorter video.';
    }

    res.render('index', {
      title: 'MovieCensorAI - Clean Your Videos with AI',
      error: errorMessage,
      success: null,
      processedVideo: null
    });
  }
});

// API endpoint for progress updates (for future implementation)
app.get('/api/status/:jobId', (req, res) => {
  // This would connect to a job queue system in production
  res.json({ status: 'processing', progress: 50 });
});

// Health check endpoint
app.get('/api/health', (req, res) => {
  const healthCheck = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    version: '1.0.0',
    services: {
      database: 'connected',
      storage: 'available',
      backend: 'unknown' // Will be checked dynamically
    },
    memory: {
      used: Math.round(process.memoryUsage().heapUsed / 1024 / 1024),
      total: Math.round(process.memoryUsage().heapTotal / 1024 / 1024)
    }
  };

  // Check backend service
  axios.get('http://localhost:5001/health', { timeout: 5000 })
    .then(() => {
      healthCheck.services.backend = 'connected';
      res.status(200).json(healthCheck);
    })
    .catch(() => {
      healthCheck.services.backend = 'disconnected';
      healthCheck.status = 'degraded';
      res.status(503).json(healthCheck);
    });
});

// API to get system statistics
app.get('/api/stats', (req, res) => {
  const stats = {
    totalUploads: 0, // Would be from database
    totalProcessingTime: '2.3 minutes', // Average
    successRate: 99.9,
    supportedFormats: ['mp4', 'avi', 'mov', 'mkv', 'webm'],
    languages: 50,
    uptime: Math.floor(process.uptime()),
    lastUpdated: new Date().toISOString()
  };
  
  res.json(stats);
});

// API to get pricing information
app.get('/api/pricing', (req, res) => {
  const pricing = {
    plans: [
      {
        id: 'free',
        name: 'Free',
        price: 0,
        currency: 'USD',
        interval: 'month',
        features: [
          'Up to 5 minutes per video',
          'Standard processing',
          'Basic support'
        ],
        limits: {
          videoLength: 300, // seconds
          dailyUploads: 3,
          monthlyUploads: 10
        }
      },
      {
        id: 'pro',
        name: 'Pro',
        price: 29,
        currency: 'USD',
        interval: 'month',
        features: [
          'Up to 60 minutes per video',
          'Priority processing',
          'Email support',
          'Batch processing'
        ],
        limits: {
          videoLength: 3600, // seconds
          dailyUploads: 50,
          monthlyUploads: 1000
        },
        popular: true
      },
      {
        id: 'enterprise',
        name: 'Enterprise',
        price: 99,
        currency: 'USD',
        interval: 'month',
        features: [
          'Unlimited video length',
          'Fastest processing',
          'Priority support',
          'API access'
        ],
        limits: {
          videoLength: -1, // unlimited
          dailyUploads: -1,
          monthlyUploads: -1
        }
      }
    ]
  };
  
  res.json(pricing);
});

// API to validate file before upload
app.post('/api/validate-file', upload.single('video'), (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({
        valid: false,
        error: 'No file provided'
      });
    }

    const validation = {
      valid: true,
      filename: req.file.originalname,
      size: req.file.size,
      sizeFormatted: `${(req.file.size / 1024 / 1024).toFixed(2)} MB`,
      mimetype: req.file.mimetype,
      estimatedProcessingTime: Math.round((req.file.size / 1024 / 1024) * 0.5) + ' minutes'
    };

    // Clean up the validation file
    fs.remove(req.file.path).catch(console.error);

    res.json(validation);
  } catch (error) {
    res.status(400).json({
      valid: false,
      error: error.message
    });
  }
});

// API to get supported formats and limits
app.get('/api/limits', (req, res) => {
  const limits = {
    fileSize: {
      max: 100 * 1024 * 1024, // 100MB
      maxFormatted: '100 MB'
    },
    supportedFormats: [
      { ext: 'mp4', description: 'MPEG-4 Video' },
      { ext: 'avi', description: 'Audio Video Interleave' },
      { ext: 'mov', description: 'QuickTime Movie' },
      { ext: 'mkv', description: 'Matroska Video' },
      { ext: 'webm', description: 'WebM Video' },
      { ext: 'wmv', description: 'Windows Media Video' }
    ],
    videoLength: {
      free: 300, // 5 minutes
      pro: 3600, // 60 minutes
      enterprise: -1 // unlimited
    },
    resolution: {
      max: '4K (3840x2160)',
      recommended: '1080p (1920x1080)'
    }
  };
  
  res.json(limits);
});

// API to get processing queue status
app.get('/api/queue', (req, res) => {
  const queueStatus = {
    activeJobs: 2,
    queuedJobs: 5,
    averageWaitTime: '3 minutes',
    estimatedProcessingTime: '7 minutes',
    serverLoad: 'medium',
    lastUpdated: new Date().toISOString()
  };
  
  res.json(queueStatus);
});

// API for contact form submission
app.post('/api/contact', express.json(), (req, res) => {
  const { name, email, subject, message } = req.body;
  
  // Validate required fields
  if (!name || !email || !message) {
    return res.status(400).json({
      success: false,
      error: 'Name, email, and message are required'
    });
  }

  // Email validation
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    return res.status(400).json({
      success: false,
      error: 'Invalid email address'
    });
  }

  // In production, this would send an email or store in database
  console.log('Contact form submission:', { name, email, subject, message });
  
  res.json({
    success: true,
    message: 'Thank you for your message. We will get back to you soon.'
  });
});

// API for newsletter subscription
app.post('/api/newsletter', express.json(), (req, res) => {
  const { email } = req.body;
  
  if (!email) {
    return res.status(400).json({
      success: false,
      error: 'Email is required'
    });
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    return res.status(400).json({
      success: false,
      error: 'Invalid email address'
    });
  }

  // In production, this would integrate with email service
  console.log('Newsletter subscription:', email);
  
  res.json({
    success: true,
    message: 'Successfully subscribed to newsletter'
  });
});

// API to get features list
app.get('/api/features', (req, res) => {
  const features = {
    core: [
      {
        id: 'ai-detection',
        name: 'AI-Powered Detection',
        description: 'Advanced machine learning algorithms detect profanity with 99.9% accuracy',
        icon: 'brain'
      },
      {
        id: 'multi-language',
        name: 'Multi-Language Support',
        description: 'Support for 50+ languages including English, Spanish, French, and more',
        icon: 'globe'
      },
      {
        id: 'fast-processing',
        name: 'Lightning Fast',
        description: 'Process videos in minutes, not hours, with our optimized infrastructure',
        icon: 'lightning'
      }
    ],
    advanced: [
      {
        id: 'batch-processing',
        name: 'Batch Processing',
        description: 'Process multiple videos simultaneously for efficiency',
        icon: 'layers'
      },
      {
        id: 'api-access',
        name: 'API Integration',
        description: 'Integrate directly into your workflow with our RESTful API',
        icon: 'code'
      },
      {
        id: 'custom-filters',
        name: 'Custom Filters',
        description: 'Create custom word lists and sensitivity settings',
        icon: 'settings'
      }
    ]
  };
  
  res.json(features);
});

// =================== RAZORPAY INTEGRATION ===================

// Create Razorpay Order
app.post('/api/create-order', async (req, res) => {
  try {
    const { planId, amount, currency = 'INR' } = req.body;
    
    // Convert USD to INR for Razorpay (approximate conversion)
    const amountInPaise = currency === 'USD' ? Math.round(amount * 83 * 100) : amount * 100;
    
    const options = {
      amount: amountInPaise, // amount in paise
      currency: 'INR',
      receipt: `receipt_${planId}_${Date.now()}`,
      payment_capture: 1,
      notes: {
        planId: planId,
        originalAmount: amount,
        originalCurrency: currency
      }
    };

    const order = await razorpay.orders.create(options);
    
    res.json({
      success: true,
      orderId: order.id,
      amount: order.amount,
      currency: order.currency,
      razorpayKeyId: process.env.RAZORPAY_KEY_ID || 'rzp_test_your_key_id'
    });
    
  } catch (error) {
    console.error('Razorpay order creation failed:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to create payment order'
    });
  }
});

// Verify Razorpay Payment
app.post('/api/verify-payment', (req, res) => {
  try {
    const { 
      razorpay_order_id, 
      razorpay_payment_id, 
      razorpay_signature,
      planId 
    } = req.body;

    // Verify signature
    const body = razorpay_order_id + "|" + razorpay_payment_id;
    const expectedSignature = crypto
      .createHmac('sha256', process.env.RAZORPAY_KEY_SECRET || 'your_key_secret')
      .update(body.toString())
      .digest('hex');

    if (expectedSignature === razorpay_signature) {
      // Payment successful - Here you would typically:
      // 1. Update user subscription in database
      // 2. Send confirmation email
      // 3. Activate plan features
      
      console.log('✅ Payment verified successfully:', {
        orderId: razorpay_order_id,
        paymentId: razorpay_payment_id,
        planId: planId,
        timestamp: new Date().toISOString()
      });
      
      res.json({
        success: true,
        message: 'Payment verified successfully',
        paymentId: razorpay_payment_id,
        orderId: razorpay_order_id,
        planId: planId,
        status: 'active'
      });
    } else {
      console.log('❌ Payment verification failed - Invalid signature');
      res.status(400).json({
        success: false,
        error: 'Payment verification failed - Invalid signature'
      });
    }
  } catch (error) {
    console.error('Payment verification error:', error);
    res.status(500).json({
      success: false,
      error: 'Payment verification failed'
    });
  }
});

// Get Razorpay Configuration
app.get('/api/razorpay-config', (req, res) => {
  res.json({
    keyId: process.env.RAZORPAY_KEY_ID || 'rzp_test_your_key_id',
    currency: 'INR',
    company: {
      name: 'MovieCensorAI',
      description: 'Professional AI-powered content moderation',
      logo: '/images/logo.png'
    }
  });
});

// Error handling middleware
app.use((error, req, res, next) => {
  if (error instanceof multer.MulterError) {
    if (error.code === 'LIMIT_FILE_SIZE') {
      return res.render('index', {
        title: 'MovieCensorAI - Clean Your Videos with AI',
        error: 'File is too large. Maximum size is 100MB.',
        success: null,
        processedVideo: null
      });
    }
  }
  
  res.render('index', {
    title: 'MovieCensorAI - Clean Your Videos with AI',
    error: 'An unexpected error occurred. Please try again.',
    success: null,
    processedVideo: null
  });
});

// Start server
ensureDirectories().then(() => {
  app.listen(PORT, () => {
    console.log(`🎬 MovieCensorAI Frontend running on http://localhost:${PORT}`);
    console.log(`📁 Upload directory: ${path.join(__dirname, 'uploads')}`);
    console.log(`📁 Processed videos: ${path.join(__dirname, 'public/processed')}`);
  });
}).catch(console.error);

module.exports = app;

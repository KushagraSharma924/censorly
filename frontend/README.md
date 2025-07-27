# MovieCensorAI Frontend

A premium Node.js + Express frontend web application for MovieCensorAI - an AI-powered video profanity filter.

## 🚀 Features

- **Premium UI Design**: Clean, modern interface inspired by premium SaaS applications
- **Drag & Drop Upload**: Intuitive file upload with validation
- **Real-time Processing**: Shows progress and status updates
- **Multiple Censor Options**: Choose between beep sounds or muting
- **Video Preview**: Preview processed videos before download
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Pricing Plans**: Ready-to-integrate subscription tiers
- **Buy Me a Coffee**: Support widget for donations

## 🛠 Tech Stack

- **Backend**: Node.js + Express
- **Templating**: EJS
- **Styling**: Tailwind CSS
- **File Upload**: Multer
- **HTTP Client**: Axios
- **Icons**: Font Awesome
- **Fonts**: Google Fonts (Inter)

## 📁 Project Structure

```
frontend/
├── app.js                 # Main Express server
├── package.json          # Dependencies and scripts
├── public/               # Static assets
│   ├── css/
│   │   └── style.css     # Custom styles
│   ├── js/
│   │   └── main.js       # Client-side JavaScript
│   └── processed/        # Processed videos (auto-created)
├── views/
│   └── index.ejs         # Main template
├── uploads/              # Temporary uploads (auto-created)
└── README.md            # This file
```

## 🚀 Quick Start

1. **Install Dependencies**:
   ```bash
   npm install
   ```

2. **Start the Application**:
   ```bash
   npm start
   ```
   Or for development with auto-reload:
   ```bash
   npm run dev
   ```

3. **Access the Application**:
   Open http://localhost:3000 in your browser

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
PORT=3000
FLASK_BACKEND_URL=http://localhost:5000
MAX_FILE_SIZE=104857600
```

### Backend Integration

The frontend expects a Flask backend running on `http://localhost:5000/process` that accepts:

**Request**:
- Method: `POST`
- Content-Type: `multipart/form-data`
- Fields:
  - `video`: Video file
  - `censor_type`: "beep" or "mute"

**Response**:
- Content-Type: `video/mp4`
- Body: Processed video file

## 🎨 Customization

### Styling

- Modify `public/css/style.css` for custom styles
- Update Tailwind config in `views/index.ejs` for theme changes
- Change colors in the Tailwind config section

### Branding

- Update logo and text in `views/index.ejs`
- Modify pricing plans in the pricing section
- Update Buy Me a Coffee URL

### Features

- Add new pages by creating EJS templates
- Extend API endpoints in `app.js`
- Add new client-side features in `public/js/main.js`

## 📱 Responsive Design

The application is fully responsive and includes:

- Mobile-optimized layouts
- Touch-friendly interactions
- Adaptive typography
- Flexible grid systems

## 🔒 Security Features

- File type validation
- File size limits
- Input sanitization
- CORS protection
- Error handling

## 🚀 Deployment

### Local Development

```bash
npm run dev
```

### Production

```bash
npm start
```

### Deploy to Vercel

1. Install Vercel CLI: `npm i -g vercel`
2. Run: `vercel`
3. Follow the prompts

### Deploy to Render

1. Connect your GitHub repository
2. Set build command: `npm install`
3. Set start command: `npm start`

## 🔧 API Endpoints

### Frontend Routes

- `GET /` - Main landing page
- `POST /upload` - Process video upload
- `GET /api/status/:jobId` - Check processing status (future feature)

### Static Files

- `/css/*` - Stylesheets
- `/js/*` - JavaScript files
- `/processed/*` - Processed videos for download

## 🎯 Future Enhancements

- [ ] User authentication system
- [ ] Payment integration (Stripe/Razorpay)
- [ ] Real-time progress tracking with WebSockets
- [ ] Video compression before processing
- [ ] Batch processing for multiple files
- [ ] Advanced profanity filter settings
- [ ] Video preview with timestamps
- [ ] Download history and cloud storage
- [ ] API for developers
- [ ] Analytics dashboard

## 🐛 Troubleshooting

### Common Issues

1. **Backend Connection Error**:
   - Ensure Flask backend is running on port 5000
   - Check the backend URL in the code

2. **File Upload Fails**:
   - Check file size limits
   - Verify file format is supported
   - Ensure uploads directory has write permissions

3. **Processing Timeout**:
   - Increase timeout in axios configuration
   - Check backend processing capacity

### Error Handling

The application includes comprehensive error handling for:
- Network connectivity issues
- File validation errors
- Backend processing errors
- Timeout scenarios

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

For support, please contact us through:
- GitHub Issues
- Email support (coming soon)
- Buy Me a Coffee for donations

---

**Built with ❤️ for clean content creation**

import multer from 'multer';
import axios from 'axios';
import fs from 'fs-extra';
import path from 'path';
import FormData from 'form-data';
import type { NextApiRequest, NextApiResponse } from 'next';

interface ExtendedNextApiRequest extends NextApiRequest {
  file?: Express.Multer.File;
}

interface UploadResponse {
  success: boolean;
  message?: string;
  processedVideo?: string;
  error?: string;
}

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const uploadDir = path.join(process.cwd(), 'uploads');
    fs.ensureDirSync(uploadDir);
    cb(null, uploadDir);
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

// Helper function to run middleware
function runMiddleware(
  req: ExtendedNextApiRequest,
  res: NextApiResponse,
  fn: Function
): Promise<any> {
  return new Promise((resolve, reject) => {
    fn(req, res, (result: any) => {
      if (result instanceof Error) {
        return reject(result);
      }
      return resolve(result);
    });
  });
}

export default async function handler(
  req: ExtendedNextApiRequest,
  res: NextApiResponse<UploadResponse>
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ success: false, error: 'Method not allowed' });
  }

  try {
    // Run the multer middleware
    await runMiddleware(req, res, upload.single('video'));

    if (!req.file) {
      return res.status(400).json({
        success: false,
        error: 'Please select a video file to upload.'
      });
    }

    const censorType = req.body.censorType || 'beep';
    const videoPath = req.file.path;
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:5000';

    // Prepare form data for Flask backend
    const formData = new FormData();
    formData.append('video', fs.createReadStream(videoPath), {
      filename: req.file.originalname,
      contentType: req.file.mimetype
    });
    formData.append('censor_type', censorType);

    // Send to Flask backend
    const response = await axios.post(`${backendUrl}/process`, formData, {
      headers: {
        ...formData.getHeaders(),
      },
      timeout: 300000, // 5 minutes timeout
      responseType: 'arraybuffer'
    });

    // Save processed video
    const processedFileName = `processed-${Date.now()}.mp4`;
    const publicDir = path.join(process.cwd(), 'public', 'processed');
    await fs.ensureDir(publicDir);
    const processedPath = path.join(publicDir, processedFileName);
    await fs.writeFile(processedPath, response.data);

    // Clean up uploaded file
    await fs.remove(videoPath);

    res.status(200).json({
      success: true,
      message: 'Video processed successfully! Your clean video is ready.',
      processedVideo: `/processed/${processedFileName}`
    });

  } catch (error: any) {
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
    } else if (error.message && error.message.includes('timeout')) {
      errorMessage = 'Processing timeout. Please try with a shorter video.';
    }

    res.status(500).json({
      success: false,
      error: errorMessage
    });
  }
}

export const config = {
  api: {
    bodyParser: false, // Disable body parsing, multer will handle it
  },
};

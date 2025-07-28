import axios from 'axios';
import type { NextApiRequest, NextApiResponse } from 'next';

interface HealthCheck {
  status: 'healthy' | 'degraded';
  timestamp: string;
  uptime: number;
  version: string;
  services: {
    database: string;
    storage: string;
    backend: string;
  };
  memory: {
    used: number;
    total: number;
  };
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<HealthCheck>
) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' } as any);
  }

  const backendUrl = process.env.BACKEND_URL || 'http://localhost:5000';

  const healthCheck: HealthCheck = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    version: '1.0.0',
    services: {
      database: 'connected',
      storage: 'available',
      backend: 'unknown'
    },
    memory: {
      used: Math.round(process.memoryUsage().heapUsed / 1024 / 1024),
      total: Math.round(process.memoryUsage().heapTotal / 1024 / 1024)
    }
  };

  // Check backend service
  try {
    await axios.get(`${backendUrl}/health`, { timeout: 5000 });
    healthCheck.services.backend = 'connected';
    res.status(200).json(healthCheck);
  } catch (error) {
    healthCheck.services.backend = 'disconnected';
    healthCheck.status = 'degraded';
    res.status(503).json(healthCheck);
  }
}

import type { NextApiRequest, NextApiResponse } from 'next';

interface PricingPlan {
  id: string;
  name: string;
  price: number;
  currency: string;
  interval: string;
  features: string[];
  limits: {
    videoLength: number;
    dailyUploads: number;
    monthlyUploads: number;
  };
  popular?: boolean;
}

interface PricingResponse {
  plans: PricingPlan[];
}

export default function handler(
  req: NextApiRequest,
  res: NextApiResponse<PricingResponse | { error: string }>
) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const pricing: PricingResponse = {
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
  
  res.status(200).json(pricing);
}

import type { NextApiRequest, NextApiResponse } from 'next';

interface RazorpayConfig {
  keyId: string;
  currency: string;
  company: {
    name: string;
    description: string;
    logo: string;
  };
}

export default function handler(
  req: NextApiRequest,
  res: NextApiResponse<RazorpayConfig | { error: string }>
) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  res.status(200).json({
    keyId: process.env.RAZORPAY_KEY_ID || 'rzp_test_your_key_id',
    currency: 'INR',
    company: {
      name: 'MovieCensorAI',
      description: 'Professional AI-powered content moderation',
      logo: '/images/logo.png'
    }
  });
}

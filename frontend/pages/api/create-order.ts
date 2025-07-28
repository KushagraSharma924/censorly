import Razorpay from 'razorpay';
import type { NextApiRequest, NextApiResponse } from 'next';

interface CreateOrderRequest {
  planId: string;
  amount: number;
  currency?: string;
}

interface CreateOrderResponse {
  success: boolean;
  orderId?: string;
  amount?: number;
  currency?: string;
  razorpayKeyId?: string;
  error?: string;
}

const razorpay = new Razorpay({
  key_id: process.env.RAZORPAY_KEY_ID || 'rzp_test_your_key_id',
  key_secret: process.env.RAZORPAY_KEY_SECRET || 'your_key_secret'
});

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<CreateOrderResponse>
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ success: false, error: 'Method not allowed' });
  }

  try {
    const { planId, amount, currency = 'INR' }: CreateOrderRequest = req.body;
    
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
    
    res.status(200).json({
      success: true,
      orderId: order.id,
      amount: typeof order.amount === 'string' ? parseInt(order.amount) : order.amount,
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
}

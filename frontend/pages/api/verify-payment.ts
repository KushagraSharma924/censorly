import crypto from 'crypto';
import type { NextApiRequest, NextApiResponse } from 'next';

interface VerifyPaymentRequest {
  razorpay_order_id: string;
  razorpay_payment_id: string;
  razorpay_signature: string;
  planId: string;
}

interface VerifyPaymentResponse {
  success: boolean;
  message?: string;
  paymentId?: string;
  orderId?: string;
  planId?: string;
  status?: string;
  error?: string;
}

export default function handler(
  req: NextApiRequest,
  res: NextApiResponse<VerifyPaymentResponse>
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ success: false, error: 'Method not allowed' });
  }

  try {
    const { 
      razorpay_order_id, 
      razorpay_payment_id, 
      razorpay_signature,
      planId 
    }: VerifyPaymentRequest = req.body;

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
      
      res.status(200).json({
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
}

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useAuth } from '@/contexts/auth-context';
import { buildApiUrl } from '@/config/api';

const ManualUpgrade: React.FC = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleManualUpgrade = async (tier: string) => {
    if (!user) {
      setError('Please login first');
      return;
    }

    setLoading(true);
    setError('');
    setMessage('');

    try {
      const response = await fetch(buildApiUrl('/api/manual/upgrade-user'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          tier: tier,
          duration_days: 30
        })
      });

      const data = await response.json();

      if (response.ok) {
        setMessage(`Successfully upgraded to ${tier} tier!`);
        // Refresh the page to show updated tier
        setTimeout(() => {
          window.location.reload();
        }, 2000);
      } else {
        setError(data.error || 'Upgrade failed');
      }
    } catch (err) {
      setError('Network error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleDowngrade = async () => {
    if (!user) {
      setError('Please login first');
      return;
    }

    setLoading(true);
    setError('');
    setMessage('');

    try {
      const response = await fetch(buildApiUrl('/api/manual/downgrade-user'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include'
      });

      const data = await response.json();

      if (response.ok) {
        setMessage('Successfully downgraded to free tier!');
        // Refresh the page to show updated tier
        setTimeout(() => {
          window.location.reload();
        }, 2000);
      } else {
        setError(data.error || 'Downgrade failed');
      }
    } catch (err) {
      setError('Network error occurred');
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <Card className="max-w-md mx-auto">
        <CardHeader>
          <CardTitle>Manual Upgrade Test</CardTitle>
        </CardHeader>
        <CardContent>
          <p>Please login to test manual upgrades.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="max-w-md mx-auto">
      <CardHeader>
        <CardTitle>Manual Upgrade Test</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <p><strong>Current User:</strong> {user.email}</p>
          <p><strong>Current Tier:</strong> {user.subscription_tier || 'free'}</p>
        </div>

        {message && (
          <Alert className="border-green-200 bg-green-50">
            <AlertDescription className="text-green-800">
              {message}
            </AlertDescription>
          </Alert>
        )}

        {error && (
          <Alert className="border-red-200 bg-red-50">
            <AlertDescription className="text-red-800">
              {error}
            </AlertDescription>
          </Alert>
        )}

        <div className="space-y-2">
          <h3 className="font-semibold">Test Upgrades:</h3>
          <div className="grid grid-cols-2 gap-2">
            <Button 
              onClick={() => handleManualUpgrade('basic')} 
              disabled={loading}
              variant="outline"
              size="sm"
            >
              Upgrade to Basic
            </Button>
            <Button 
              onClick={() => handleManualUpgrade('pro')} 
              disabled={loading}
              variant="outline"
              size="sm"
            >
              Upgrade to Pro
            </Button>
          </div>
          <Button 
            onClick={handleDowngrade} 
            disabled={loading}
            variant="outline"
            size="sm"
            className="w-full"
          >
            Downgrade to Free
          </Button>
        </div>

        {loading && (
          <div className="text-center">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500 mx-auto"></div>
            <p className="text-sm text-gray-600 mt-2">Processing...</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default ManualUpgrade;

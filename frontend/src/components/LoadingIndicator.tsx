import React from 'react';
import { Loader2, AlertCircle } from 'lucide-react';
import { Progress } from '@/components/ui/progress';

interface LoadingIndicatorProps {
  status: string;
  progress?: number;
  hasError?: boolean;
}

export const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({
  status,
  progress = 0,
  hasError = false
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 space-y-4">
      {hasError ? (
        <AlertCircle className="h-8 w-8 text-red-500 animate-pulse" />
      ) : (
        <Loader2 className="h-8 w-8 text-blue-500 animate-spin" />
      )}
      
      <div className="text-center">
        <p className={`text-lg font-medium ${hasError ? 'text-red-600' : 'text-gray-700'}`}>
          {status}
        </p>
        
        {progress > 0 && progress < 100 && (
          <div className="w-64 mt-3">
            <Progress value={progress} className="h-2" />
            <p className="text-sm text-gray-500 mt-1">{Math.round(progress)}% complete</p>
          </div>
        )}
      </div>
    </div>
  );
};

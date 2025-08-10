import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  FileVideo, 
  Upload, 
  Settings, 
  Download, 
  Clock,
  CheckCircle,
  AlertCircle,
  Zap,
  Shield,
  Sparkles
} from 'lucide-react';

export const UploadGuide = () => {
  return (
    <div className="space-y-6">
      {/* Quick Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="text-center p-4 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg border border-blue-200">
          <Zap className="h-8 w-8 text-blue-600 mx-auto mb-2" />
          <p className="text-sm font-medium text-blue-900">Fast Processing</p>
          <p className="text-xs text-blue-600">2-5 minutes avg</p>
        </div>
        <div className="text-center p-4 bg-gradient-to-br from-green-50 to-green-100 rounded-lg border border-green-200">
          <Shield className="h-8 w-8 text-green-600 mx-auto mb-2" />
          <p className="text-sm font-medium text-green-900">High Accuracy</p>
          <p className="text-xs text-green-600">0.8 threshold</p>
        </div>
        <div className="text-center p-4 bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg border border-purple-200">
          <FileVideo className="h-8 w-8 text-purple-600 mx-auto mb-2" />
          <p className="text-sm font-medium text-purple-900">All Formats</p>
          <p className="text-xs text-purple-600">MP4, AVI, MOV+</p>
        </div>
        <div className="text-center p-4 bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg border border-orange-200">
          <Sparkles className="h-8 w-8 text-orange-600 mx-auto mb-2" />
          <p className="text-sm font-medium text-orange-900">Auto Clean</p>
          <p className="text-xs text-orange-600">Smart detection</p>
        </div>
      </div>

      {/* Step-by-step Process */}
      <Card>
        <CardContent className="p-6">
          <h3 className="text-lg font-semibold mb-4 text-gray-900">How It Works</h3>
          <div className="space-y-4">
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                <Upload className="h-4 w-4 text-blue-600" />
              </div>
              <div>
                <h4 className="font-medium text-gray-900">1. Upload Your Video</h4>
                <p className="text-sm text-gray-600">Drag & drop or click to select. Supports MP4, AVI, MOV, WMV, MKV up to 500MB</p>
              </div>
            </div>
            
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0 w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                <Settings className="h-4 w-4 text-purple-600" />
              </div>
              <div>
                <h4 className="font-medium text-gray-900">2. AI Auto-Configuration</h4>
                <p className="text-sm text-gray-600">AI automatically sets optimal detection threshold (0.8) and beep censoring mode</p>
              </div>
            </div>
            
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0 w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
                <Clock className="h-4 w-4 text-yellow-600" />
              </div>
              <div>
                <h4 className="font-medium text-gray-900">3. Transformer AI Processing</h4>
                <p className="text-sm text-gray-600">HuggingFace transformer model analyzes audio with 290+ training samples</p>
              </div>
            </div>
            
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0 w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                <Download className="h-4 w-4 text-green-600" />
              </div>
              <div>
                <h4 className="font-medium text-gray-900">4. Download Clean Video</h4>
                <p className="text-sm text-gray-600">Get your professionally cleaned video ready for any platform</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Supported Formats */}
      <Card>
        <CardContent className="p-6">
          <h3 className="text-lg font-semibold mb-4 text-gray-900">Supported Formats</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {['MP4', 'AVI', 'MOV', 'WMV', 'MKV', 'WEBM'].map((format) => (
              <div key={format} className="flex items-center space-x-2 p-2 bg-gray-50 rounded-lg">
                <CheckCircle className="h-4 w-4 text-green-500" />
                <span className="text-sm font-medium">{format}</span>
              </div>
            ))}
          </div>
          <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
            <div className="flex items-start space-x-2">
              <AlertCircle className="h-5 w-5 text-blue-600 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-blue-900">Real Capabilities</p>
                <ul className="text-xs text-blue-700 mt-1 space-y-1">
                  <li>• Max file size: 500MB (Basic), 100MB (Free)</li>
                  <li>• Max duration: 30min (Basic), 5min (Free)</li>
                  <li>• AI Model: HuggingFace Transformer</li>
                  <li>• Training: 290+ sample dataset</li>
                </ul>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

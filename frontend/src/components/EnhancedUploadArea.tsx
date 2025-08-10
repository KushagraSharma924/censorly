import React, { useState, useRef } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Skeleton } from '@/components/ui/skeleton';
import { 
  Upload, 
  FileVideo, 
  X, 
  CheckCircle,
  AlertCircle,
  Film,
  PlayCircle,
  Clock
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface EnhancedUploadAreaProps {
  onFileSelect: (files: FileList) => void;
  isUploading?: boolean;
  dragActive?: boolean;
  onDragStateChange?: (active: boolean) => void;
  acceptedFiles?: string;
  maxSize?: number; // in MB
  multiple?: boolean;
}

export const EnhancedUploadArea: React.FC<EnhancedUploadAreaProps> = ({
  onFileSelect,
  isUploading = false,
  dragActive = false,
  onDragStateChange,
  acceptedFiles = 'video/*',
  maxSize = 500,
  multiple = true
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragOver(true);
      onDragStateChange?.(true);
    } else if (e.type === 'dragleave') {
      setIsDragOver(false);
      onDragStateChange?.(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
    onDragStateChange?.(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      onFileSelect(e.dataTransfer.files);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onFileSelect(e.target.files);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  if (isUploading) {
    return (
      <Card className="w-full">
        <CardContent className="p-8">
          <div className="text-center space-y-4">
            <div className="flex items-center justify-center w-16 h-16 mx-auto bg-blue-100 rounded-full">
              <Upload className="w-8 h-8 text-blue-600 animate-bounce" />
            </div>
            <div className="space-y-2">
              <h3 className="text-lg font-medium text-gray-900">Uploading your video...</h3>
              <p className="text-sm text-gray-600">Please wait while we process your file</p>
            </div>
            <div className="w-full max-w-xs mx-auto space-y-2">
              <Skeleton className="h-2 w-full" />
              <div className="flex justify-between text-xs text-gray-500">
                <span>Processing...</span>
                <span>Please don't close this page</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full">
      <CardContent className="p-0">
        <div
          className={cn(
            "relative border-2 border-dashed rounded-lg p-8 text-center transition-all duration-300 cursor-pointer",
            isDragOver || dragActive
              ? "border-blue-500 bg-blue-50 scale-[1.02] shadow-lg"
              : "border-gray-300 hover:border-gray-400 hover:bg-gray-50",
            isUploading && "pointer-events-none opacity-50"
          )}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            multiple={multiple}
            accept={acceptedFiles}
            onChange={handleFileSelect}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            disabled={isUploading}
          />
          
          <div className="space-y-4">
            {/* Upload Icon */}
            <div className={cn(
              "flex items-center justify-center w-16 h-16 mx-auto rounded-full transition-colors",
              isDragOver || dragActive
                ? "bg-blue-200 text-blue-600"
                : "bg-gray-100 text-gray-400"
            )}>
              {isDragOver || dragActive ? (
                <FileVideo className="w-8 h-8 animate-pulse" />
              ) : (
                <Upload className="w-8 h-8" />
              )}
            </div>

            {/* Upload Text */}
            <div className="space-y-2">
              <h3 className={cn(
                "text-lg font-medium transition-colors",
                isDragOver || dragActive ? "text-blue-900" : "text-gray-900"
              )}>
                {isDragOver || dragActive ? "Drop your videos here!" : "Upload your videos"}
              </h3>
              <p className="text-gray-600">
                Drag & drop your video files here, or click to browse
              </p>
            </div>

            {/* Upload Button */}
            <Button 
              type="button"
              className={cn(
                "transition-all duration-200",
                isDragOver || dragActive && "scale-105"
              )}
              onClick={(e) => {
                e.stopPropagation();
                fileInputRef.current?.click();
              }}
            >
              <Film className="w-4 h-4 mr-2" />
              Choose Videos
            </Button>

            {/* File Requirements */}
            <div className="text-xs text-gray-500 space-y-1">
              <p>Supports: MP4, AVI, MOV, WMV, MKV, WEBM</p>
              <p>Maximum size: {maxSize}MB per file</p>
              {multiple && <p>You can upload multiple files at once</p>}
            </div>
          </div>

          {/* Visual Enhancement for Drag State */}
          {(isDragOver || dragActive) && (
            <div className="absolute inset-0 border-2 border-blue-500 rounded-lg bg-blue-50/50 flex items-center justify-center">
              <div className="text-center">
                <PlayCircle className="w-12 h-12 text-blue-600 mx-auto mb-2 animate-pulse" />
                <p className="text-blue-900 font-medium">Release to upload</p>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

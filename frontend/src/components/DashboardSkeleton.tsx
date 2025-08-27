import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { FileVideo, BarChart3, Key, Calendar } from 'lucide-react';

export const DashboardSkeleton = () => {
  return (
    <div className="space-y-8">
      {/* Title Skeleton */}
      <div className="space-y-2">
        <Skeleton className="h-8 w-48" />
        <div className="flex items-center space-x-2">
          <span className="text-gray-700">Welcome back,</span>
          <Skeleton className="h-4 w-24" />
        </div>
      </div>

      {/* Refresh Button Skeleton */}
      <div className="flex justify-between items-center">
        <div></div>
        <Skeleton className="h-9 w-20" />
      </div>

      {/* Quick Stats Cards - Matching Actual Dashboard Layout */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        {/* Videos Processed This Month Card */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-600">Videos Processed This Month</p>
                <Skeleton className="h-8 w-20 mt-1" />
                <Skeleton className="h-2 w-full mt-2" />
                <Skeleton className="h-3 w-24 mt-1" />
              </div>
              <FileVideo className="h-8 w-8 text-gray-300" />
            </div>
          </CardContent>
        </Card>

        {/* Subscription Card */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Subscription</p>
                <Skeleton className="h-8 w-16 mt-1" />
                <Skeleton className="h-4 w-28 mt-2" />
              </div>
              <BarChart3 className="h-8 w-8 text-gray-300" />
            </div>
          </CardContent>
        </Card>

        {/* API Keys Card */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-600">API Keys</p>
                <Skeleton className="h-8 w-16 mt-1" />
                <Skeleton className="h-2 w-full mt-2" />
                <Skeleton className="h-3 w-20 mt-1" />
              </div>
              <Key className="h-8 w-8 text-gray-300" />
            </div>
          </CardContent>
        </Card>

        {/* Last Active Card */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Last Active</p>
                <Skeleton className="h-8 w-20 mt-1" />
                <Skeleton className="h-4 w-16 mt-2" />
              </div>
              <Calendar className="h-8 w-8 text-gray-300" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs Skeleton */}
      <div className="space-y-4">
        <div className="flex space-x-1 border-b">
          <Skeleton className="h-8 w-16" />
          <Skeleton className="h-8 w-20" />
          <Skeleton className="h-8 w-18" />
        </div>

        {/* Tab Content Skeleton */}
        <div className="space-y-6">
          {/* Recent Jobs */}
          <Card>
            <CardHeader>
              <Skeleton className="h-6 w-32" />
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {Array.from({ length: 3 }).map((_, i) => (
                  <div key={i} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex-1 space-y-2">
                      <Skeleton className="h-4 w-48" />
                      <div className="flex items-center space-x-4">
                        <Skeleton className="h-3 w-16" />
                        <Skeleton className="h-3 w-20" />
                        <Skeleton className="h-3 w-24" />
                      </div>
                    </div>
                    <div className="flex space-x-2">
                      <Skeleton className="h-8 w-16" />
                      <Skeleton className="h-8 w-8" />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

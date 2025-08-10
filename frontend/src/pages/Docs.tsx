import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  BookOpenIcon, 
  CodeBracketIcon, 
  CogIcon, 
  KeyIcon,
  ShieldCheckIcon,
  CloudArrowUpIcon,
  CommandLineIcon,
  DocumentTextIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  PlayIcon,
  GlobeAltIcon,
  BoltIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';
import { Header } from '@/components/Header';

const Docs: React.FC = () => {
  const [activeSection, setActiveSection] = useState('introduction');

  const sidebarItems = [
    {
      id: 'getting-started',
      title: 'Getting Started',
      icon: BookOpenIcon,
      items: [
        { id: 'introduction', title: 'Introduction' },
        { id: 'quick-start', title: 'Quick Start' },
        { id: 'authentication', title: 'Authentication' }
      ]
    },
    {
      id: 'api-reference',
      title: 'API Reference',
      icon: CodeBracketIcon,
      items: [
        { id: 'detect-endpoint', title: 'Detect Content' },
        { id: 'usage-endpoint', title: 'Check Usage' },
        { id: 'feedback-endpoint', title: 'Send Feedback' },
        { id: 'error-codes', title: 'Error Codes' }
      ]
    },
    {
      id: 'integration',
      title: 'Integration',
      icon: CogIcon,
      items: [
        { id: 'javascript-sdk', title: 'JavaScript SDK' },
        { id: 'python-sdk', title: 'Python SDK' },
        { id: 'webhooks', title: 'Webhooks' }
      ]
    },
    {
      id: 'resources',
      title: 'Resources',
      icon: ChartBarIcon,
      items: [
        { id: 'best-practices', title: 'Best Practices' },
        { id: 'coming-soon', title: 'Coming Soon' },
        { id: 'support', title: 'Support' }
      ]
    }
  ];

  const renderContent = () => {
    switch (activeSection) {
      case 'introduction':
        return (
          <div className="space-y-8">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-4">Censorly API Documentation</h1>
              <p className="text-xl text-gray-600 mb-8">
                AI-powered profanity and abuse detection for video, audio, and text content. 
                Keep your platform safe with real-time content moderation.
              </p>
            </div>

            <div className="bg-blue-50 border-l-4 border-blue-400 p-6">
              <div className="flex items-start">
                <ShieldCheckIcon className="h-6 w-6 text-blue-600 mt-1 mr-3 flex-shrink-0" />
                <div>
                  <h3 className="text-lg font-semibold text-blue-900 mb-2">What is Censorly?</h3>
                  <p className="text-blue-800">
                    Censorly is a comprehensive content moderation platform that automatically detects 
                    profanity, abuse, and inappropriate content across video, audio, and text formats. 
                    Built for developers who need reliable, scalable content moderation.
                  </p>
                </div>
              </div>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="bg-white border rounded-lg p-6">
                <div className="flex items-center mb-4">
                  <BoltIcon className="h-8 w-8 text-yellow-500 mr-3" />
                  <h3 className="text-lg font-semibold">Real-time Detection</h3>
                </div>
                <p className="text-gray-600">
                  Analyze content in real-time with sub-second response times for text and under 30 seconds for video.
                </p>
              </div>

              <div className="bg-white border rounded-lg p-6">
                <div className="flex items-center mb-4">
                  <GlobeAltIcon className="h-8 w-8 text-green-500 mr-3" />
                  <h3 className="text-lg font-semibold">Multi-language Support</h3>
                </div>
                <p className="text-gray-600">
                  Advanced AI models support English and Indic languages. Free tier includes regex-based English detection.
                </p>
              </div>

              <div className="bg-white border rounded-lg p-6">
                <div className="flex items-center mb-4">
                  <ChartBarIcon className="h-8 w-8 text-blue-500 mr-3" />
                  <h3 className="text-lg font-semibold">Developer Dashboard</h3>
                </div>
                <p className="text-gray-600">
                  Monitor usage, view analytics, and manage API keys through our intuitive developer dashboard.
                </p>
              </div>
            </div>

            <div className="bg-gray-50 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Who is Censorly for?</h3>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <h4 className="font-medium mb-2">Content Platforms</h4>
                  <ul className="text-gray-600 space-y-1 text-sm">
                    <li>• Social media platforms</li>
                    <li>• Video sharing websites</li>
                    <li>• Online communities</li>
                    <li>• Educational platforms</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-medium mb-2">Applications</h4>
                  <ul className="text-gray-600 space-y-1 text-sm">
                    <li>• Chat applications</li>
                    <li>• Gaming platforms</li>
                    <li>• Live streaming services</li>
                    <li>• Content management systems</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        );

      case 'quick-start':
        return (
          <div className="space-y-8">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-4">Quick Start</h1>
              <p className="text-xl text-gray-600 mb-8">
                Get started with Censorly in under 5 minutes. Sign up, get your API key, and make your first request.
              </p>
            </div>

            <div className="space-y-6">
              <div className="border-l-4 border-green-500 bg-green-50 p-6">
                <div className="flex items-center mb-3">
                  <span className="bg-green-600 text-white w-6 h-6 rounded-full flex items-center justify-center text-sm font-bold mr-3">1</span>
                  <h3 className="text-lg font-semibold">Sign Up & Get API Key</h3>
                </div>
                <p className="text-green-800 mb-4">
                  Create your account and get your JWT authentication token from the dashboard.
                </p>
                <Link 
                  to="/signup" 
                  className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 text-sm font-medium"
                >
                  Create Free Account
                </Link>
              </div>

              <div className="border-l-4 border-blue-500 bg-blue-50 p-6">
                <div className="flex items-center mb-3">
                  <span className="bg-blue-600 text-white w-6 h-6 rounded-full flex items-center justify-center text-sm font-bold mr-3">2</span>
                  <h3 className="text-lg font-semibold">Choose Your Plan</h3>
                </div>
                <div className="grid md:grid-cols-2 gap-4 mt-4">
                  <div className="bg-white border rounded-lg p-4">
                    <h4 className="font-semibold text-green-600 mb-2">Free Tier</h4>
                    <ul className="text-sm text-gray-600 space-y-1">
                      <li>• 3 videos/month</li>
                      <li>• 100MB per video</li>
                      <li>• Regex-based detection</li>
                      <li>• English only</li>
                    </ul>
                  </div>
                  <div className="bg-white border rounded-lg p-4">
                    <h4 className="font-semibold text-blue-600 mb-2">Basic Plan - $19/month</h4>
                    <ul className="text-sm text-gray-600 space-y-1">
                      <li>• 30 videos/month</li>
                      <li>• 1GB per video</li>
                      <li>• AI-powered detection</li>
                      <li>• Multi-language support</li>
                    </ul>
                  </div>
                </div>
              </div>

              <div className="border-l-4 border-purple-500 bg-purple-50 p-6">
                <div className="flex items-center mb-3">
                  <span className="bg-purple-600 text-white w-6 h-6 rounded-full flex items-center justify-center text-sm font-bold mr-3">3</span>
                  <h3 className="text-lg font-semibold">Make Your First Request</h3>
                </div>
                <p className="text-purple-800 mb-4">
                  Analyze your first piece of content using our detection API.
                </p>
                <div className="bg-gray-900 text-white p-4 rounded-lg font-mono text-sm overflow-x-auto">
                  <div className="text-green-400 mb-2"># Analyze text content</div>
                  <div>curl -X POST https://api.censorly.com/v1/detect \\</div>
                  <div className="ml-4">-H "Authorization: Bearer YOUR_JWT_TOKEN" \\</div>
                  <div className="ml-4">-H "Content-Type: application/json" \\</div>
                  <div className="ml-4">-d {`'{`}</div>
                  <div className="ml-8">"content": "Your text content here",</div>
                  <div className="ml-8">"type": "text",</div>
                  <div className="ml-8">"language": "en",</div>
                  <div className="ml-8">"mode": "regex"</div>
                  <div className="ml-4">{`}'`}</div>
                </div>
              </div>
            </div>

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
              <div className="flex items-start">
                <ExclamationTriangleIcon className="h-6 w-6 text-yellow-600 mt-1 mr-3 flex-shrink-0" />
                <div>
                  <h3 className="text-lg font-semibold text-yellow-900 mb-2">Rate Limits</h3>
                  <p className="text-yellow-800">
                    Free tier: 3 requests/month. Basic plan: 30 requests/month. 
                    Pro and Enterprise plans coming soon with higher limits.
                  </p>
                </div>
              </div>
            </div>
          </div>
        );

      case 'authentication':
        return (
          <div className="space-y-8">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-4">Authentication</h1>
              <p className="text-xl text-gray-600 mb-8">
                Censorly uses JWT-based authentication. Include your token in the Authorization header of every request.
              </p>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Getting Your JWT Token</h3>
              <p className="text-blue-800 mb-4">
                After signing up, you'll receive a JWT token from your dashboard. This token authenticates all your API requests.
              </p>
              <div className="bg-gray-900 text-white p-4 rounded-lg font-mono text-sm">
                <div className="text-green-400 mb-2"># Login to get your JWT token</div>
                <div>curl -X POST https://api.censorly.com/auth/login \\</div>
                <div className="ml-4">-H "Content-Type: application/json" \\</div>
                <div className="ml-4">-d {`'{`}</div>
                <div className="ml-8">"email": "your-email@example.com",</div>
                <div className="ml-8">"password": "your-password"</div>
                <div className="ml-4">{`}'`}</div>
              </div>
            </div>

            <div className="space-y-6">
              <div>
                <h3 className="text-xl font-semibold mb-4">Using the Authorization Header</h3>
                <p className="text-gray-600 mb-4">
                  Include your JWT token in the Authorization header of every API request:
                </p>
                
                <div className="space-y-4">
                  <div>
                    <h4 className="font-semibold mb-2">cURL Example</h4>
                    <div className="bg-gray-900 text-white p-4 rounded-lg font-mono text-sm">
                      <div>curl -X POST https://api.censorly.com/v1/detect \\</div>
                      <div className="ml-4 text-yellow-300">-H "Authorization: Bearer YOUR_JWT_TOKEN" \\</div>
                      <div className="ml-4">-H "Content-Type: application/json" \\</div>
                      <div className="ml-4">-d {`'{"content": "Text to analyze"}'`}</div>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-semibold mb-2">JavaScript Example</h4>
                    <div className="bg-gray-900 text-white p-4 rounded-lg font-mono text-sm">
                      <div className="text-green-400 mb-2">// Using fetch API</div>
                      <div>const response = await fetch('https://api.censorly.com/v1/detect', {'{'}</div>
                      <div className="ml-4">method: 'POST',</div>
                      <div className="ml-4">headers: {'{'}</div>
                      <div className="ml-8 text-yellow-300">'Authorization': `Bearer ${'{YOUR_JWT_TOKEN}'}`,</div>
                      <div className="ml-8">'Content-Type': 'application/json'</div>
                      <div className="ml-4">{'},'},</div>
                      <div className="ml-4">body: JSON.stringify({`{`}</div>
                      <div className="ml-8">content: 'Text to analyze',</div>
                      <div className="ml-8">type: 'text',</div>
                      <div className="ml-8">language: 'en'</div>
                      <div className="ml-4">{`})`}</div>
                      <div>{`});`}</div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-red-50 border border-red-200 rounded-lg p-6">
                <div className="flex items-start">
                  <ExclamationTriangleIcon className="h-6 w-6 text-red-600 mt-1 mr-3 flex-shrink-0" />
                  <div>
                    <h3 className="text-lg font-semibold text-red-900 mb-2">Security Best Practices</h3>
                    <ul className="text-red-800 space-y-1">
                      <li>• Never expose your JWT token in client-side code</li>
                      <li>• Use environment variables to store tokens</li>
                      <li>• Implement token refresh logic for long-running applications</li>
                      <li>• Monitor token usage in your dashboard</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        );

      case 'detect-endpoint':
        return (
          <div className="space-y-8">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-4">POST /api/v1/detect</h1>
              <p className="text-xl text-gray-600 mb-8">
                Analyze video, audio, or text content for profanity and inappropriate material.
              </p>
            </div>

            <div className="bg-green-50 border-l-4 border-green-400 p-6">
              <h3 className="text-lg font-semibold mb-4">Endpoint URL</h3>
              <div className="bg-gray-900 text-white p-3 rounded font-mono">
                POST https://api.censorly.com/v1/detect
              </div>
            </div>

            <div className="space-y-6">
              <div>
                <h3 className="text-xl font-semibold mb-4">Parameters</h3>
                <div className="overflow-x-auto">
                  <table className="w-full border-collapse border border-gray-300">
                    <thead>
                      <tr className="bg-gray-50">
                        <th className="border border-gray-300 px-4 py-2 text-left">Parameter</th>
                        <th className="border border-gray-300 px-4 py-2 text-left">Type</th>
                        <th className="border border-gray-300 px-4 py-2 text-left">Required</th>
                        <th className="border border-gray-300 px-4 py-2 text-left">Description</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td className="border border-gray-300 px-4 py-2 font-mono">file</td>
                        <td className="border border-gray-300 px-4 py-2">File/String</td>
                        <td className="border border-gray-300 px-4 py-2">Yes</td>
                        <td className="border border-gray-300 px-4 py-2">Video, audio file, or text string to analyze</td>
                      </tr>
                      <tr>
                        <td className="border border-gray-300 px-4 py-2 font-mono">language</td>
                        <td className="border border-gray-300 px-4 py-2">String</td>
                        <td className="border border-gray-300 px-4 py-2">No</td>
                        <td className="border border-gray-300 px-4 py-2">Language code (en, hi, ta, etc). Default: en</td>
                      </tr>
                      <tr>
                        <td className="border border-gray-300 px-4 py-2 font-mono">mode</td>
                        <td className="border border-gray-300 px-4 py-2">String</td>
                        <td className="border border-gray-300 px-4 py-2">No</td>
                        <td className="border border-gray-300 px-4 py-2">Detection mode: "regex" or "ai". Default: regex</td>
                      </tr>
                      <tr>
                        <td className="border border-gray-300 px-4 py-2 font-mono">type</td>
                        <td className="border border-gray-300 px-4 py-2">String</td>
                        <td className="border border-gray-300 px-4 py-2">No</td>
                        <td className="border border-gray-300 px-4 py-2">Content type: "video", "audio", "text". Auto-detected if not provided</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <div>
                <h3 className="text-xl font-semibold mb-4">Example Requests</h3>
                
                <div className="space-y-6">
                  <div>
                    <h4 className="font-semibold mb-2">Text Analysis</h4>
                    <div className="bg-gray-900 text-white p-4 rounded-lg font-mono text-sm">
                      <div>curl -X POST https://api.censorly.com/v1/detect \\</div>
                      <div className="ml-4">-H "Authorization: Bearer YOUR_JWT_TOKEN" \\</div>
                      <div className="ml-4">-H "Content-Type: application/json" \\</div>
                      <div className="ml-4">-d {`'{`}</div>
                      <div className="ml-8">"content": "This is sample text to analyze",</div>
                      <div className="ml-8">"type": "text",</div>
                      <div className="ml-8">"language": "en",</div>
                      <div className="ml-8">"mode": "regex"</div>
                      <div className="ml-4">{`}'`}</div>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-semibold mb-2">Video/Audio File Upload</h4>
                    <div className="bg-gray-900 text-white p-4 rounded-lg font-mono text-sm">
                      <div>curl -X POST https://api.censorly.com/v1/detect \\</div>
                      <div className="ml-4">-H "Authorization: Bearer YOUR_JWT_TOKEN" \\</div>
                      <div className="ml-4">-F "file=@/path/to/video.mp4" \\</div>
                      <div className="ml-4">-F "language=en" \\</div>
                      <div className="ml-4">-F "mode=ai"</div>
                    </div>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-xl font-semibold mb-4">Response Format</h3>
                <div className="bg-gray-900 text-white p-4 rounded-lg font-mono text-sm">
                  <div>{"{"}</div>
                  <div className="ml-4">"success": true,</div>
                  <div className="ml-4">"analysis_id": "ana_1234567890",</div>
                  <div className="ml-4">"status": "completed",</div>
                  <div className="ml-4">"result": {"{"}</div>
                  <div className="ml-8">"is_appropriate": false,</div>
                  <div className="ml-8">"confidence_score": 0.92,</div>
                  <div className="ml-8">"detected_issues": [</div>
                  <div className="ml-12">{"{"}</div>
                  <div className="ml-16">"type": "profanity",</div>
                  <div className="ml-16">"content": "inappropriate word",</div>
                  <div className="ml-16">"timestamp": "00:01:23",</div>
                  <div className="ml-16">"severity": "high"</div>
                  <div className="ml-12">{"}"}</div>
                  <div className="ml-8">"],</div>
                  <div className="ml-8">"summary": {"{"}</div>
                  <div className="ml-12">"total_violations": 1,</div>
                  <div className="ml-12">"categories": ["profanity"]</div>
                  <div className="ml-8">{"}"}</div>
                  <div className="ml-4">{"},"},</div>
                  <div className="ml-4">"processing_time_ms": 1250</div>
                  <div>{"}"}</div>
                </div>
              </div>
            </div>
          </div>
        );

      case 'usage-endpoint':
        return (
          <div className="space-y-8">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-4">GET /api/v1/usage</h1>
              <p className="text-xl text-gray-600 mb-8">
                Check your current quota usage and remaining limits.
              </p>
            </div>

            <div className="bg-blue-50 border-l-4 border-blue-400 p-6">
              <h3 className="text-lg font-semibold mb-4">Endpoint URL</h3>
              <div className="bg-gray-900 text-white p-3 rounded font-mono">
                GET https://api.censorly.com/v1/usage
              </div>
            </div>

            <div className="space-y-6">
              <div>
                <h3 className="text-xl font-semibold mb-4">Example Request</h3>
                <div className="bg-gray-900 text-white p-4 rounded-lg font-mono text-sm">
                  <div>curl -X GET https://api.censorly.com/v1/usage \\</div>
                  <div className="ml-4">-H "Authorization: Bearer YOUR_JWT_TOKEN"</div>
                </div>
              </div>

              <div>
                <h3 className="text-xl font-semibold mb-4">Response Format</h3>
                <div className="bg-gray-900 text-white p-4 rounded-lg font-mono text-sm">
                  <div>{"{"}</div>
                  <div className="ml-4">"success": true,</div>
                  <div className="ml-4">"plan": "basic",</div>
                  <div className="ml-4">"usage": {"{"}</div>
                  <div className="ml-8">"current_month": {"{"}</div>
                  <div className="ml-12">"videos_analyzed": 15,</div>
                  <div className="ml-12">"total_size_mb": 2500,</div>
                  <div className="ml-12">"api_calls": 28</div>
                  <div className="ml-8">{"},"},</div>
                  <div className="ml-8">"limits": {"{"}</div>
                  <div className="ml-12">"videos_per_month": 30,</div>
                  <div className="ml-12">"max_file_size_mb": 1024,</div>
                  <div className="ml-12">"api_calls_per_month": 100</div>
                  <div className="ml-8">{"},"},</div>
                  <div className="ml-8">"remaining": {"{"}</div>
                  <div className="ml-12">"videos": 15,</div>
                  <div className="ml-12">"api_calls": 72</div>
                  <div className="ml-8">{"}"}</div>
                  <div className="ml-4">{"},"},</div>
                  <div className="ml-4">"reset_date": "2025-09-01T00:00:00Z"</div>
                  <div>{"}"}</div>
                </div>
              </div>
            </div>
          </div>
        );

      case 'feedback-endpoint':
        return (
          <div className="space-y-8">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-4">POST /api/v1/feedback</h1>
              <p className="text-xl text-gray-600 mb-8">
                Send feedback to help improve our AI detection accuracy.
              </p>
            </div>

            <div className="bg-purple-50 border-l-4 border-purple-400 p-6">
              <h3 className="text-lg font-semibold mb-4">Endpoint URL</h3>
              <div className="bg-gray-900 text-white p-3 rounded font-mono">
                POST https://api.censorly.com/v1/feedback
              </div>
            </div>

            <div className="space-y-6">
              <div>
                <h3 className="text-xl font-semibold mb-4">Parameters</h3>
                <div className="overflow-x-auto">
                  <table className="w-full border-collapse border border-gray-300">
                    <thead>
                      <tr className="bg-gray-50">
                        <th className="border border-gray-300 px-4 py-2 text-left">Parameter</th>
                        <th className="border border-gray-300 px-4 py-2 text-left">Type</th>
                        <th className="border border-gray-300 px-4 py-2 text-left">Required</th>
                        <th className="border border-gray-300 px-4 py-2 text-left">Description</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td className="border border-gray-300 px-4 py-2 font-mono">analysis_id</td>
                        <td className="border border-gray-300 px-4 py-2">String</td>
                        <td className="border border-gray-300 px-4 py-2">Yes</td>
                        <td className="border border-gray-300 px-4 py-2">ID of the analysis to provide feedback on</td>
                      </tr>
                      <tr>
                        <td className="border border-gray-300 px-4 py-2 font-mono">feedback_type</td>
                        <td className="border border-gray-300 px-4 py-2">String</td>
                        <td className="border border-gray-300 px-4 py-2">Yes</td>
                        <td className="border border-gray-300 px-4 py-2">"false_positive", "false_negative", or "correct"</td>
                      </tr>
                      <tr>
                        <td className="border border-gray-300 px-4 py-2 font-mono">comments</td>
                        <td className="border border-gray-300 px-4 py-2">String</td>
                        <td className="border border-gray-300 px-4 py-2">No</td>
                        <td className="border border-gray-300 px-4 py-2">Additional comments about the analysis</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <div>
                <h3 className="text-xl font-semibold mb-4">Example Request</h3>
                <div className="bg-gray-900 text-white p-4 rounded-lg font-mono text-sm">
                  <div>curl -X POST https://api.censorly.com/v1/feedback \\</div>
                  <div className="ml-4">-H "Authorization: Bearer YOUR_JWT_TOKEN" \\</div>
                  <div className="ml-4">-H "Content-Type: application/json" \\</div>
                  <div className="ml-4">-d {`'{`}</div>
                  <div className="ml-8">"analysis_id": "ana_1234567890",</div>
                  <div className="ml-8">"feedback_type": "false_positive",</div>
                  <div className="ml-8">"comments": "This was flagged incorrectly"</div>
                  <div className="ml-4">{`}'`}</div>
                </div>
              </div>

              <div>
                <h3 className="text-xl font-semibold mb-4">Response Format</h3>
                <div className="bg-gray-900 text-white p-4 rounded-lg font-mono text-sm">
                  <div>{"{"}</div>
                  <div className="ml-4">"success": true,</div>
                  <div className="ml-4">"message": "Feedback received successfully",</div>
                  <div className="ml-4">"feedback_id": "fb_9876543210"</div>
                  <div>{"}"}</div>
                </div>
              </div>
            </div>
          </div>
        );
        return (
          <div className="space-y-8">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-4">Welcome to Censorly</h1>
              <p className="text-xl text-gray-600 mb-8">
                Advanced AI-powered content moderation and profanity filtering for modern applications.
              </p>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <div className="flex items-center mb-4">
                <ShieldCheckIcon className="h-6 w-6 text-blue-600 mr-2" />
                <h3 className="text-lg font-semibold text-blue-900">What is Censorly?</h3>
              </div>
              <p className="text-blue-800">
                Censorly is a text content moderation platform that uses AI-powered classification to detect and filter 
                inappropriate content, profanity, and harmful material in real-time. Built with HuggingFace transformers 
                and scikit-learn models.
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <div className="bg-white border rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-3 flex items-center">
                  <DocumentTextIcon className="h-5 w-5 mr-2 text-green-600" />
                  Text Classification
                </h3>
                <p className="text-gray-600">
                  Advanced AI models detect profanity, hate speech, and inappropriate content in text with high accuracy using transformer-based classification.
                </p>
              </div>
              
              <div className="bg-white border rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-3 flex items-center">
                  <CloudArrowUpIcon className="h-5 w-5 mr-2 text-blue-600" />
                  Job Processing
                </h3>
                <p className="text-gray-600">
                  Create jobs to process content asynchronously with real-time status tracking and detailed results.
                </p>
              </div>
            </div>
          </div>
        );

      case 'endpoints':
        return (
          <div className="space-y-8">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-4">API Endpoints</h1>
              <p className="text-xl text-gray-600 mb-8">
                Complete reference for all available API endpoints.
              </p>
            </div>

            <div className="space-y-6">
              <div className="border rounded-lg overflow-hidden">
                <div className="bg-green-50 px-6 py-4 border-b">
                  <div className="flex items-center">
                    <span className="bg-green-600 text-white px-3 py-1 rounded text-sm font-mono mr-4">POST</span>
                    <span className="font-mono text-lg">/api/jobs</span>
                  </div>
                </div>
                <div className="p-6">
                  <h3 className="text-lg font-semibold mb-3">Create Content Analysis Job</h3>
                  <p className="text-gray-600 mb-4">
                    Create a new job to analyze text content for profanity and inappropriate material.
                  </p>
                  
                  <h4 className="font-semibold mb-2">Headers:</h4>
                  <div className="bg-gray-900 text-white p-4 rounded-lg font-mono text-sm mb-4">
                    <div>Authorization: Bearer YOUR_JWT_TOKEN</div>
                    <div>Content-Type: application/json</div>
                  </div>

                  <h4 className="font-semibold mb-2">Request Body:</h4>
                  <div className="bg-gray-900 text-white p-4 rounded-lg font-mono text-sm mb-4">
                    <div>{`{`}</div>
                    <div className="ml-4">"content": "Text content to analyze",</div>
                    <div className="ml-4">"job_type": "text_analysis",</div>
                    <div className="ml-4">"metadata": {`{`}</div>
                    <div className="ml-8">"source": "api",</div>
                    <div className="ml-8">"priority": "normal"</div>
                    <div className="ml-4">{`}`}</div>
                    <div>{`}`}</div>
                  </div>

                  <h4 className="font-semibold mb-2">Response:</h4>
                  <div className="bg-gray-900 text-white p-4 rounded-lg font-mono text-sm">
                    <div>{`{`}</div>
                    <div className="ml-4">"message": "Job created successfully",</div>
                    <div className="ml-4">"job_id": "uuid-string",</div>
                    <div className="ml-4">"status": "pending",</div>
                    <div className="ml-4">"created_at": "2025-08-10T11:30:00Z"</div>
                    <div>{`}`}</div>
                  </div>
                </div>
              </div>

              <div className="border rounded-lg overflow-hidden">
                <div className="bg-blue-50 px-6 py-4 border-b">
                  <div className="flex items-center">
                    <span className="bg-blue-600 text-white px-3 py-1 rounded text-sm font-mono mr-4">GET</span>
                    <span className="font-mono text-lg">/api/jobs/{`{job_id}`}</span>
                  </div>
                </div>
                <div className="p-6">
                  <h3 className="text-lg font-semibold mb-3">Get Job Status and Results</h3>
                  <p className="text-gray-600 mb-4">
                    Retrieve the status and results of a content analysis job.
                  </p>
                  
                  <h4 className="font-semibold mb-2">Headers:</h4>
                  <div className="bg-gray-900 text-white p-4 rounded-lg font-mono text-sm mb-4">
                    <div>Authorization: Bearer YOUR_JWT_TOKEN</div>
                  </div>

                  <h4 className="font-semibold mb-2">Response:</h4>
                  <div className="bg-gray-900 text-white p-4 rounded-lg font-mono text-sm">
                    <div>{`{`}</div>
                    <div className="ml-4">"id": "uuid-string",</div>
                    <div className="ml-4">"status": "completed",</div>
                    <div className="ml-4">"job_type": "text_analysis",</div>
                    <div className="ml-4">"result": {`{`}</div>
                    <div className="ml-8">"is_appropriate": false,</div>
                    <div className="ml-8">"confidence": 0.92,</div>
                    <div className="ml-8">"flagged_content": ["inappropriate word"],</div>
                    <div className="ml-8">"classification": "profanity"</div>
                    <div className="ml-4">{`}`},</div>
                    <div className="ml-4">"created_at": "2025-08-10T11:30:00Z",</div>
                    <div className="ml-4">"completed_at": "2025-08-10T11:30:15Z"</div>
                    <div>{`}`}</div>
                  </div>
                </div>
              </div>

              <div className="border rounded-lg overflow-hidden">
                <div className="bg-purple-50 px-6 py-4 border-b">
                  <div className="flex items-center">
                    <span className="bg-purple-600 text-white px-3 py-1 rounded text-sm font-mono mr-4">GET</span>
                    <span className="font-mono text-lg">/api/keys</span>
                  </div>
                </div>
                <div className="p-6">
                  <h3 className="text-lg font-semibold mb-3">List API Keys</h3>
                  <p className="text-gray-600 mb-4">
                    Get all API keys for the authenticated user.
                  </p>
                  
                  <h4 className="font-semibold mb-2">Headers:</h4>
                  <div className="bg-gray-900 text-white p-4 rounded-lg font-mono text-sm mb-4">
                    <div>Authorization: Bearer YOUR_JWT_TOKEN</div>
                  </div>

                  <h4 className="font-semibold mb-2">Response:</h4>
                  <div className="bg-gray-900 text-white p-4 rounded-lg font-mono text-sm">
                    <div>{`{`}</div>
                    <div className="ml-4">"api_keys": [</div>
                    <div className="ml-8">{`{`}</div>
                    <div className="ml-12">"id": "uuid",</div>
                    <div className="ml-12">"name": "My API Key",</div>
                    <div className="ml-12">"key": "ak_****",</div>
                    <div className="ml-12">"is_active": true,</div>
                    <div className="ml-12">"created_at": "2025-08-10T10:00:00Z"</div>
                    <div className="ml-8">{`}`}</div>
                    <div className="ml-4">]</div>
                    <div>{`}`}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        );

      case 'request-format':
        return (
          <div className="space-y-8">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-4">Request Format</h1>
              <p className="text-xl text-gray-600 mb-8">
                Standard request formats and conventions for the Censorly API.
              </p>
            </div>

            <div className="space-y-6">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Authentication Header</h3>
                <p className="text-blue-800 mb-4">All authenticated requests must include a JWT token:</p>
                <div className="bg-gray-900 text-white p-4 rounded-lg font-mono text-sm">
                  <div>Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...</div>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="text-xl font-semibold">Content Types</h3>
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="bg-white border rounded-lg p-4">
                    <h4 className="font-semibold mb-2">JSON Requests</h4>
                    <div className="bg-gray-100 p-3 rounded font-mono text-sm">
                      Content-Type: application/json
                    </div>
                    <p className="text-gray-600 text-sm mt-2">Used for most API endpoints</p>
                  </div>
                  <div className="bg-white border rounded-lg p-4">
                    <h4 className="font-semibold mb-2">File Uploads</h4>
                    <div className="bg-gray-100 p-3 rounded font-mono text-sm">
                      Content-Type: multipart/form-data
                    </div>
                    <p className="text-gray-600 text-sm mt-2">Used for profile image uploads</p>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-xl font-semibold mb-4">Request Body Examples</h3>
                <div className="space-y-4">
                  <div>
                    <h4 className="font-semibold mb-2">Create Job Request</h4>
                    <div className="bg-gray-900 text-white p-4 rounded-lg font-mono text-sm">
                      <div>{`{`}</div>
                      <div className="ml-4">"content": "Text to analyze for inappropriate content",</div>
                      <div className="ml-4">"job_type": "text_analysis",</div>
                      <div className="ml-4">"metadata": {`{`}</div>
                      <div className="ml-8">"source": "web_app",</div>
                      <div className="ml-8">"priority": "normal",</div>
                      <div className="ml-8">"callback_url": "https://yourapp.com/webhook"</div>
                      <div className="ml-4">{`}`}</div>
                      <div>{`}`}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        );

      case 'response-format':
        return (
          <div className="space-y-8">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-4">Response Format</h1>
              <p className="text-xl text-gray-600 mb-8">
                Standard response formats and status codes from the Censorly API.
              </p>
            </div>

            <div className="space-y-6">
              <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Success Response</h3>
                <div className="bg-gray-900 text-white p-4 rounded-lg font-mono text-sm">
                  <div>HTTP/1.1 200 OK</div>
                  <div>Content-Type: application/json</div>
                  <div><br/></div>
                  <div>{`{`}</div>
                  <div className="ml-4">"message": "Job created successfully",</div>
                  <div className="ml-4">"job_id": "123e4567-e89b-12d3-a456-426614174000",</div>
                  <div className="ml-4">"status": "pending",</div>
                  <div className="ml-4">"created_at": "2025-08-10T11:30:00Z"</div>
                  <div>{`}`}</div>
                </div>
              </div>

              <div className="bg-red-50 border border-red-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Error Response</h3>
                <div className="bg-gray-900 text-white p-4 rounded-lg font-mono text-sm">
                  <div>HTTP/1.1 401 Unauthorized</div>
                  <div>Content-Type: application/json</div>
                  <div><br/></div>
                  <div>{`{`}</div>
                  <div className="ml-4">"error": "Invalid or expired token",</div>
                  <div className="ml-4">"code": "INVALID_TOKEN",</div>
                  <div className="ml-4">"timestamp": "2025-08-10T11:30:00Z"</div>
                  <div>{`}`}</div>
                </div>
              </div>

              <div>
                <h3 className="text-xl font-semibold mb-4">Job Result Response</h3>
                <div className="bg-gray-900 text-white p-4 rounded-lg font-mono text-sm">
                  <div>{`{`}</div>
                  <div className="ml-4">"id": "123e4567-e89b-12d3-a456-426614174000",</div>
                  <div className="ml-4">"status": "completed",</div>
                  <div className="ml-4">"job_type": "text_analysis",</div>
                  <div className="ml-4">"content": "Original text content",</div>
                  <div className="ml-4">"result": {`{`}</div>
                  <div className="ml-8">"is_appropriate": false,</div>
                  <div className="ml-8">"confidence": 0.92,</div>
                  <div className="ml-8">"flagged_words": ["inappropriate", "word"],</div>
                  <div className="ml-8">"classification": "profanity",</div>
                  <div className="ml-8">"severity": "medium"</div>
                  <div className="ml-4">{`}`},</div>
                  <div className="ml-4">"created_at": "2025-08-10T11:30:00Z",</div>
                  <div className="ml-4">"completed_at": "2025-08-10T11:30:15Z"</div>
                  <div>{`}`}</div>
                </div>
              </div>
            </div>
          </div>
        );

      case 'web-apps':
        return (
          <div className="space-y-8">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-4">Web Application Integration</h1>
              <p className="text-xl text-gray-600 mb-8">
                Integrate Censorly into your web applications for real-time content moderation.
              </p>
            </div>

            <div className="space-y-6">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">JavaScript/React Integration</h3>
                <div className="bg-gray-900 text-white p-4 rounded-lg font-mono text-sm overflow-x-auto">
                  <div className="text-green-400 mb-2">// Example React integration</div>
                  <div>const analyzeContent = async (text) =&gt; {'{'}</div>
                  <div className="ml-4">const response = await fetch('/api/jobs', {'{'}</div>
                  <div className="ml-8">method: 'POST',</div>
                  <div className="ml-8">headers: {'{'}</div>
                  <div className="ml-12">'Authorization': `Bearer ${'{token}'}`,</div>
                  <div className="ml-12">'Content-Type': 'application/json'</div>
                  <div className="ml-8">{'}'}</div>
                  <div className="ml-8">body: JSON.stringify({'{'}</div>
                  <div className="ml-12">content: text,</div>
                  <div className="ml-12">job_type: 'text_analysis'</div>
                  <div className="ml-8">{'}'}</div>
                  <div className="ml-4">{'}'});</div>
                  <div className="ml-4">return await response.json();</div>
                  <div>{'}'}</div>
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                <div className="bg-white border rounded-lg p-6">
                  <h4 className="font-semibold mb-3">Form Validation</h4>
                  <ul className="space-y-2 text-gray-600 text-sm">
                    <li>• Validate comments before posting</li>
                    <li>• Check user-generated content</li>
                    <li>• Real-time chat moderation</li>
                    <li>• Forum post filtering</li>
                  </ul>
                </div>
                <div className="bg-white border rounded-lg p-6">
                  <h4 className="font-semibold mb-3">Content Management</h4>
                  <ul className="space-y-2 text-gray-600 text-sm">
                    <li>• Bulk content analysis</li>
                    <li>• Automated flagging system</li>
                    <li>• Moderation dashboard</li>
                    <li>• Appeal management</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        );

      case 'mobile-apps':
        return (
          <div className="space-y-8">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-4">Mobile Application Integration</h1>
              <p className="text-xl text-gray-600 mb-8">
                Integrate content moderation into your iOS and Android applications.
              </p>
            </div>

            <div className="space-y-6">
              <div className="grid md:grid-cols-2 gap-6">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                  <h3 className="text-lg font-semibold mb-4">iOS (Swift)</h3>
                  <div className="bg-gray-900 text-white p-4 rounded-lg font-mono text-xs overflow-x-auto">
                    <div className="text-green-400 mb-2">// Swift example</div>
                    <div>func analyzeText(_ text: String) async {'{'}</div>
                    <div className="ml-4">let url = URL(string: "https://api.censorly.com/jobs")!</div>
                    <div className="ml-4">var request = URLRequest(url: url)</div>
                    <div className="ml-4">request.httpMethod = "POST"</div>
                    <div className="ml-4">request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")</div>
                    <div className="ml-4">request.setValue("application/json", forHTTPHeaderField: "Content-Type")</div>
                    <div className="ml-4">// Add request body...</div>
                    <div>{'}'}</div>
                  </div>
                </div>

                <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                  <h3 className="text-lg font-semibold mb-4">Android (Kotlin)</h3>
                  <div className="bg-gray-900 text-white p-4 rounded-lg font-mono text-xs overflow-x-auto">
                    <div className="text-green-400 mb-2">// Kotlin example</div>
                    <div>suspend fun analyzeText(text: String) {'{'}</div>
                    <div className="ml-4">val client = OkHttpClient()</div>
                    <div className="ml-4">val json = JSONObject().apply {'{'}</div>
                    <div className="ml-8">put("content", text)</div>
                    <div className="ml-8">put("job_type", "text_analysis")</div>
                    <div className="ml-4">{'}'}</div>
                    <div className="ml-4">// Make request...</div>
                    <div>{'}'}</div>
                  </div>
                </div>
              </div>

              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Best Practices for Mobile</h3>
                <ul className="space-y-2 text-yellow-800">
                  <li>• <strong>Offline Support:</strong> Cache results for offline viewing</li>
                  <li>• <strong>Battery Optimization:</strong> Batch requests when possible</li>
                  <li>• <strong>Network Efficiency:</strong> Use compression and minimize requests</li>
                  <li>• <strong>User Experience:</strong> Show loading states and handle errors gracefully</li>
                </ul>
              </div>
            </div>
          </div>
        );

      case 'webhooks':
        return (
          <div className="space-y-8">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-4">Webhooks</h1>
              <p className="text-xl text-gray-600 mb-8">
                Receive real-time notifications when analysis is completed.
              </p>
            </div>

            <div className="bg-yellow-50 border-l-4 border-yellow-400 p-6">
              <h3 className="text-lg font-semibold mb-2">🚧 Coming Soon</h3>
              <p>Webhook functionality is currently in development. Available in Q4 2025.</p>
            </div>

            <div className="space-y-6">
              <div>
                <h3 className="text-xl font-semibold mb-4">Planned Features</h3>
                <ul className="space-y-2 text-gray-700">
                  <li className="flex items-start">
                    <span className="text-green-500 mr-2">✓</span>
                    Real-time notifications for completed analysis
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-500 mr-2">✓</span>
                    Configurable event types and filters
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-500 mr-2">✓</span>
                    Automatic retry with exponential backoff
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-500 mr-2">✓</span>
                    HMAC signature verification for security
                  </li>
                </ul>
              </div>

              <div>
                <h3 className="text-xl font-semibold mb-4">Expected Webhook Format</h3>
                <div className="bg-gray-900 text-white p-4 rounded-lg font-mono text-sm">
                  <div>POST /your-webhook-endpoint</div>
                  <div>Content-Type: application/json</div>
                  <div>X-Censorly-Signature: sha256=...</div>
                  <div className="mt-2">{`{`}</div>
                  <div className="ml-4">"event": "analysis.completed",</div>
                  <div className="ml-4">"timestamp": "2024-08-15T10:30:00Z",</div>
                  <div className="ml-4">"data": {`{`}</div>
                  <div className="ml-8">"analysis_id": "ana_1234567890",</div>
                  <div className="ml-8">"status": "completed",</div>
                  <div className="ml-8">"result": {`{ ... }`}</div>
                  <div className="ml-4">{`}`}</div>
                  <div>{`}`}</div>
                </div>
              </div>
            </div>
          </div>
        );

      case 'best-practices':
        return (
          <div className="space-y-8">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-4">Best Practices</h1>
              <p className="text-xl text-gray-600 mb-8">
                Optimize your integration for better performance and accuracy.
              </p>
            </div>

            <div className="space-y-8">
              <div>
                <h3 className="text-2xl font-semibold mb-4">Performance Optimization</h3>
                <div className="space-y-4">
                  <div className="bg-blue-50 border border-blue-200 p-4 rounded">
                    <h4 className="font-semibold mb-2">Choose the Right Detection Mode</h4>
                    <ul className="space-y-1 text-sm text-gray-700">
                      <li>• Use "regex" mode for basic text filtering (faster, free tier)</li>
                      <li>• Use "ai" mode for nuanced context analysis (slower, paid tier)</li>
                      <li>• Consider hybrid approach: regex first, then AI for edge cases</li>
                    </ul>
                  </div>

                  <div className="bg-green-50 border border-green-200 p-4 rounded">
                    <h4 className="font-semibold mb-2">File Size Optimization</h4>
                    <ul className="space-y-1 text-sm text-gray-700">
                      <li>• Compress videos before upload (H.264 recommended)</li>
                      <li>• Extract audio for audio-only analysis</li>
                      <li>• Consider chunking large files for better processing</li>
                    </ul>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-2xl font-semibold mb-4">Accuracy Improvement</h3>
                <div className="space-y-4">
                  <div className="bg-purple-50 border border-purple-200 p-4 rounded">
                    <h4 className="font-semibold mb-2">Language Selection</h4>
                    <ul className="space-y-1 text-sm text-gray-700">
                      <li>• Always specify the correct language for better accuracy</li>
                      <li>• Use auto-detection sparingly - manual selection preferred</li>
                      <li>• Consider regional variations (en-US vs en-GB)</li>
                    </ul>
                  </div>

                  <div className="bg-orange-50 border border-orange-200 p-4 rounded">
                    <h4 className="font-semibold mb-2">Feedback Loop</h4>
                    <ul className="space-y-1 text-sm text-gray-700">
                      <li>• Provide feedback on false positives/negatives</li>
                      <li>• This helps improve our AI models over time</li>
                      <li>• Regular feedback improves accuracy for your specific use case</li>
                    </ul>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-2xl font-semibold mb-4">Error Handling</h3>
                <div className="bg-gray-900 text-white p-4 rounded-lg font-mono text-sm">
                  <div>// Recommended error handling pattern</div>
                  <div>try {`{`}</div>
                  <div className="ml-4">const result = await censorly.analyzeText(content);</div>
                  <div className="ml-4">return result;</div>
                  <div>{`} catch (error) {`}</div>
                  <div className="ml-4">if (error.status === 429) {`{`}</div>
                  <div className="ml-8">// Rate limited - implement exponential backoff</div>
                  <div className="ml-8">await delay(error.retryAfter * 1000);</div>
                  <div className="ml-8">return retry();</div>
                  <div className="ml-4">{`} else if (error.status === 413) {`}</div>
                  <div className="ml-8">// File too large - compress or chunk</div>
                  <div className="ml-8">return compressAndRetry();</div>
                  <div className="ml-4">{`}`}</div>
                  <div className="ml-4">throw error;</div>
                  <div>{`}`}</div>
                </div>
              </div>
            </div>
          </div>
        );

      case 'coming-soon':
        return (
          <div className="space-y-8">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-4">Coming Soon</h1>
              <p className="text-xl text-gray-600 mb-8">
                Exciting features in development for the Censorly platform.
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-lg">
                <h3 className="text-xl font-semibold mb-3 text-blue-800">Real-time Streaming</h3>
                <p className="text-blue-700 mb-4">Live content moderation for streaming platforms and video calls.</p>
                <div className="text-sm text-blue-600">Expected: Q4 2025</div>
              </div>

              <div className="bg-gradient-to-br from-green-50 to-green-100 p-6 rounded-lg">
                <h3 className="text-xl font-semibold mb-3 text-green-800">Custom AI Models</h3>
                <p className="text-green-700 mb-4">Train personalized models for your specific content and context.</p>
                <div className="text-sm text-green-600">Expected: Q1 2026</div>
              </div>

              <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-6 rounded-lg">
                <h3 className="text-xl font-semibold mb-3 text-purple-800">Advanced Analytics</h3>
                <p className="text-purple-700 mb-4">Detailed insights and trends about your content moderation.</p>
                <div className="text-sm text-purple-600">Expected: Q4 2025</div>
              </div>

              <div className="bg-gradient-to-br from-orange-50 to-orange-100 p-6 rounded-lg">
                <h3 className="text-xl font-semibold mb-3 text-orange-800">Mobile SDKs</h3>
                <p className="text-orange-700 mb-4">Native iOS and Android SDKs for mobile app integration.</p>
                <div className="text-sm text-orange-600">Expected: Q2 2026</div>
              </div>

              <div className="bg-gradient-to-br from-red-50 to-red-100 p-6 rounded-lg">
                <h3 className="text-xl font-semibold mb-3 text-red-800">Image Moderation</h3>
                <p className="text-red-700 mb-4">AI-powered analysis for inappropriate images and visual content.</p>
                <div className="text-sm text-red-600">Expected: Q1 2026</div>
              </div>

              <div className="bg-gradient-to-br from-indigo-50 to-indigo-100 p-6 rounded-lg">
                <h3 className="text-xl font-semibold mb-3 text-indigo-800">Enterprise Features</h3>
                <p className="text-indigo-700 mb-4">SSO, advanced security, dedicated infrastructure, and SLA.</p>
                <div className="text-sm text-indigo-600">Expected: Q3 2026</div>
              </div>
            </div>

            <div className="bg-yellow-50 border border-yellow-200 p-6 rounded-lg">
              <h3 className="text-lg font-semibold mb-2">Want to influence our roadmap?</h3>
              <p className="text-gray-700 mb-4">
                We'd love to hear about your specific use cases and feature requests.
              </p>
              <a 
                href="mailto:feedback@censorly.com" 
                className="bg-yellow-500 text-white px-4 py-2 rounded hover:bg-yellow-600 transition-colors"
              >
                Share Your Ideas
              </a>
            </div>
          </div>
        );

      case 'support':
        return (
          <div className="space-y-8">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-4">Support</h1>
              <p className="text-xl text-gray-600 mb-8">
                Get help with integration, troubleshooting, and technical questions.
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <div className="bg-white border border-gray-200 p-6 rounded-lg">
                <h3 className="text-xl font-semibold mb-3">📧 Email Support</h3>
                <p className="text-gray-600 mb-4">For technical questions and integration help</p>
                <a href="mailto:support@censorly.com" className="text-blue-600 hover:underline">
                  support@censorly.com
                </a>
              </div>

              <div className="bg-white border border-gray-200 p-6 rounded-lg">
                <h3 className="text-xl font-semibold mb-3">💬 Chat Support</h3>
                <p className="text-gray-600 mb-4">Real-time help during business hours</p>
                <span className="text-gray-500">Available in dashboard</span>
              </div>

              <div className="bg-white border border-gray-200 p-6 rounded-lg">
                <h3 className="text-xl font-semibold mb-3">📖 Documentation</h3>
                <p className="text-gray-600 mb-4">Comprehensive guides and API reference</p>
                <span className="text-blue-600">You're here!</span>
              </div>

              <div className="bg-white border border-gray-200 p-6 rounded-lg">
                <h3 className="text-xl font-semibold mb-3">🐛 Bug Reports</h3>
                <p className="text-gray-600 mb-4">Report issues and get updates</p>
                <a href="mailto:bugs@censorly.com" className="text-blue-600 hover:underline">
                  bugs@censorly.com
                </a>
              </div>
            </div>

            <div className="bg-blue-50 border border-blue-200 p-6 rounded-lg">
              <h3 className="text-lg font-semibold mb-4">Response Times</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Free Plan:</span>
                  <span className="font-medium">48 hours</span>
                </div>
                <div className="flex justify-between">
                  <span>Basic Plan:</span>
                  <span className="font-medium">24 hours</span>
                </div>
                <div className="flex justify-between">
                  <span>Pro Plan:</span>
                  <span className="font-medium">12 hours</span>
                </div>
                <div className="flex justify-between">
                  <span>Enterprise:</span>
                  <span className="font-medium">4 hours</span>
                </div>
              </div>
            </div>
          </div>
        );
        return (
          <div className="space-y-8">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-4">Webhooks</h1>
              <p className="text-xl text-gray-600 mb-8">
                Receive real-time notifications when content analysis jobs are completed.
              </p>
            </div>

            <div className="space-y-6">
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Setting Up Webhooks</h3>
                <p className="text-purple-800 mb-4">
                  Include a <code>callback_url</code> in your job creation request to receive notifications:
                </p>
                <div className="bg-gray-900 text-white p-4 rounded-lg font-mono text-sm">
                  <div>{`{`}</div>
                  <div className="ml-4">"content": "Text to analyze",</div>
                  <div className="ml-4">"job_type": "text_analysis",</div>
                  <div className="ml-4">"metadata": {`{`}</div>
                  <div className="ml-8">"callback_url": "https://yourapp.com/webhook/content-analyzed"</div>
                  <div className="ml-4">{`}`}</div>
                  <div>{`}`}</div>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="text-xl font-semibold">Webhook Payload</h3>
                <div className="bg-gray-900 text-white p-4 rounded-lg font-mono text-sm">
                  <div>POST /webhook/content-analyzed</div>
                  <div>Content-Type: application/json</div>
                  <div><br/></div>
                  <div>{`{`}</div>
                  <div className="ml-4">"event": "job.completed",</div>
                  <div className="ml-4">"job_id": "123e4567-e89b-12d3-a456-426614174000",</div>
                  <div className="ml-4">"status": "completed",</div>
                  <div className="ml-4">"result": {`{`}</div>
                  <div className="ml-8">"is_appropriate": false,</div>
                  <div className="ml-8">"confidence": 0.92,</div>
                  <div className="ml-8">"classification": "profanity"</div>
                  <div className="ml-4">{`}`},</div>
                  <div className="ml-4">"timestamp": "2025-08-10T11:30:15Z"</div>
                  <div>{`}`}</div>
                </div>
              </div>

              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Security Considerations</h3>
                <ul className="space-y-2 text-yellow-800">
                  <li>• <strong>HTTPS Only:</strong> Webhook URLs must use HTTPS</li>
                  <li>• <strong>Signature Verification:</strong> Verify webhook signatures (coming soon)</li>
                  <li>• <strong>Retry Logic:</strong> Implement idempotent handlers for retries</li>
                  <li>• <strong>Timeout Handling:</strong> Respond within 30 seconds</li>
                </ul>
              </div>
            </div>
          </div>
        );

      case 'subscription':
        return (
          <div className="space-y-8">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-4">Subscription Plans</h1>
              <p className="text-xl text-gray-600 mb-8">
                Choose the right plan for your content moderation needs.
              </p>
            </div>

            <div className="grid md:grid-cols-3 gap-6">
              <div className="bg-white border rounded-lg p-6">
                <h3 className="text-xl font-semibold mb-4 text-center">Free</h3>
                <div className="text-center mb-6">
                  <div className="text-3xl font-bold text-blue-600">$0</div>
                  <div className="text-gray-600">/month</div>
                </div>
                <ul className="space-y-3 mb-6">
                  <li className="flex items-center">
                    <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2" />
                    <span>50 requests/month</span>
                  </li>
                  <li className="flex items-center">
                    <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2" />
                    <span>3 API keys</span>
                  </li>
                  <li className="flex items-center">
                    <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2" />
                    <span>Basic text analysis</span>
                  </li>
                  <li className="flex items-center">
                    <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2" />
                    <span>Community support</span>
                  </li>
                </ul>
              </div>

              <div className="bg-white border-2 border-blue-500 rounded-lg p-6 relative">
                <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                  <span className="bg-blue-500 text-white px-3 py-1 rounded-full text-sm">Popular</span>
                </div>
                <h3 className="text-xl font-semibold mb-4 text-center">Basic</h3>
                <div className="text-center mb-6">
                  <div className="text-3xl font-bold text-blue-600">$19</div>
                  <div className="text-gray-600">/month</div>
                </div>
                <ul className="space-y-3 mb-6">
                  <li className="flex items-center">
                    <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2" />
                    <span>100 requests/month</span>
                  </li>
                  <li className="flex items-center">
                    <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2" />
                    <span>10 API keys</span>
                  </li>
                  <li className="flex items-center">
                    <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2" />
                    <span>Advanced classification</span>
                  </li>
                  <li className="flex items-center">
                    <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2" />
                    <span>Email support</span>
                  </li>
                  <li className="flex items-center">
                    <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2" />
                    <span>Webhook notifications</span>
                  </li>
                </ul>
              </div>

              <div className="bg-white border rounded-lg p-6">
                <h3 className="text-xl font-semibold mb-4 text-center">Premium</h3>
                <div className="text-center mb-6">
                  <div className="text-3xl font-bold text-blue-600">$99</div>
                  <div className="text-gray-600">/month</div>
                </div>
                <ul className="space-y-3 mb-6">
                  <li className="flex items-center">
                    <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2" />
                    <span>1000 requests/month</span>
                  </li>
                  <li className="flex items-center">
                    <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2" />
                    <span>50 API keys</span>
                  </li>
                  <li className="flex items-center">
                    <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2" />
                    <span>Custom models</span>
                  </li>
                  <li className="flex items-center">
                    <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2" />
                    <span>Priority support</span>
                  </li>
                  <li className="flex items-center">
                    <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2" />
                    <span>SLA guarantee</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        );

      case 'error-codes':
        return (
          <div className="space-y-8">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-4">Error Codes</h1>
              <p className="text-xl text-gray-600 mb-8">
                Complete reference for API error codes and troubleshooting.
              </p>
            </div>

            <div className="space-y-6">
              <div>
                <h3 className="text-xl font-semibold mb-4">HTTP Status Codes</h3>
                <div className="overflow-x-auto">
                  <table className="w-full border-collapse border border-gray-300">
                    <thead>
                      <tr className="bg-gray-50">
                        <th className="border border-gray-300 px-4 py-2 text-left">Status Code</th>
                        <th className="border border-gray-300 px-4 py-2 text-left">Description</th>
                        <th className="border border-gray-300 px-4 py-2 text-left">Common Causes</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td className="border border-gray-300 px-4 py-2 font-mono">200</td>
                        <td className="border border-gray-300 px-4 py-2">Success</td>
                        <td className="border border-gray-300 px-4 py-2">Request completed successfully</td>
                      </tr>
                      <tr>
                        <td className="border border-gray-300 px-4 py-2 font-mono">400</td>
                        <td className="border border-gray-300 px-4 py-2">Bad Request</td>
                        <td className="border border-gray-300 px-4 py-2">Invalid parameters, missing required fields</td>
                      </tr>
                      <tr>
                        <td className="border border-gray-300 px-4 py-2 font-mono">401</td>
                        <td className="border border-gray-300 px-4 py-2">Unauthorized</td>
                        <td className="border border-gray-300 px-4 py-2">Invalid or missing JWT token</td>
                      </tr>
                      <tr>
                        <td className="border border-gray-300 px-4 py-2 font-mono">403</td>
                        <td className="border border-gray-300 px-4 py-2">Forbidden</td>
                        <td className="border border-gray-300 px-4 py-2">Quota exceeded, plan limitations</td>
                      </tr>
                      <tr>
                        <td className="border border-gray-300 px-4 py-2 font-mono">413</td>
                        <td className="border border-gray-300 px-4 py-2">File Too Large</td>
                        <td className="border border-gray-300 px-4 py-2">File exceeds maximum size limit</td>
                      </tr>
                      <tr>
                        <td className="border border-gray-300 px-4 py-2 font-mono">429</td>
                        <td className="border border-gray-300 px-4 py-2">Rate Limited</td>
                        <td className="border border-gray-300 px-4 py-2">Too many requests in time window</td>
                      </tr>
                      <tr>
                        <td className="border border-gray-300 px-4 py-2 font-mono">500</td>
                        <td className="border border-gray-300 px-4 py-2">Internal Server Error</td>
                        <td className="border border-gray-300 px-4 py-2">Processing error, try again later</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <div>
                <h3 className="text-xl font-semibold mb-4">Error Response Format</h3>
                <div className="bg-gray-900 text-white p-4 rounded-lg font-mono text-sm">
                  <div>{"{"}</div>
                  <div className="ml-4">"success": false,</div>
                  <div className="ml-4">"error": {"{"}</div>
                  <div className="ml-8">"code": "QUOTA_EXCEEDED",</div>
                  <div className="ml-8">"message": "Monthly video analysis quota exceeded",</div>
                  <div className="ml-8">"details": "15/15 videos used. Resets on 2025-09-01"</div>
                  <div className="ml-4">{"},"},</div>
                  <div className="ml-4">"request_id": "req_1234567890"</div>
                  <div>{"}"}</div>
                </div>
              </div>

              <div>
                <h3 className="text-xl font-semibold mb-4">Common Error Codes</h3>
                <div className="space-y-4">
                  <div className="bg-red-50 border border-red-200 p-4 rounded">
                    <h4 className="font-semibold text-red-800">INVALID_TOKEN</h4>
                    <p className="text-red-700">JWT token is invalid or expired. Refresh your token or re-authenticate.</p>
                  </div>
                  <div className="bg-orange-50 border border-orange-200 p-4 rounded">
                    <h4 className="font-semibold text-orange-800">QUOTA_EXCEEDED</h4>
                    <p className="text-orange-700">You've reached your plan's usage limits. Upgrade or wait for reset.</p>
                  </div>
                  <div className="bg-blue-50 border border-blue-200 p-4 rounded">
                    <h4 className="font-semibold text-blue-800">FILE_TOO_LARGE</h4>
                    <p className="text-blue-700">Upload file is larger than allowed. Compress or upgrade plan.</p>
                  </div>
                  <div className="bg-yellow-50 border border-yellow-200 p-4 rounded">
                    <h4 className="font-semibold text-yellow-800">UNSUPPORTED_FORMAT</h4>
                    <p className="text-yellow-700">File format not supported. Check supported formats list.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        );

      case 'javascript-sdk':
        return (
          <div className="space-y-8">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-4">JavaScript SDK</h1>
              <p className="text-xl text-gray-600 mb-8">
                Official JavaScript SDK for browser and Node.js applications.
              </p>
            </div>

            <div className="bg-yellow-50 border-l-4 border-yellow-400 p-6">
              <h3 className="text-lg font-semibold mb-2">🚧 Coming Soon</h3>
              <p>JavaScript SDK is currently in development. Expected release: Q4 2025.</p>
              <p className="mt-2">For now, use direct API calls as shown in the API Reference section.</p>
            </div>

            <div className="space-y-6">
              <div>
                <h3 className="text-xl font-semibold mb-4">Current Alternative: Direct API Calls</h3>
                <div className="bg-gray-900 text-white p-4 rounded-lg font-mono text-sm">
                  <div>// Current approach using fetch API</div>
                  <div>const response = await fetch('https://api.censorly.com/v1/detect', {`{`}</div>
                  <div className="ml-4">method: 'POST',</div>
                  <div className="ml-4">headers: {`{`}</div>
                  <div className="ml-8">'Authorization': `Bearer ${`{token}`}`,</div>
                  <div className="ml-8">'Content-Type': 'application/json'</div>
                  <div className="ml-4">{`},`}</div>
                  <div className="ml-4">body: JSON.stringify({`{`}</div>
                  <div className="ml-8">content: 'Text to analyze',</div>
                  <div className="ml-8">language: 'en'</div>
                  <div className="ml-4">{`})`}</div>
                  <div>{`});`}</div>
                  <div className="mt-2">const result = await response.json();</div>
                </div>
              </div>

              <div>
                <h3 className="text-xl font-semibold mb-4">Planned SDK Features</h3>
                <ul className="space-y-2 text-gray-700">
                  <li className="flex items-start">
                    <span className="text-green-500 mr-2">✓</span>
                    Automatic authentication handling
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-500 mr-2">✓</span>
                    Built-in retry logic and error handling
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-500 mr-2">✓</span>
                    TypeScript support with full type definitions
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-500 mr-2">✓</span>
                    File upload helpers for video/audio analysis
                  </li>
                </ul>
              </div>
            </div>
          </div>
        );

      case 'python-sdk':
        return (
          <div className="space-y-8">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-4">Python SDK</h1>
              <p className="text-xl text-gray-600 mb-8">
                Official Python SDK for server-side applications and ML pipelines.
              </p>
            </div>

            <div className="bg-yellow-50 border-l-4 border-yellow-400 p-6">
              <h3 className="text-lg font-semibold mb-2">🚧 Coming Soon</h3>
              <p>Python SDK is currently in development. Expected release: Q1 2026.</p>
              <p className="mt-2">For now, use direct API calls with the requests library.</p>
            </div>

            <div className="space-y-6">
              <div>
                <h3 className="text-xl font-semibold mb-4">Current Alternative: Direct API Calls</h3>
                <div className="bg-gray-900 text-white p-4 rounded-lg font-mono text-sm">
                  <div># Current approach using requests</div>
                  <div>import requests</div>
                  <div className="mt-2">headers = {`{`}</div>
                  <div className="ml-4">'Authorization': f'Bearer {`{token}`}',</div>
                  <div className="ml-4">'Content-Type': 'application/json'</div>
                  <div>{`}`}</div>
                  <div className="mt-2">data = {`{`}</div>
                  <div className="ml-4">'content': 'Text to analyze',</div>
                  <div className="ml-4">'language': 'en'</div>
                  <div>{`}`}</div>
                  <div className="mt-2">response = requests.post(</div>
                  <div className="ml-4">'https://api.censorly.com/v1/detect',</div>
                  <div className="ml-4">headers=headers,</div>
                  <div className="ml-4">json=data</div>
                  <div>)</div>
                  <div className="mt-2">result = response.json()</div>
                </div>
              </div>

              <div>
                <h3 className="text-xl font-semibold mb-4">Planned SDK Features</h3>
                <ul className="space-y-2 text-gray-700">
                  <li className="flex items-start">
                    <span className="text-green-500 mr-2">✓</span>
                    Pythonic API with type hints
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-500 mr-2">✓</span>
                    Async/await support for high-performance applications
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-500 mr-2">✓</span>
                    Batch processing helpers for large datasets
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-500 mr-2">✓</span>
                    Integration with popular ML frameworks (pandas, numpy)
                  </li>
                </ul>
              </div>
            </div>
          </div>
        );
        return (
          <div className="space-y-8">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-4">Error Codes</h1>
              <p className="text-xl text-gray-600 mb-8">
                Understanding API error responses and how to handle them.
              </p>
            </div>

            <div className="space-y-4">
              {[
                { code: '200', status: 'OK', description: 'Request successful', color: 'green' },
                { code: '400', status: 'Bad Request', description: 'Invalid request format or parameters', color: 'red' },
                { code: '401', status: 'Unauthorized', description: 'Invalid or missing API key', color: 'red' },
                { code: '403', status: 'Forbidden', description: 'API key does not have required permissions', color: 'red' },
                { code: '429', status: 'Rate Limited', description: 'Too many requests - rate limit exceeded', color: 'yellow' },
                { code: '500', status: 'Server Error', description: 'Internal server error - please try again', color: 'red' }
              ].map((error) => (
                <div key={error.code} className="border rounded-lg p-4">
                  <div className="flex items-center mb-2">
                    <span className={`px-3 py-1 rounded text-sm font-mono mr-4 text-white bg-${error.color}-600`}>
                      {error.code}
                    </span>
                    <span className="font-semibold">{error.status}</span>
                  </div>
                  <p className="text-gray-600">{error.description}</p>
                </div>
              ))}
            </div>
          </div>
        );

      case 'api-keys':
        return (
          <div className="space-y-8">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-4">API Key Management</h1>
              <p className="text-xl text-gray-600 mb-8">
                Learn how to create, manage, and secure your API keys.
              </p>
            </div>

            <div className="space-y-6">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-3 flex items-center">
                  <KeyIcon className="h-5 w-5 mr-2 text-blue-600" />
                  Creating API Keys
                </h3>
                <ol className="list-decimal list-inside space-y-2 text-blue-800">
                  <li>Navigate to your <Link to="/dashboard" className="underline">Dashboard</Link></li>
                  <li>Click on "API Keys" in the sidebar</li>
                  <li>Click "Generate New Key"</li>
                  <li>Give your key a descriptive name</li>
                  <li>Set appropriate permissions</li>
                  <li>Copy and securely store your key</li>
                </ol>
              </div>

              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-3 flex items-center">
                  <ExclamationTriangleIcon className="h-5 w-5 mr-2 text-yellow-600" />
                  Security Best Practices
                </h3>
                <ul className="list-disc list-inside space-y-2 text-yellow-800">
                  <li>Never commit API keys to version control</li>
                  <li>Use environment variables for key storage</li>
                  <li>Rotate keys regularly</li>
                  <li>Use different keys for different environments</li>
                  <li>Monitor key usage in your dashboard</li>
                  <li>Immediately revoke compromised keys</li>
                </ul>
              </div>
            </div>
          </div>
        );

      case 'text-filtering':
        return (
          <div className="space-y-8">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-4">Text Classification</h1>
              <p className="text-xl text-gray-600 mb-8">
                Advanced AI-powered text analysis using HuggingFace transformers and scikit-learn models.
              </p>
            </div>

            <div className="bg-green-50 border border-green-200 rounded-lg p-6">
              <div className="flex items-center mb-4">
                <CheckCircleIcon className="h-6 w-6 text-green-600 mr-2" />
                <h3 className="text-lg font-semibold text-green-900">How It Works</h3>
              </div>
              <div className="space-y-3 text-green-800">
                <p>• <strong>AI Classification:</strong> Uses transformer models to analyze text content</p>
                <p>• <strong>Multiple Models:</strong> Supports both HuggingFace and scikit-learn models</p>
                <p>• <strong>High Accuracy:</strong> Advanced algorithms ensure reliable detection</p>
                <p>• <strong>Real-time Processing:</strong> Fast analysis with immediate results</p>
              </div>
            </div>

            <div className="space-y-6">
              <h3 className="text-xl font-semibold">Supported Content Types</h3>
              <div className="grid md:grid-cols-2 gap-4">
                <div className="bg-white border rounded-lg p-4">
                  <h4 className="font-semibold mb-2">Profanity Detection</h4>
                  <p className="text-gray-600 text-sm">Identifies offensive language and inappropriate terms</p>
                </div>
                <div className="bg-white border rounded-lg p-4">
                  <h4 className="font-semibold mb-2">Hate Speech</h4>
                  <p className="text-gray-600 text-sm">Detects discriminatory and harmful language</p>
                </div>
                <div className="bg-white border rounded-lg p-4">
                  <h4 className="font-semibold mb-2">Inappropriate Content</h4>
                  <p className="text-gray-600 text-sm">Flags unsuitable content for various contexts</p>
                </div>
                <div className="bg-white border rounded-lg p-4">
                  <h4 className="font-semibold mb-2">Custom Classifications</h4>
                  <p className="text-gray-600 text-sm">Configurable categories based on your needs</p>
                </div>
              </div>
            </div>
          </div>
        );

      case 'job-processing':
        return (
          <div className="space-y-8">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-4">Job Processing</h1>
              <p className="text-xl text-gray-600 mb-8">
                Asynchronous job processing system for scalable content analysis.
              </p>
            </div>

            <div className="space-y-6">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-3">Job Lifecycle</h3>
                <div className="space-y-3">
                  <div className="flex items-center">
                    <div className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs mr-3">1</div>
                    <span><strong>Create:</strong> Submit content for analysis via POST /api/jobs</span>
                  </div>
                  <div className="flex items-center">
                    <div className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs mr-3">2</div>
                    <span><strong>Process:</strong> AI models analyze the content</span>
                  </div>
                  <div className="flex items-center">
                    <div className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs mr-3">3</div>
                    <span><strong>Complete:</strong> Results are stored and accessible</span>
                  </div>
                  <div className="flex items-center">
                    <div className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs mr-3">4</div>
                    <span><strong>Retrieve:</strong> Get results via GET /api/jobs/{`{job_id}`}</span>
                  </div>
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                <div className="bg-white border rounded-lg p-6">
                  <h4 className="font-semibold mb-3">Job Types</h4>
                  <ul className="space-y-2 text-gray-600">
                    <li>• <code className="bg-gray-100 px-2 py-1 rounded">text_analysis</code> - Text content classification</li>
                    <li>• <code className="bg-gray-100 px-2 py-1 rounded">batch_processing</code> - Multiple content items</li>
                    <li>• <code className="bg-gray-100 px-2 py-1 rounded">custom</code> - Custom analysis workflows</li>
                  </ul>
                </div>
                <div className="bg-white border rounded-lg p-6">
                  <h4 className="font-semibold mb-3">Job Status</h4>
                  <ul className="space-y-2 text-gray-600">
                    <li>• <span className="inline-block w-3 h-3 bg-yellow-500 rounded-full mr-2"></span><code>pending</code> - Waiting for processing</li>
                    <li>• <span className="inline-block w-3 h-3 bg-blue-500 rounded-full mr-2"></span><code>processing</code> - Currently analyzing</li>
                    <li>• <span className="inline-block w-3 h-3 bg-green-500 rounded-full mr-2"></span><code>completed</code> - Analysis finished</li>
                    <li>• <span className="inline-block w-3 h-3 bg-red-500 rounded-full mr-2"></span><code>failed</code> - Processing error</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        );

      case 'rate-limiting':
        return (
          <div className="space-y-8">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-4">Rate Limiting</h1>
              <p className="text-xl text-gray-600 mb-8">
                Subscription-based usage limits and fair use policies.
              </p>
            </div>

            <div className="space-y-6">
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
                <div className="flex items-center mb-4">
                  <ExclamationTriangleIcon className="h-6 w-6 text-yellow-600 mr-2" />
                  <h3 className="text-lg font-semibold text-yellow-900">Rate Limit Headers</h3>
                </div>
                <p className="text-yellow-800 mb-4">
                  Every API response includes rate limit information in the headers:
                </p>
                <div className="bg-gray-900 text-white p-4 rounded-lg font-mono text-sm">
                  <div>X-RateLimit-Limit: 100</div>
                  <div>X-RateLimit-Remaining: 95</div>
                  <div>X-RateLimit-Reset: 1691659200</div>
                </div>
              </div>

              <div className="grid md:grid-cols-3 gap-6">
                <div className="bg-white border rounded-lg p-6">
                  <h4 className="font-semibold mb-3 text-center">Free Tier</h4>
                  <div className="text-center mb-4">
                    <div className="text-2xl font-bold text-blue-600">50</div>
                    <div className="text-gray-600">requests/month</div>
                  </div>
                  <ul className="space-y-2 text-sm text-gray-600">
                    <li>• Basic text analysis</li>
                    <li>• 3 API keys max</li>
                    <li>• Standard support</li>
                  </ul>
                </div>

                <div className="bg-white border rounded-lg p-6 border-blue-500">
                  <h4 className="font-semibold mb-3 text-center">Basic Plan</h4>
                  <div className="text-center mb-4">
                    <div className="text-2xl font-bold text-blue-600">100</div>
                    <div className="text-gray-600">requests/month</div>
                  </div>
                  <ul className="space-y-2 text-sm text-gray-600">
                    <li>• Advanced classification</li>
                    <li>• 10 API keys max</li>
                    <li>• Priority support</li>
                  </ul>
                </div>

                <div className="bg-white border rounded-lg p-6">
                  <h4 className="font-semibold mb-3 text-center">Premium Plan</h4>
                  <div className="text-center mb-4">
                    <div className="text-2xl font-bold text-blue-600">1000</div>
                    <div className="text-gray-600">requests/month</div>
                  </div>
                  <ul className="space-y-2 text-sm text-gray-600">
                    <li>• Custom models</li>
                    <li>• 50 API keys max</li>
                    <li>• Dedicated support</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        );

      default:
        return (
          <div className="space-y-8">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-4">Section Not Found</h1>
              <p className="text-xl text-gray-600 mb-8">
                The requested documentation section could not be found.
              </p>
            </div>
            <div className="bg-yellow-50 border border-yellow-200 p-6 rounded-lg">
              <p>Please select a section from the sidebar to view documentation.</p>
            </div>
          </div>
        );
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex gap-8">
          {/* Sidebar */}
          <div className="w-64 flex-shrink-0">
            <div className="bg-white rounded-lg border p-4">
              <nav className="space-y-2">
                {sidebarItems.map((section) => (
                  <div key={section.id}>
                    <div className="flex items-center text-sm font-semibold text-gray-900 mb-2">
                      <section.icon className="h-4 w-4 mr-2" />
                      {section.title}
                    </div>
                    <div className="ml-6 space-y-1">
                      {section.items.map((item) => (
                        <button
                          key={item.id}
                          onClick={() => setActiveSection(item.id)}
                          className={`block w-full text-left text-sm py-1 px-2 rounded ${
                            activeSection === item.id
                              ? 'bg-blue-100 text-blue-700'
                              : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                          }`}
                        >
                          {item.title}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </nav>
            </div>
          </div>

          {/* Main Content */}
          <div className="flex-1">
            <div className="bg-white rounded-lg border p-8">
              {renderContent()}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Docs;

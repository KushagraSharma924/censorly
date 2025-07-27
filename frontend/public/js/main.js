// Main JavaScript for MovieCensorAI Frontend with API Integration

// Global configuration
let CONFIG = {
    backendUrl: 'http://localhost:5000' // Default fallback
};

// Load configuration from server
async function loadConfig() {
    try {
        const response = await fetch('/api/config');
        if (response.ok) {
            CONFIG = await response.json();
        }
    } catch (error) {
        console.warn('Failed to load config, using defaults:', error);
    }
}

document.addEventListener('DOMContentLoaded', async function() {
    // Load configuration first
    await loadConfig();
    
    // Initialize API client
    const API = {
        baseURL: window.location.origin,
        
        async call(endpoint, options = {}) {
            try {
                const response = await fetch(`${this.baseURL}${endpoint}`, {
                    headers: {
                        'Content-Type': 'application/json',
                        ...options.headers
                    },
                    ...options
                });
                
                if (!response.ok) {
                    throw new Error(`API Error: ${response.status}`);
                }
                
                return await response.json();
            } catch (error) {
                console.error('API call failed:', error);
                throw error;
            }
        },

        // Health check
        async checkHealth() {
            return this.call('/api/health');
        },

        // Get system stats
        async getStats() {
            return this.call('/api/stats');
        },

        // Get pricing info
        async getPricing() {
            return this.call('/api/pricing');
        },

        // Validate file
        async validateFile(file) {
            const formData = new FormData();
            formData.append('video', file);
            
            return fetch(`${this.baseURL}/api/validate-file`, {
                method: 'POST',
                body: formData
            }).then(res => res.json());
        },

        // Get limits
        async getLimits() {
            return this.call('/api/limits');
        },

        // Get queue status
        async getQueueStatus() {
            return this.call('/api/queue');
        },

        // Submit contact form
        async submitContact(data) {
            return this.call('/api/contact', {
                method: 'POST',
                body: JSON.stringify(data)
            });
        },

        // Subscribe to newsletter
        async subscribeNewsletter(email) {
            return this.call('/api/newsletter', {
                method: 'POST',
                body: JSON.stringify({ email })
            });
        },

        // Get features
        async getFeatures() {
            return this.call('/api/features');
        },

        // Razorpay Integration
        async createOrder(planId, amount, currency = 'USD') {
            return this.call('/api/create-order', {
                method: 'POST',
                body: JSON.stringify({ planId, amount, currency })
            });
        },

        async verifyPayment(paymentData) {
            return this.call('/api/verify-payment', {
                method: 'POST',
                body: JSON.stringify(paymentData)
            });
        },

        async getRazorpayConfig() {
            return this.call('/api/razorpay-config');
        }
    };

    // Global loading state manager
    const LoadingManager = {
        activeRequests: 0,
        
        show() {
            this.activeRequests++;
            this.updateUI();
        },
        
        hide() {
            this.activeRequests = Math.max(0, this.activeRequests - 1);
            this.updateUI();
        },
        
        updateUI() {
            const isLoading = this.activeRequests > 0;
            document.body.style.cursor = isLoading ? 'wait' : '';
            
            // Could add a global loading indicator here if needed
            // const loader = document.getElementById('global-loader');
            // if (loader) loader.style.display = isLoading ? 'block' : 'none';
        }
    };

    // Elements
    const videoInput = document.getElementById('videoInput');
    const dropZone = document.getElementById('dropZone');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const uploadForm = document.getElementById('uploadForm');
    const submitBtn = document.getElementById('submitBtn');
    const submitText = document.getElementById('submitText');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const processingStatus = document.getElementById('processingStatus');

    // Initialize app
    initializeApp();

    // Pricing button handlers
    setupPricingButtons();

    // CTA button handler
    setupCTAButton();

    // Setup checkout overlay handlers
    setupCheckoutHandlers();

    async function initializeApp() {
        try {
            // Check system health
            const health = await API.checkHealth();
            updateHealthStatus(health);

            // Load dynamic content
            await Promise.all([
                loadStats(),
                loadPricingData(),
                loadQueueStatus(),
                loadFeatures()
            ]);

            console.log('🎬 MovieCensorAI Frontend Initialized Successfully!');
        } catch (error) {
            console.error('Initialization failed:', error);
            showAlert('System initialization failed. Some features may not work properly.', 'error');
        }
    }

    function setupPricingButtons() {
        // Free plan button
        const freeBtn = document.getElementById('free-plan-btn');
        if (freeBtn) {
            freeBtn.addEventListener('click', () => handlePlanSelection('free'));
        }

        // Pro plan button
        const proBtn = document.getElementById('pro-plan-btn');
        if (proBtn) {
            proBtn.addEventListener('click', () => handlePlanSelection('pro'));
        }

        // Enterprise plan button
        const enterpriseBtn = document.getElementById('enterprise-plan-btn');
        if (enterpriseBtn) {
            enterpriseBtn.addEventListener('click', () => handlePlanSelection('enterprise'));
        }
    }

    async function handlePlanSelection(plan) {
        const button = document.getElementById(`${plan}-plan-btn`);
        if (!button) return;

        const originalText = button.textContent;
        
        try {
            button.disabled = true;
            button.textContent = 'Loading...';

            if (plan === 'free') {
                // Free plan - redirect to upload
                const uploadSection = document.getElementById('upload');
                if (uploadSection) {
                    uploadSection.scrollIntoView({ behavior: 'smooth' });
                    showAlert('Welcome to the free plan! Please upload a video to get started.', 'success');
                }
            } else if (plan === 'enterprise') {
                // Enterprise plan - redirect to contact form
                const contactSection = document.getElementById('contact');
                if (contactSection) {
                    contactSection.scrollIntoView({ behavior: 'smooth' });
                    const subjectField = document.getElementById('contact-subject');
                    if (subjectField) {
                        subjectField.value = 'Enterprise Plan Inquiry';
                    }
                    showAlert('Please fill out the contact form for enterprise pricing.', 'info');
                }
            } else {
                // Paid plans - redirect to Razorpay payment page
                button.textContent = 'Redirecting to Payment...';
                window.open('https://rzp.io/rzp/censorly-upgrade', '_blank');
                showAlert('Redirecting to secure payment page...', 'info');
            }
        } catch (error) {
            console.error('Error handling plan selection:', error);
            showAlert('Error processing plan selection. Please try again.', 'error');
        } finally {
            button.disabled = false;
            button.textContent = originalText;
        }
    }

    async function openCheckout(planId) {
        try {
            // Get pricing data
            const pricing = await API.getPricing();
            const plan = pricing.plans.find(p => p.id === planId);
            
            if (!plan) {
                throw new Error('Plan not found');
            }

            // Populate checkout overlay
            document.getElementById('checkout-plan-name').textContent = `${plan.name} Plan`;
            document.getElementById('checkout-price').textContent = `$${plan.price}/${plan.interval}`;
            
            // Populate features
            const featuresList = document.querySelector('#checkout-features ul');
            featuresList.innerHTML = plan.features.map(feature => 
                `<li class="flex items-center"><svg class="w-4 h-4 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path></svg>${feature}</li>`
            ).join('');

            // Store plan data for payment
            document.getElementById('checkout-overlay').setAttribute('data-plan-id', planId);
            document.getElementById('checkout-overlay').setAttribute('data-plan-amount', plan.price);
            
            // Show overlay
            document.getElementById('checkout-overlay').classList.remove('hidden');
            document.body.style.overflow = 'hidden';
            
        } catch (error) {
            console.error('Error opening checkout:', error);
            showAlert('Error opening checkout. Please try again.', 'error');
        }
    }

    function setupCTAButton() {
        const ctaButtons = document.querySelectorAll('a[href="#upload"]');
        ctaButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const uploadSection = document.getElementById('upload');
                if (uploadSection) {
                    uploadSection.scrollIntoView({ behavior: 'smooth' });
                    showAlert('Ready to process your video! Please upload a file below.', 'info');
                }
            });
        });
    }

    function setupCheckoutHandlers() {
        // Close checkout overlay
        const closeBtn = document.getElementById('close-checkout');
        const overlay = document.getElementById('checkout-overlay');
        
        if (closeBtn) {
            closeBtn.addEventListener('click', closeCheckout);
        }
        
        if (overlay) {
            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) {
                    closeCheckout();
                }
            });
        }

        // Proceed to payment button
        const proceedBtn = document.getElementById('proceed-payment');
        if (proceedBtn) {
            proceedBtn.addEventListener('click', handlePayment);
        }

        // Handle escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !overlay.classList.contains('hidden')) {
                closeCheckout();
            }
        });
    }

    function closeCheckout() {
        document.getElementById('checkout-overlay').classList.add('hidden');
        document.body.style.overflow = '';
    }

    async function handlePayment() {
        const overlay = document.getElementById('checkout-overlay');
        const proceedBtn = document.getElementById('proceed-payment');
        
        const planId = overlay.getAttribute('data-plan-id');
        const amount = parseFloat(overlay.getAttribute('data-plan-amount'));
        
        const originalText = proceedBtn.textContent;
        
        try {
            proceedBtn.disabled = true;
            proceedBtn.textContent = 'Creating Order...';

            // Create Razorpay order
            const orderData = await API.createOrder(planId, amount, 'USD');
            
            if (!orderData.success) {
                throw new Error('Failed to create payment order');
            }

            // Close the overlay immediately and open Razorpay fullscreen
            closeCheckout();
            
            proceedBtn.textContent = 'Opening Payment...';

            // Initialize Razorpay checkout in fullscreen mode
            const options = {
                key: orderData.razorpayKeyId,
                amount: orderData.amount,
                currency: orderData.currency,
                name: 'MovieCensorAI',
                description: `${planId.charAt(0).toUpperCase() + planId.slice(1)} Plan Subscription`,
                order_id: orderData.orderId,
                prefill: {
                    name: '',
                    email: '',
                    contact: ''
                },
                config: {
                    display: {
                        blocks: {
                            banks: {
                                name: 'Pay using Netbanking',
                                instruments: [
                                    {
                                        method: 'netbanking',
                                        banks: ['HDFC', 'ICICI', 'SBI', 'AXIS', 'YES', 'KOTAK']
                                    }
                                ]
                            },
                            card: {
                                name: 'Pay using Cards',
                                instruments: [
                                    {
                                        method: 'card'
                                    }
                                ]
                            },
                            upi: {
                                name: 'Pay using UPI',
                                instruments: [
                                    {
                                        method: 'upi'
                                    }
                                ]
                            }
                        },
                        hide: [
                            {
                                method: 'emi'
                            }
                        ],
                        sequence: ['block.card', 'block.upi', 'block.banks'],
                        preferences: {
                            show_default_blocks: true
                        }
                    }
                },
                theme: {
                    color: '#6366f1',
                    backdrop_color: 'rgba(0, 0, 0, 0.9)'
                },
                modal: {
                    backdropclose: false,
                    escape: true,
                    handleback: true,
                    ondismiss: function() {
                        showAlert('Payment cancelled', 'info');
                    }
                },
                handler: async function(response) {
                    await verifyPayment(response, planId);
                },
                notes: {
                    plan: planId,
                    service: 'MovieCensorAI'
                }
            };

            // Open Razorpay checkout in fullscreen
            const rzp = new Razorpay(options);
            rzp.open();

        } catch (error) {
            console.error('Payment initiation failed:', error);
            showAlert('Failed to initiate payment. Please try again.', 'error');
        } finally {
            proceedBtn.disabled = false;
            proceedBtn.textContent = originalText;
        }
    }

    async function verifyPayment(razorpayResponse, planId) {
        try {
            showAlert('Verifying payment...', 'info');
            
            const verificationData = {
                razorpay_order_id: razorpayResponse.razorpay_order_id,
                razorpay_payment_id: razorpayResponse.razorpay_payment_id,
                razorpay_signature: razorpayResponse.razorpay_signature,
                planId: planId
            };

            const result = await API.verifyPayment(verificationData);
            
            if (result.success) {
                showAlert('🎉 Payment successful! Your subscription is now active.', 'success');
                
                // Redirect to upload section after successful payment
                setTimeout(() => {
                    const uploadSection = document.getElementById('upload');
                    if (uploadSection) {
                        uploadSection.scrollIntoView({ behavior: 'smooth' });
                        showAlert(`Welcome to ${planId} plan! You can now upload videos.`, 'success');
                    }
                }, 3000);
                
            } else {
                throw new Error(result.error || 'Payment verification failed');
            }
            
        } catch (error) {
            console.error('Payment verification failed:', error);
            showAlert('Payment verification failed. Please contact support if money was deducted.', 'error');
        }
    }

    async function updateHealthStatus(health) {
        const isHealthy = health.status === 'healthy';
        
        // Update footer status
        const statusIndicator = document.querySelector('[data-health-status]');
        if (statusIndicator) {
            statusIndicator.innerHTML = `
                <svg class="w-4 h-4 ${isHealthy ? 'text-green-500' : 'text-yellow-500'}" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
                </svg>
                <span>${isHealthy ? 'All systems operational' : 'Some services degraded'}</span>
            `;
        }
        
        // Update header status
        const headerStatus = document.querySelector('[data-header-status]');
        if (headerStatus) {
            const statusColor = isHealthy ? 'bg-green-500' : 'bg-yellow-500';
            const statusText = isHealthy ? 'Online' : 'Degraded';
            headerStatus.innerHTML = `
                <div class="w-2 h-2 ${statusColor} rounded-full"></div>
                <span class="text-gray-600">${statusText}</span>
            `;
        }
    }

    async function loadStats() {
        try {
            const stats = await API.getStats();
            updateStatsDisplay(stats);
        } catch (error) {
            console.error('Failed to load stats:', error);
        }
    }

    function updateStatsDisplay(stats) {
        // Update accuracy rate
        const accuracyEl = document.querySelector('[data-stat="accuracy"]');
        if (accuracyEl) accuracyEl.textContent = `${stats.successRate}%`;

        // Update processing time
        const timeEl = document.querySelector('[data-stat="time"]');
        if (timeEl) timeEl.textContent = stats.totalProcessingTime;

        // Update languages
        const langEl = document.querySelector('[data-stat="languages"]');
        if (langEl) langEl.textContent = `${stats.languages}+`;
    }

    async function loadPricingData() {
        try {
            const pricing = await API.getPricing();
            updatePricingDisplay(pricing);
            console.log('Pricing data loaded:', pricing);
        } catch (error) {
            console.error('Failed to load pricing:', error);
        }
    }

    function updatePricingDisplay(pricing) {
        // Update pricing cards with dynamic data
        pricing.plans.forEach(plan => {
            // Find the pricing card
            const priceElement = document.querySelector(`[data-plan="${plan.id}"] .text-4xl`);
            if (priceElement) {
                priceElement.innerHTML = `$${plan.price}`;
            }

            // Update plan name if needed
            const nameElement = document.querySelector(`[data-plan="${plan.id}"] h3`);
            if (nameElement) {
                nameElement.textContent = plan.name;
            }

            // Update features if they exist in the API response
            if (plan.features) {
                const card = document.querySelector(`[data-plan="${plan.id}"]`);
                if (card) {
                    const featuresList = card.querySelector('ul');
                    if (featuresList && plan.features.length > 0) {
                        // Keep existing features but could enhance with API data
                        console.log(`${plan.name} features:`, plan.features);
                    }
                }
            }
        });
    }

    async function loadQueueStatus() {
        try {
            const queue = await API.getQueueStatus();
            updateQueueDisplay(queue);
        } catch (error) {
            console.error('Failed to load queue status:', error);
        }
    }

    async function loadFeatures() {
        try {
            const features = await API.getFeatures();
            console.log('Features loaded:', features);
            // Features are currently static in HTML, but could be made dynamic
        } catch (error) {
            console.error('Failed to load features:', error);
        }
    }

    function updateQueueDisplay(queue) {
        const queueEl = document.querySelector('[data-queue-status]');
        if (queueEl) {
            queueEl.innerHTML = `
                <div class="text-sm text-gray-600">
                    <span class="font-medium">${queue.activeJobs}</span> processing, 
                    <span class="font-medium">${queue.queuedJobs}</span> in queue
                    <br>
                    Estimated wait: <span class="font-medium">${queue.averageWaitTime}</span>
                </div>
            `;
        }
    }

    // File upload handlers with API integration
    let dragCounter = 0;

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    // Highlight drop area when item is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    // Handle dropped files
    dropZone.addEventListener('drop', handleDrop, false);

    // Handle file input change
    videoInput.addEventListener('change', function() {
        handleFiles(this.files);
    });

    // Form submission with enhanced validation and backend integration
    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        if (!videoInput.files || videoInput.files.length === 0) {
            showAlert('Please select a video file to upload.', 'error');
            return;
        }

        const file = videoInput.files[0];
        
        try {
            // Show initial loading
            showLoadingState();
            
            // Validate file using API
            const validation = await API.validateFile(file);
            
            if (!validation.valid) {
                hideLoadingState();
                showAlert(validation.error, 'error');
                return;
            }

            // Show file validation success
            showAlert(`File validated successfully. Estimated processing time: ${validation.estimatedProcessingTime}`, 'success');
            
            // Submit to backend for processing
            await submitVideoForProcessing(file);
            
        } catch (error) {
            hideLoadingState();
            showAlert('File validation failed. Please try again.', 'error');
            console.error('Validation error:', error);
        }
    });

    async function submitVideoForProcessing(file) {
        try {
            const formData = new FormData();
            formData.append('video', file);
            
            // Get moderation options
            const censorType = document.querySelector('input[name="censorType"]:checked').value;
            formData.append('censorType', censorType);

            // Submit to backend
            const response = await fetch(`${CONFIG.backendUrl}/process`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Backend error: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.job_id) {
                showAlert('Video submitted for processing successfully!', 'success');
                // Start polling for status
                pollJobStatus(result.job_id);
            } else {
                throw new Error('No job ID received from backend');
            }

        } catch (error) {
            hideLoadingState();
            showAlert('Failed to submit video for processing. Please try again.', 'error');
            console.error('Backend submission error:', error);
        }
    }

    async function pollJobStatus(jobId) {
        try {
            const response = await fetch(`${CONFIG.backendUrl}/status/${jobId}`);
            const status = await response.json();
            
            updateProcessingStatus(status);
            
            if (status.status === 'completed') {
                hideLoadingState();
                showAlert('Video processing completed successfully!', 'success');
                // Here you could add download link or show result
            } else if (status.status === 'error') {
                hideLoadingState();
                showAlert('Video processing failed. Please try again.', 'error');
            } else {
                // Continue polling
                setTimeout(() => pollJobStatus(jobId), 2000);
            }
            
        } catch (error) {
            console.error('Status polling error:', error);
            setTimeout(() => pollJobStatus(jobId), 5000); // Retry with longer interval
        }
    }

    function updateProcessingStatus(status) {
        const statusEl = document.getElementById('processingStatus');
        if (statusEl) {
            statusEl.classList.remove('hidden');
            statusEl.innerHTML = `
                <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <div class="flex items-center">
                        <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mr-3"></div>
                        <div>
                            <p class="font-medium text-blue-900">Processing Video</p>
                            <p class="text-sm text-blue-700">Status: ${status.status} ${status.progress ? `- ${status.progress}%` : ''}</p>
                        </div>
                    </div>
                </div>
            `;
        }
    }

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function highlight(e) {
        dropZone.classList.add('drag-over');
    }

    function unhighlight(e) {
        dropZone.classList.remove('drag-over');
    }

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    async function handleFiles(files) {
        if (files.length > 0) {
            const file = files[0];
            
            // Basic client-side validation
            if (!file.type.startsWith('video/')) {
                showAlert('Please select a valid video file.', 'error');
                return;
            }

            try {
                // Get limits from API
                const limits = await API.getLimits();
                
                if (file.size > limits.fileSize.max) {
                    showAlert(`File is too large. Maximum size is ${limits.fileSize.maxFormatted}.`, 'error');
                    return;
                }

                // Update file input
                const dt = new DataTransfer();
                dt.items.add(file);
                videoInput.files = dt.files;

                // Show file info with enhanced details
                await showFileInfo(file, limits);
                
            } catch (error) {
                console.error('Error handling file:', error);
                showAlert('Error processing file information.', 'error');
            }
        }
    }

    async function showFileInfo(file, limits) {
        fileName.textContent = file.name;
        fileSize.textContent = formatFileSize(file.size);
        
        // Add processing time estimate
        const estimatedTime = Math.round((file.size / 1024 / 1024) * 0.5);
        const timeEl = document.createElement('div');
        timeEl.className = 'text-sm text-gray-500';
        timeEl.textContent = `Estimated processing time: ${estimatedTime} minutes`;
        
        if (fileInfo.querySelector('.estimated-time')) {
            fileInfo.querySelector('.estimated-time').remove();
        }
        timeEl.className += ' estimated-time';
        fileInfo.appendChild(timeEl);
        
        fileInfo.classList.remove('hidden');
        
        // Update drop zone with success state
        dropZone.innerHTML = `
            <div class="space-y-4">
                <div class="text-4xl text-green-500">
                    <i class="fas fa-check-circle"></i>
                </div>
                <div>
                    <p class="text-lg font-medium text-gray-900">File Selected</p>
                    <p class="text-gray-600">Click to choose a different file</p>
                    <p class="text-sm text-gray-500 mt-2">Size: ${formatFileSize(file.size)}</p>
                </div>
            </div>
        `;
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    function showLoadingState() {
        submitBtn.disabled = true;
        submitText.textContent = 'Processing...';
        loadingSpinner.classList.remove('hidden');
        processingStatus.classList.remove('hidden');
        
        // Start progress simulation
        simulateProgress();
        
        // Scroll to processing status
        processingStatus.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    function hideLoadingState() {
        submitBtn.disabled = false;
        submitText.textContent = 'Process Video';
        loadingSpinner.classList.add('hidden');
        processingStatus.classList.add('hidden');
    }

    function showAlert(message, type) {
        // Create alert element
        const alertDiv = document.createElement('div');
        
        let bgColor, borderColor, textColor, icon;
        switch(type) {
            case 'error':
                bgColor = 'bg-red-50';
                borderColor = 'border-red-200';
                textColor = 'text-red-700';
                icon = 'fa-exclamation-circle';
                break;
            case 'success':
                bgColor = 'bg-green-50';
                borderColor = 'border-green-200';
                textColor = 'text-green-700';
                icon = 'fa-check-circle';
                break;
            case 'info':
                bgColor = 'bg-blue-50';
                borderColor = 'border-blue-200';
                textColor = 'text-blue-700';
                icon = 'fa-info-circle';
                break;
            case 'warning':
                bgColor = 'bg-yellow-50';
                borderColor = 'border-yellow-200';
                textColor = 'text-yellow-700';
                icon = 'fa-exclamation-triangle';
                break;
            default:
                bgColor = 'bg-gray-50';
                borderColor = 'border-gray-200';
                textColor = 'text-gray-700';
                icon = 'fa-info-circle';
        }
        
        alertDiv.className = `fixed top-4 right-4 p-4 rounded-xl shadow-lg z-50 max-w-md ${bgColor} border ${borderColor} ${textColor}`;
        
        alertDiv.innerHTML = `
            <div class="flex items-start">
                <i class="fas ${icon} mr-3 mt-0.5"></i>
                <div class="flex-1">
                    <p class="text-sm">${message}</p>
                </div>
                <button class="ml-4 text-gray-500 hover:text-gray-700" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(alertDiv);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentElement) {
                alertDiv.remove();
            }
        }, 5000);
    }

    // Enhanced progress simulation with real-time updates
    async function simulateProgress() {
        const progressSteps = [
            { text: 'Uploading video...', progress: 20 },
            { text: 'Extracting audio track...', progress: 40 },
            { text: 'AI transcription in progress...', progress: 60 },
            { text: 'Detecting inappropriate content...', progress: 80 },
            { text: 'Generating censored video...', progress: 95 },
            { text: 'Finalizing and optimizing...', progress: 100 }
        ];

        let currentStep = 0;
        const statusElement = processingStatus.querySelector('span');
        const progressBar = document.querySelector('.progress-bar');

        const updateProgress = async () => {
            if (currentStep < progressSteps.length) {
                const step = progressSteps[currentStep];
                if (statusElement) {
                    statusElement.textContent = step.text;
                }
                if (progressBar) {
                    progressBar.style.width = `${step.progress}%`;
                }

                // Try to get real queue status
                try {
                    const queue = await API.getQueueStatus();
                    updateQueueDisplay(queue);
                } catch (error) {
                    console.log('Queue status update failed:', error);
                }

                currentStep++;
                setTimeout(updateProgress, 2000 + Math.random() * 1000); // Variable timing
            }
        };

        // Start progress simulation
        if (processingStatus && !processingStatus.classList.contains('hidden')) {
            setTimeout(updateProgress, 1000);
        }
    }

    // Contact form integration
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const data = {
                name: formData.get('name'),
                email: formData.get('email'),
                subject: formData.get('subject'),
                message: formData.get('message')
            };

            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            
            try {
                submitBtn.disabled = true;
                submitBtn.textContent = 'Sending...';
                
                const result = await API.submitContact(data);
                
                if (result.success) {
                    showAlert(result.message, 'success');
                    this.reset();
                } else {
                    showAlert(result.error || 'Failed to send message', 'error');
                }
            } catch (error) {
                showAlert('Failed to send message. Please try again.', 'error');
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        });
    }

    // Newsletter subscription
    const newsletterForm = document.getElementById('newsletterForm');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const email = this.querySelector('input[type="email"]').value;
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            
            try {
                submitBtn.disabled = true;
                submitBtn.textContent = 'Subscribing...';
                
                const result = await API.subscribeNewsletter(email);
                
                if (result.success) {
                    showAlert(result.message, 'success');
                    this.reset();
                } else {
                    showAlert(result.error || 'Subscription failed', 'error');
                }
            } catch (error) {
                showAlert('Subscription failed. Please try again.', 'error');
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        });
    }

    // Real-time health monitoring
    setInterval(async () => {
        try {
            const health = await API.checkHealth();
            updateHealthStatus(health);
        } catch (error) {
            console.log('Health check failed:', error);
            // Update status to show disconnected state
            updateOfflineStatus();
        }
    }, 30000); // Check every 30 seconds

    function updateOfflineStatus() {
        const statusIndicator = document.querySelector('[data-health-status]');
        if (statusIndicator) {
            statusIndicator.innerHTML = `
                <svg class="w-4 h-4 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path>
                </svg>
                <span>System offline</span>
            `;
        }
        
        const headerStatus = document.querySelector('[data-header-status]');
        if (headerStatus) {
            headerStatus.innerHTML = `
                <div class="w-2 h-2 bg-red-500 rounded-full"></div>
                <span class="text-gray-600">Offline</span>
            `;
        }
    }

    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Enhanced intersection observer for animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
            }
        });
    }, observerOptions);

    // Observe elements for animation
    document.querySelectorAll('.bg-white, .pricing-card').forEach(el => {
        observer.observe(el);
    });

    // Video player enhancements
    const videos = document.querySelectorAll('video');
    videos.forEach(video => {
        video.addEventListener('loadstart', function() {
            this.style.opacity = '0.5';
        });
        
        video.addEventListener('canplay', function() {
            this.style.opacity = '1';
        });
        
        video.addEventListener('error', function() {
            showAlert('Error loading video. Please try refreshing the page.', 'error');
        });
    });

    // Copy to clipboard functionality
    function copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            showAlert('Copied to clipboard!', 'success');
        }).catch(() => {
            showAlert('Failed to copy to clipboard', 'error');
        });
    }

    // Add copy functionality
    document.addEventListener('click', function(e) {
        if (e.target.matches('[data-copy]')) {
            copyToClipboard(e.target.dataset.copy);
        }
    });

    // Mobile menu toggle
    const mobileMenuButton = document.querySelector('[data-mobile-menu-button]');
    const mobileMenu = document.querySelector('[data-mobile-menu]');
    
    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
        });
    }

    // Periodic stats updates with error handling
    setInterval(async () => {
        try {
            await loadStats();
        } catch (error) {
            console.log('Failed to update stats:', error);
        }
    }, 60000); // Update stats every minute
    
    setInterval(async () => {
        try {
            await loadQueueStatus();
        } catch (error) {
            console.log('Failed to update queue status:', error);
        }
    }, 30000); // Update queue every 30 seconds

    // Add keyboard shortcuts for testing
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + R for refresh (in addition to browser refresh)
        if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
            // Let browser handle the refresh, but log it
            console.log('Manual refresh triggered');
        }
        
        // Ctrl/Cmd + Shift + R for data refresh
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'R') {
            e.preventDefault();
            refreshAllData();
        }
    });

    async function refreshAllData() {
        showAlert('Refreshing data...', 'info');
        try {
            await Promise.all([
                loadStats(),
                loadPricingData(),
                loadQueueStatus(),
                loadFeatures(),
                API.checkHealth().then(updateHealthStatus)
            ]);
            showAlert('Data refreshed successfully!', 'success');
        } catch (error) {
            showAlert('Failed to refresh some data. Please try again.', 'error');
            console.error('Refresh failed:', error);
        }
    }

    console.log('🎬 MovieCensorAI Frontend with Full API Integration Loaded Successfully!');
});

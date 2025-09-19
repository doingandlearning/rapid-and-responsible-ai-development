/**
 * RAG System Capstone - Python Frontend
 * Main JavaScript functionality
 */

// Global state
const AppState = {
	isLoading: false,
	currentView: 'chat',
	messages: [],
	analytics: null,
	settings: {
		similarityThreshold: 0.4,
		maxResults: 10,
		includeMetadata: true
	}
};

// Utility functions
const Utils = {
	// Show toast notification
	showToast(message, type = 'info', duration = 3000) {
		const toast = document.createElement('div');
		toast.className = `toast toast-${type}`;
		toast.innerHTML = `
            <div class="flex items-center justify-between">
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-white hover:text-gray-200">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

		document.body.appendChild(toast);

		setTimeout(() => {
			if (toast.parentElement) {
				toast.remove();
			}
		}, duration);
	},

	// Format timestamp
	formatTimestamp(timestamp) {
		if (!timestamp) return '';
		return new Date(timestamp).toLocaleTimeString();
	},

	// Format file size
	formatFileSize(bytes) {
		if (bytes === 0) return '0 Bytes';
		const k = 1024;
		const sizes = ['Bytes', 'KB', 'MB', 'GB'];
		const i = Math.floor(Math.log(bytes) / Math.log(k));
		return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
	},

	// Debounce function
	debounce(func, wait) {
		let timeout;
		return function executedFunction(...args) {
			const later = () => {
				clearTimeout(timeout);
				func(...args);
			};
			clearTimeout(timeout);
			timeout = setTimeout(later, wait);
		};
	},

	// Throttle function
	throttle(func, limit) {
		let inThrottle;
		return function () {
			const args = arguments;
			const context = this;
			if (!inThrottle) {
				func.apply(context, args);
				inThrottle = true;
				setTimeout(() => inThrottle = false, limit);
			}
		};
	}
};

// API service
const API = {
	baseUrl: '/api',

	async request(endpoint, options = {}) {
		const url = `${this.baseUrl}${endpoint}`;
		const config = {
			headers: {
				'Content-Type': 'application/json',
				...options.headers,
			},
			...options,
		};

		try {
			const response = await fetch(url, config);

			if (!response.ok) {
				const errorData = await response.json().catch(() => ({}));
				throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
			}

			return await response.json();
		} catch (error) {
			console.error('API request failed:', error);
			throw error;
		}
	},

	async sendQuery(query, options = {}) {
		return this.request('/query', {
			method: 'POST',
			body: JSON.stringify({
				query,
				options: {
					max_results: 10,
					similarity_threshold: 0.4,
					include_metadata: true,
					...options
				}
			})
		});
	},

	async getAnalytics() {
		return this.request('/analytics');
	},

	async getDocumentStats() {
		return this.request('/documents/stats');
	},

	async getHealth() {
		return this.request('/health');
	},

	async uploadDocuments(files, projectType) {
		const formData = new FormData();
		files.forEach(file => {
			formData.append('files', file);
		});
		formData.append('project_type', projectType);

		return this.request('/documents/upload', {
			method: 'POST',
			headers: {}, // Let browser set Content-Type for FormData
			body: formData
		});
	}
};

// Chat functionality
const Chat = {
	init() {
		this.bindEvents();
		this.loadSettings();
	},

	bindEvents() {
		// Form submission
		const form = document.getElementById('chat-form');
		if (form) {
			form.addEventListener('submit', this.handleSubmit.bind(this));
		}

		// Input handling
		const input = document.getElementById('message-input');
		if (input) {
			input.addEventListener('keydown', this.handleKeyDown.bind(this));
			input.addEventListener('input', this.handleInput.bind(this));
		}

		// Settings changes
		const similaritySelect = document.getElementById('similarity-threshold');
		const maxResultsSelect = document.getElementById('max-results');

		if (similaritySelect) {
			similaritySelect.addEventListener('change', this.updateSettings.bind(this));
		}

		if (maxResultsSelect) {
			maxResultsSelect.addEventListener('change', this.updateSettings.bind(this));
		}
	},

	handleSubmit(e) {
		e.preventDefault();

		if (AppState.isLoading) return;

		const input = document.getElementById('message-input');
		const query = input.value.trim();

		if (!query) return;

		this.sendMessage(query);
	},

	handleKeyDown(e) {
		if (e.key === 'Enter' && !e.shiftKey) {
			e.preventDefault();
			this.handleSubmit(e);
		}
	},

	handleInput(e) {
		// Auto-resize textarea
		e.target.style.height = 'auto';
		e.target.style.height = e.target.scrollHeight + 'px';
	},

	async sendMessage(query) {
		const input = document.getElementById('message-input');

		// Add user message
		this.addMessage('user', query);

		// Clear input
		input.value = '';
		input.style.height = 'auto';

		// Show loading
		this.showLoading();

		try {
			const response = await API.sendQuery(query, AppState.settings);

			// Add assistant response
			this.addMessage('assistant', response.answer, {
				sources: response.sources || [],
				metadata: response.metadata || {},
				confidence: response.confidence_score,
				responseTime: response.response_time_ms
			});

		} catch (error) {
			console.error('Query failed:', error);
			this.addMessage('error', error.message || 'Sorry, I encountered an error processing your query. Please try again.');
		} finally {
			this.hideLoading();
		}
	},

	addMessage(role, content, metadata = {}) {
		const messagesContainer = document.getElementById('messages-container');
		if (!messagesContainer) return;

		const messageDiv = document.createElement('div');
		messageDiv.className = `flex ${role === 'user' ? 'justify-end' : 'justify-start'} message-bubble`;

		const messageContent = this.renderMessage(role, content, metadata);
		messageDiv.innerHTML = messageContent;

		messagesContainer.appendChild(messageDiv);

		// Scroll to bottom
		messagesContainer.scrollTop = messagesContainer.scrollHeight;

		// Store in state
		AppState.messages.push({
			role,
			content,
			metadata,
			timestamp: new Date().toISOString()
		});
	},

	renderMessage(role, content, metadata) {
		const isUser = role === 'user';
		const isError = role === 'error';

		return `
            <div class="max-w-3xl p-4 rounded-lg border ${this.getMessageStyle(role)}">
                <div class="flex items-center space-x-2 mb-2">
                    ${this.getMessageIcon(role)}
                    <span class="font-medium text-sm">${this.getMessageLabel(role)}</span>
                    <span class="text-xs text-gray-500">${Utils.formatTimestamp(new Date())}</span>
                    ${metadata.confidence ? `<span class="text-xs font-medium ${this.getConfidenceColor(metadata.confidence)}">Confidence: ${Math.round(metadata.confidence * 100)}%</span>` : ''}
                    ${metadata.responseTime ? `<span class="text-xs text-gray-500">(${metadata.responseTime}ms)</span>` : ''}
                </div>
                <div class="prose prose-sm max-w-none">
                    <p class="whitespace-pre-wrap">${content}</p>
                </div>
                ${metadata.sources && metadata.sources.length > 0 ? this.renderSources(metadata.sources) : ''}
                ${metadata.metadata && Object.keys(metadata.metadata).length > 0 ? this.renderMetadata(metadata.metadata) : ''}
            </div>
        `;
	},

	getMessageStyle(role) {
		switch (role) {
			case 'user':
				return 'bg-blue-50 border-blue-200 ml-12';
			case 'assistant':
				return 'bg-green-50 border-green-200 mr-12';
			case 'error':
				return 'bg-red-50 border-red-200 mr-12';
			default:
				return 'bg-gray-50 border-gray-200 mr-12';
		}
	},

	getMessageIcon(role) {
		switch (role) {
			case 'user':
				return '<i class="fas fa-user text-blue-600"></i>';
			case 'assistant':
				return '<i class="fas fa-robot text-green-600"></i>';
			case 'error':
				return '<i class="fas fa-exclamation-triangle text-red-600"></i>';
			default:
				return '<i class="fas fa-robot text-gray-600"></i>';
		}
	},

	getMessageLabel(role) {
		switch (role) {
			case 'user':
				return 'You';
			case 'assistant':
				return 'Assistant';
			case 'error':
				return 'Error';
			default:
				return 'Assistant';
		}
	},

	getConfidenceColor(confidence) {
		if (confidence >= 0.8) return 'text-green-600';
		if (confidence >= 0.6) return 'text-yellow-600';
		return 'text-red-600';
	},

	renderSources(sources) {
		return `
            <div class="mt-3 pt-3 border-t border-gray-200">
                <button onclick="Chat.toggleSources(this)" class="flex items-center space-x-1 text-sm text-gray-600 hover:text-gray-800">
                    <i class="fas fa-chevron-down"></i>
                    <span>Sources (${sources.length})</span>
                </button>
                <div class="sources-content hidden mt-2 space-y-2">
                    ${sources.map((source, idx) => `
                        <div class="bg-white p-3 rounded border text-sm">
                            <div class="flex items-start justify-between">
                                <div class="flex-1">
                                    <div class="font-medium text-gray-900">
                                        ${source.title || source.document_title || `Source ${idx + 1}`}
                                    </div>
                                    ${source.category ? `<div class="text-xs text-gray-500 mt-1">Category: ${source.category}</div>` : ''}
                                    ${source.authority ? `<div class="text-xs text-gray-500">Authority: ${source.authority}</div>` : ''}
                                    ${source.excerpt ? `<div class="mt-2 text-gray-700 italic">"${source.excerpt}"</div>` : ''}
                                    ${source.similarity_score ? `<div class="text-xs text-gray-500 mt-1">Relevance: ${Math.round(source.similarity_score * 100)}%</div>` : ''}
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
	},

	renderMetadata(metadata) {
		return `
            <div class="mt-3 pt-3 border-t border-gray-200">
                <button onclick="Chat.toggleMetadata(this)" class="flex items-center space-x-1 text-xs text-gray-500 hover:text-gray-700">
                    <i class="fas fa-chevron-down"></i>
                    <span>Metadata</span>
                </button>
                <div class="metadata-content hidden mt-2 bg-gray-100 p-2 rounded text-xs font-mono">
                    <pre>${JSON.stringify(metadata, null, 2)}</pre>
                </div>
            </div>
        `;
	},

	toggleSources(button) {
		const content = button.nextElementSibling;
		const icon = button.querySelector('i');

		if (content.classList.contains('hidden')) {
			content.classList.remove('hidden');
			icon.className = 'fas fa-chevron-up';
		} else {
			content.classList.add('hidden');
			icon.className = 'fas fa-chevron-down';
		}
	},

	toggleMetadata(button) {
		const content = button.nextElementSibling;
		const icon = button.querySelector('i');

		if (content.classList.contains('hidden')) {
			content.classList.remove('hidden');
			icon.className = 'fas fa-chevron-up';
		} else {
			content.classList.add('hidden');
			icon.className = 'fas fa-chevron-down';
		}
	},

	showLoading() {
		AppState.isLoading = true;
		const sendButton = document.getElementById('send-button');
		const input = document.getElementById('message-input');

		if (sendButton) {
			sendButton.disabled = true;
			sendButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span>Sending...</span>';
		}

		if (input) {
			input.disabled = true;
		}

		// Add loading message
		const messagesContainer = document.getElementById('messages-container');
		if (messagesContainer) {
			const loadingDiv = document.createElement('div');
			loadingDiv.id = 'loading-message';
			loadingDiv.className = 'flex items-center space-x-2 text-gray-500';
			loadingDiv.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span>Searching documents...</span>';
			messagesContainer.appendChild(loadingDiv);
			messagesContainer.scrollTop = messagesContainer.scrollHeight;
		}
	},

	hideLoading() {
		AppState.isLoading = false;
		const sendButton = document.getElementById('send-button');
		const input = document.getElementById('message-input');

		if (sendButton) {
			sendButton.disabled = false;
			sendButton.innerHTML = '<i class="fas fa-paper-plane"></i> <span>Send</span>';
		}

		if (input) {
			input.disabled = false;
		}

		// Remove loading message
		const loadingMessage = document.getElementById('loading-message');
		if (loadingMessage) {
			loadingMessage.remove();
		}
	},

	updateSettings() {
		const similaritySelect = document.getElementById('similarity-threshold');
		const maxResultsSelect = document.getElementById('max-results');

		if (similaritySelect) {
			AppState.settings.similarityThreshold = parseFloat(similaritySelect.value);
		}

		if (maxResultsSelect) {
			AppState.settings.maxResults = parseInt(maxResultsSelect.value);
		}
	},

	loadSettings() {
		// Load settings from localStorage if available
		const savedSettings = localStorage.getItem('rag-settings');
		if (savedSettings) {
			AppState.settings = { ...AppState.settings, ...JSON.parse(savedSettings) };
		}

		// Apply settings to UI
		const similaritySelect = document.getElementById('similarity-threshold');
		const maxResultsSelect = document.getElementById('max-results');

		if (similaritySelect) {
			similaritySelect.value = AppState.settings.similarityThreshold;
		}

		if (maxResultsSelect) {
			maxResultsSelect.value = AppState.settings.maxResults;
		}
	},

	saveSettings() {
		localStorage.setItem('rag-settings', JSON.stringify(AppState.settings));
	}
};

// Analytics functionality
const Analytics = {
	async load() {
		try {
			const analytics = await API.getAnalytics();
			AppState.analytics = analytics;
			return analytics;
		} catch (error) {
			console.error('Failed to load analytics:', error);
			Utils.showToast('Failed to load analytics data', 'error');
			throw error;
		}
	},

	async refresh() {
		try {
			const analytics = await this.load();
			Utils.showToast('Analytics refreshed', 'success');
			return analytics;
		} catch (error) {
			Utils.showToast('Failed to refresh analytics', 'error');
			throw error;
		}
	}
};

// Settings functionality
const Settings = {
	async uploadFiles(files, projectType) {
		try {
			const result = await API.uploadDocuments(files, projectType);
			Utils.showToast('Files uploaded successfully', 'success');
			return result;
		} catch (error) {
			console.error('Upload failed:', error);
			Utils.showToast(`Upload failed: ${error.message}`, 'error');
			throw error;
		}
	},

	async checkProcessingStatus() {
		try {
			const status = await API.request('/documents/processing/status');
			return status;
		} catch (error) {
			console.error('Failed to check processing status:', error);
			return { status: 'error', error: error.message };
		}
	}
};

// Initialize application
document.addEventListener('DOMContentLoaded', function () {
	// Initialize chat if on chat page
	if (document.getElementById('chat-form')) {
		Chat.init();
	}

	// Initialize analytics if on analytics page
	if (document.getElementById('analytics-container')) {
		Analytics.load();
	}

	// Initialize settings if on settings page
	if (document.getElementById('upload-form')) {
		Settings.init();
	}

	// Global error handling
	window.addEventListener('error', function (e) {
		console.error('Global error:', e.error);
		Utils.showToast('An unexpected error occurred', 'error');
	});

	// Global unhandled promise rejection handling
	window.addEventListener('unhandledrejection', function (e) {
		console.error('Unhandled promise rejection:', e.reason);
		Utils.showToast('An unexpected error occurred', 'error');
	});
});

// Export for global access
window.Chat = Chat;
window.Analytics = Analytics;
window.Settings = Settings;
window.Utils = Utils;
window.API = API;

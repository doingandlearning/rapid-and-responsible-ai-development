const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000/api';

class ApiService {
	async request(endpoint, options = {}) {
		const url = `${API_BASE}${endpoint}`;
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
	}

	// Query the RAG system
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
	}

	// Get system analytics
	async getAnalytics() {
		return this.request('/analytics');
	}

	// Get document statistics
	async getDocumentStats() {
		return this.request('/documents/stats');
	}

	// Search documents with filters
	async searchDocuments(query, filters = {}) {
		return this.request('/documents/search', {
			method: 'POST',
			body: JSON.stringify({
				query,
				filters
			})
		});
	}

	// Get system health
	async getHealth() {
		return this.request('/health');
	}

	// Upload documents (for admin use)
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

	// Get processing status
	async getProcessingStatus() {
		return this.request('/documents/processing/status');
	}
}

// Create singleton instance
const apiService = new ApiService();

// Export individual functions for convenience
export const sendQuery = (query, options) => apiService.sendQuery(query, options);
export const getAnalytics = () => apiService.getAnalytics();
export const getDocumentStats = () => apiService.getDocumentStats();
export const searchDocuments = (query, filters) => apiService.searchDocuments(query, filters);
export const getHealth = () => apiService.getHealth();
export const uploadDocuments = (files, projectType) => apiService.uploadDocuments(files, projectType);
export const getProcessingStatus = () => apiService.getProcessingStatus();

export default apiService;

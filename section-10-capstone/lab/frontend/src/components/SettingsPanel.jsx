import React, { useState } from 'react';
import { Settings, Save, RefreshCw } from 'lucide-react';

const SettingsPanel = () => {
	const [settings, setSettings] = useState({
		projectType: 'literature',
		similarityThreshold: 0.4,
		maxResults: 10,
		apiBaseUrl: 'http://localhost:5000/api'
	});

	const [saved, setSaved] = useState(false);

	const handleSave = () => {
		// TODO: Implement settings persistence
		localStorage.setItem('ragSettings', JSON.stringify(settings));
		setSaved(true);
		setTimeout(() => setSaved(false), 2000);
	};

	const handleReset = () => {
		setSettings({
			projectType: 'literature',
			similarityThreshold: 0.4,
			maxResults: 10,
			apiBaseUrl: 'http://localhost:5000/api'
		});
	};

	return (
		<div className="max-w-2xl mx-auto space-y-6">
			<div className="flex items-center space-x-2">
				<Settings className="h-6 w-6 text-blue-600" />
				<h2 className="text-2xl font-bold text-gray-900">Settings</h2>
			</div>

			<div className="bg-white rounded-lg shadow p-6 space-y-6">
				{/* Project Type */}
				<div>
					<label className="block text-sm font-medium text-gray-700 mb-2">
						Project Type
					</label>
					<select
						value={settings.projectType}
						onChange={(e) => setSettings({ ...settings, projectType: e.target.value })}
						className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
					>
						<option value="literature">Literature Analysis</option>
						<option value="documentation">API Documentation</option>
						<option value="research">Research Papers</option>
						<option value="custom">Whatever You Fancy</option>
					</select>
					<p className="mt-1 text-sm text-gray-500">
						Choose the type of content you're working with
					</p>
				</div>

				{/* Similarity Threshold */}
				<div>
					<label className="block text-sm font-medium text-gray-700 mb-2">
						Similarity Threshold: {settings.similarityThreshold}
					</label>
					<input
						type="range"
						min="0.1"
						max="0.9"
						step="0.1"
						value={settings.similarityThreshold}
						onChange={(e) => setSettings({ ...settings, similarityThreshold: parseFloat(e.target.value) })}
						className="w-full"
					/>
					<p className="mt-1 text-sm text-gray-500">
						Higher values return more relevant but fewer results
					</p>
				</div>

				{/* Max Results */}
				<div>
					<label className="block text-sm font-medium text-gray-700 mb-2">
						Maximum Results
					</label>
					<input
						type="number"
						min="1"
						max="50"
						value={settings.maxResults}
						onChange={(e) => setSettings({ ...settings, maxResults: parseInt(e.target.value) })}
						className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
					/>
					<p className="mt-1 text-sm text-gray-500">
						Maximum number of search results to return
					</p>
				</div>

				{/* API Base URL */}
				<div>
					<label className="block text-sm font-medium text-gray-700 mb-2">
						API Base URL
					</label>
					<input
						type="url"
						value={settings.apiBaseUrl}
						onChange={(e) => setSettings({ ...settings, apiBaseUrl: e.target.value })}
						className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
					/>
					<p className="mt-1 text-sm text-gray-500">
						Backend API endpoint URL
					</p>
				</div>

				{/* Action Buttons */}
				<div className="flex space-x-4 pt-4">
					<button
						onClick={handleSave}
						className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
					>
						<Save className="h-4 w-4 mr-2" />
						{saved ? 'Saved!' : 'Save Settings'}
					</button>

					<button
						onClick={handleReset}
						className="flex items-center px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500"
					>
						<RefreshCw className="h-4 w-4 mr-2" />
						Reset
					</button>
				</div>
			</div>

			{/* System Info */}
			<div className="bg-gray-50 rounded-lg p-6">
				<h3 className="text-lg font-semibold text-gray-900 mb-4">System Information</h3>
				<div className="space-y-2 text-sm text-gray-600">
					<p><strong>Frontend:</strong> React 18 + Vite</p>
					<p><strong>Backend:</strong> Flask + PostgreSQL + pgvector</p>
					<p><strong>Database:</strong> PostgreSQL with JSONB support</p>
					<p><strong>Embeddings:</strong> BGE-M3 via Ollama</p>
				</div>
			</div>
		</div>
	);
};

export default SettingsPanel;

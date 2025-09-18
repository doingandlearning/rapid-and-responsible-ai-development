import React, { useState, useEffect } from 'react';
import ChatInterface from './components/ChatInterface';
import AnalyticsDashboard from './components/AnalyticsDashboard';
import SettingsPanel from './components/SettingsPanel';
import { getAnalytics } from './services/api';
import './index.css';

function App() {
	const [currentView, setCurrentView] = useState('chat');
	const [analytics, setAnalytics] = useState(null);
	const [loading, setLoading] = useState(false);

	useEffect(() => {
		loadAnalytics();
	}, []);

	const loadAnalytics = async () => {
		try {
			setLoading(true);
			const data = await getAnalytics();
			setAnalytics(data);
		} catch (error) {
			console.error('Failed to load analytics:', error);
		} finally {
			setLoading(false);
		}
	};

	const renderCurrentView = () => {
		switch (currentView) {
			case 'chat':
				return <ChatInterface />;
			case 'analytics':
				return <AnalyticsDashboard analytics={analytics} loading={loading} onRefresh={loadAnalytics} />;
			case 'settings':
				return <SettingsPanel />;
			default:
				return <ChatInterface />;
		}
	};

	return (
		<div className="min-h-screen bg-gray-50">
			{/* Navigation Header */}
			<nav className="bg-white shadow-sm border-b">
				<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
					<div className="flex justify-between h-16">
						<div className="flex items-center">
							<h1 className="text-xl font-semibold text-gray-900">
								RAG System Capstone
							</h1>
						</div>
						<div className="flex space-x-4">
							<button
								onClick={() => setCurrentView('chat')}
								className={`px-3 py-2 rounded-md text-sm font-medium ${currentView === 'chat'
									? 'bg-blue-100 text-blue-700'
									: 'text-gray-500 hover:text-gray-700'
									}`}
							>
								Chat
							</button>
							<button
								onClick={() => setCurrentView('analytics')}
								className={`px-3 py-2 rounded-md text-sm font-medium ${currentView === 'analytics'
									? 'bg-blue-100 text-blue-700'
									: 'text-gray-500 hover:text-gray-700'
									}`}
							>
								Analytics
							</button>
							<button
								onClick={() => setCurrentView('settings')}
								className={`px-3 py-2 rounded-md text-sm font-medium ${currentView === 'settings'
									? 'bg-blue-100 text-blue-700'
									: 'text-gray-500 hover:text-gray-700'
									}`}
							>
								Settings
							</button>
						</div>
					</div>
				</div>
			</nav>

			{/* Main Content */}
			<main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
				{renderCurrentView()}
			</main>
		</div>
	);
}

export default App;

import React from 'react';
import { BarChart3, TrendingUp, Clock, Users } from 'lucide-react';

const AnalyticsDashboard = ({ analytics, loading, onRefresh }) => {
	if (loading) {
		return (
			<div className="flex items-center justify-center h-64">
				<div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
			</div>
		);
	}

	if (!analytics) {
		return (
			<div className="text-center py-8">
				<p className="text-gray-500">No analytics data available</p>
				<button
					onClick={onRefresh}
					className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
				>
					Refresh
				</button>
			</div>
		);
	}

	const queryAnalytics = analytics.query_analytics || {};
	const documentStats = analytics.document_stats || {};

	return (
		<div className="space-y-6">
			<div className="flex justify-between items-center">
				<h2 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h2>
				<button
					onClick={onRefresh}
					className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
				>
					Refresh
				</button>
			</div>

			{/* Stats Cards */}
			<div className="grid grid-cols-1 md:grid-cols-4 gap-6">
				<div className="bg-white p-6 rounded-lg shadow">
					<div className="flex items-center">
						<BarChart3 className="h-8 w-8 text-blue-600" />
						<div className="ml-4">
							<p className="text-sm font-medium text-gray-500">Total Queries</p>
							<p className="text-2xl font-semibold text-gray-900">
								{queryAnalytics.total_queries || 0}
							</p>
						</div>
					</div>
				</div>

				<div className="bg-white p-6 rounded-lg shadow">
					<div className="flex items-center">
						<Clock className="h-8 w-8 text-green-600" />
						<div className="ml-4">
							<p className="text-sm font-medium text-gray-500">Avg Response Time</p>
							<p className="text-2xl font-semibold text-gray-900">
								{queryAnalytics.avg_response_time_ms ?
									`${Math.round(queryAnalytics.avg_response_time_ms)}ms` : 'N/A'}
							</p>
						</div>
					</div>
				</div>

				<div className="bg-white p-6 rounded-lg shadow">
					<div className="flex items-center">
						<TrendingUp className="h-8 w-8 text-purple-600" />
						<div className="ml-4">
							<p className="text-sm font-medium text-gray-500">Avg Confidence</p>
							<p className="text-2xl font-semibold text-gray-900">
								{queryAnalytics.avg_confidence ?
									`${Math.round(queryAnalytics.avg_confidence * 100)}%` : 'N/A'}
							</p>
						</div>
					</div>
				</div>

				<div className="bg-white p-6 rounded-lg shadow">
					<div className="flex items-center">
						<Users className="h-8 w-8 text-orange-600" />
						<div className="ml-4">
							<p className="text-sm font-medium text-gray-500">Documents</p>
							<p className="text-2xl font-semibold text-gray-900">
								{documentStats.total_chunks || 0}
							</p>
						</div>
					</div>
				</div>
			</div>

			{/* Document Types */}
			{documentStats.document_types && (
				<div className="bg-white p-6 rounded-lg shadow">
					<h3 className="text-lg font-semibold text-gray-900 mb-4">Document Types</h3>
					<div className="space-y-2">
						{Object.entries(documentStats.document_types).map(([type, count]) => (
							<div key={type} className="flex justify-between items-center">
								<span className="text-gray-600 capitalize">{type.replace('_', ' ')}</span>
								<span className="font-semibold">{count}</span>
							</div>
						))}
					</div>
				</div>
			)}

			{/* Popular Themes */}
			{documentStats.popular_themes && documentStats.popular_themes.length > 0 && (
				<div className="bg-white p-6 rounded-lg shadow">
					<h3 className="text-lg font-semibold text-gray-900 mb-4">Popular Themes</h3>
					<div className="space-y-2">
						{documentStats.popular_themes.slice(0, 5).map((theme, index) => (
							<div key={index} className="flex justify-between items-center">
								<span className="text-gray-600">{theme.theme}</span>
								<span className="font-semibold">{theme.count}</span>
							</div>
						))}
					</div>
				</div>
			)}

			{/* Top Queries */}
			{queryAnalytics.top_queries && queryAnalytics.top_queries.length > 0 && (
				<div className="bg-white p-6 rounded-lg shadow">
					<h3 className="text-lg font-semibold text-gray-900 mb-4">Top Queries</h3>
					<div className="space-y-2">
						{queryAnalytics.top_queries.slice(0, 5).map((query, index) => (
							<div key={index} className="flex justify-between items-center">
								<span className="text-gray-600 truncate">{query.query}</span>
								<span className="font-semibold">{query.frequency}</span>
							</div>
						))}
					</div>
				</div>
			)}
		</div>
	);
};

export default AnalyticsDashboard;

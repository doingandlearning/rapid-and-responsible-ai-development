import React, { useState } from 'react';
import { User, Bot, AlertCircle, ChevronDown, ChevronUp, ExternalLink } from 'lucide-react';

const MessageComponent = ({ message }) => {
	const [showSources, setShowSources] = useState(false);
	const [showMetadata, setShowMetadata] = useState(false);

	const getMessageIcon = () => {
		switch (message.role) {
			case 'user':
				return <User className="h-5 w-5 text-blue-600" />;
			case 'assistant':
				return <Bot className="h-5 w-5 text-green-600" />;
			case 'error':
				return <AlertCircle className="h-5 w-5 text-red-600" />;
			default:
				return <Bot className="h-5 w-5 text-gray-600" />;
		}
	};

	const getMessageStyle = () => {
		switch (message.role) {
			case 'user':
				return 'bg-blue-50 border-blue-200 ml-12';
			case 'assistant':
				return 'bg-green-50 border-green-200 mr-12';
			case 'error':
				return 'bg-red-50 border-red-200 mr-12';
			default:
				return 'bg-gray-50 border-gray-200 mr-12';
		}
	};

	const formatTimestamp = (timestamp) => {
		if (!timestamp) return '';
		return new Date(timestamp).toLocaleTimeString();
	};

	const getConfidenceColor = (confidence) => {
		if (confidence >= 0.8) return 'text-green-600';
		if (confidence >= 0.6) return 'text-yellow-600';
		return 'text-red-600';
	};

	return (
		<div className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
			<div className={`max-w-3xl p-4 rounded-lg border ${getMessageStyle()}`}>
				{/* Message Header */}
				<div className="flex items-center space-x-2 mb-2">
					{getMessageIcon()}
					<span className="font-medium text-sm">
						{message.role === 'user' ? 'You' :
							message.role === 'error' ? 'Error' : 'Assistant'}
					</span>
					{message.timestamp && (
						<span className="text-xs text-gray-500">
							{formatTimestamp(message.timestamp)}
						</span>
					)}
					{message.confidence && (
						<span className={`text-xs font-medium ${getConfidenceColor(message.confidence)}`}>
							Confidence: {(message.confidence * 100).toFixed(0)}%
						</span>
					)}
					{message.responseTime && (
						<span className="text-xs text-gray-500">
							({message.responseTime}ms)
						</span>
					)}
				</div>

				{/* Message Content */}
				<div className="prose prose-sm max-w-none">
					<p className="whitespace-pre-wrap">{message.content}</p>
				</div>

				{/* Sources Section */}
				{message.sources && message.sources.length > 0 && (
					<div className="mt-3 pt-3 border-t border-gray-200">
						<button
							onClick={() => setShowSources(!showSources)}
							className="flex items-center space-x-1 text-sm text-gray-600 hover:text-gray-800"
						>
							{showSources ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
							<span>Sources ({message.sources.length})</span>
						</button>

						{showSources && (
							<div className="mt-2 space-y-2">
								{message.sources.map((source, idx) => (
									<div key={idx} className="bg-white p-3 rounded border text-sm">
										<div className="flex items-start justify-between">
											<div className="flex-1">
												<div className="font-medium text-gray-900">
													{source.title || source.document_title || `Source ${idx + 1}`}
												</div>
												{source.category && (
													<div className="text-xs text-gray-500 mt-1">
														Category: {source.category}
													</div>
												)}
												{source.authority && (
													<div className="text-xs text-gray-500">
														Authority: {source.authority}
													</div>
												)}
												{source.excerpt && (
													<div className="mt-2 text-gray-700 italic">
														"{source.excerpt}"
													</div>
												)}
												{source.similarity_score && (
													<div className="text-xs text-gray-500 mt-1">
														Relevance: {(source.similarity_score * 100).toFixed(0)}%
													</div>
												)}
											</div>
											{source.chunk_id && (
												<button
													onClick={() => {
														// TODO: Implement source viewing functionality
														console.log('View source:', source.chunk_id);
													}}
													className="ml-2 p-1 text-gray-400 hover:text-gray-600"
												>
													<ExternalLink className="h-4 w-4" />
												</button>
											)}
										</div>
									</div>
								))}
							</div>
						)}
					</div>
				)}

				{/* Metadata Section (for debugging) */}
				{message.metadata && Object.keys(message.metadata).length > 0 && (
					<div className="mt-3 pt-3 border-t border-gray-200">
						<button
							onClick={() => setShowMetadata(!showMetadata)}
							className="flex items-center space-x-1 text-xs text-gray-500 hover:text-gray-700"
						>
							{showMetadata ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
							<span>Metadata</span>
						</button>

						{showMetadata && (
							<div className="mt-2 bg-gray-100 p-2 rounded text-xs font-mono">
								<pre>{JSON.stringify(message.metadata, null, 2)}</pre>
							</div>
						)}
					</div>
				)}
			</div>
		</div>
	);
};

export default MessageComponent;

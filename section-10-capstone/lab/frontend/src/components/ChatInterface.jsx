import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, BookOpen, ExternalLink } from 'lucide-react';
import { sendQuery } from '../services/api';
import MessageComponent from './MessageComponent';

const ChatInterface = () => {
	const [messages, setMessages] = useState([
		{
			role: 'assistant',
			content: 'Hello! I\'m your RAG assistant. I can help you search through and analyze documents. What would you like to know?',
			sources: [],
			metadata: {}
		}
	]);
	const [input, setInput] = useState('');
	const [loading, setLoading] = useState(false);
	const [queryOptions, setQueryOptions] = useState({
		maxResults: 10,
		similarityThreshold: 0.4,
		includeMetadata: true
	});
	const messagesEndRef = useRef(null);

	const scrollToBottom = () => {
		messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
	};

	useEffect(() => {
		scrollToBottom();
	}, [messages]);

	const handleSubmit = async (e) => {
		e.preventDefault();
		if (!input.trim() || loading) return;

		const userMessage = {
			role: 'user',
			content: input,
			timestamp: new Date().toISOString()
		};

		setMessages(prev => [...prev, userMessage]);
		setLoading(true);

		try {
			const response = await sendQuery(input, queryOptions);

			const assistantMessage = {
				role: 'assistant',
				content: response.answer,
				sources: response.sources || [],
				metadata: response.metadata || {},
				confidence: response.confidence_score,
				responseTime: response.response_time_ms,
				timestamp: new Date().toISOString()
			};

			setMessages(prev => [...prev, assistantMessage]);
		} catch (error) {
			console.error('Query failed:', error);
			const errorMessage = {
				role: 'error',
				content: 'Sorry, I encountered an error processing your query. Please try again.',
				timestamp: new Date().toISOString()
			};
			setMessages(prev => [...prev, errorMessage]);
		} finally {
			setLoading(false);
			setInput('');
		}
	};

	const handleKeyPress = (e) => {
		if (e.key === 'Enter' && !e.shiftKey) {
			e.preventDefault();
			handleSubmit(e);
		}
	};

	return (
		<div className="flex flex-col h-[calc(100vh-8rem)] bg-white rounded-lg shadow-sm border">
			{/* Chat Header */}
			<div className="flex items-center justify-between p-4 border-b bg-gray-50 rounded-t-lg">
				<div className="flex items-center space-x-2">
					<BookOpen className="h-5 w-5 text-blue-600" />
					<h2 className="text-lg font-semibold text-gray-900">Document Chat</h2>
				</div>
				<div className="flex items-center space-x-2 text-sm text-gray-500">
					<span>Query Options:</span>
					<select
						value={queryOptions.similarityThreshold}
						onChange={(e) => setQueryOptions(prev => ({
							...prev,
							similarityThreshold: parseFloat(e.target.value)
						}))}
						className="px-2 py-1 border rounded text-xs"
					>
						<option value={0.3}>Low (0.3)</option>
						<option value={0.4}>Medium (0.4)</option>
						<option value={0.5}>High (0.5)</option>
					</select>
				</div>
			</div>

			{/* Messages Area */}
			<div className="flex-1 overflow-y-auto p-4 space-y-4">
				{messages.map((message, idx) => (
					<MessageComponent key={idx} message={message} />
				))}
				{loading && (
					<div className="flex items-center space-x-2 text-gray-500">
						<Loader2 className="h-4 w-4 animate-spin" />
						<span>Searching documents...</span>
					</div>
				)}
				<div ref={messagesEndRef} />
			</div>

			{/* Input Area */}
			<div className="p-4 border-t bg-gray-50 rounded-b-lg">
				<form onSubmit={handleSubmit} className="flex space-x-2">
					<div className="flex-1">
						<textarea
							value={input}
							onChange={(e) => setInput(e.target.value)}
							onKeyPress={handleKeyPress}
							placeholder="Ask me anything about the documents..."
							className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
							rows={2}
							disabled={loading}
						/>
					</div>
					<button
						type="submit"
						disabled={loading || !input.trim()}
						className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
					>
						{loading ? (
							<Loader2 className="h-4 w-4 animate-spin" />
						) : (
							<Send className="h-4 w-4" />
						)}
						<span>Send</span>
					</button>
				</form>

				{/* Quick Query Examples */}
				<div className="mt-2 flex flex-wrap gap-2">
					<span className="text-xs text-gray-500">Try:</span>
					{[
						"What are the main themes?",
						"Show me character relationships",
						"Find examples of literary devices"
					].map((example, idx) => (
						<button
							key={idx}
							onClick={() => setInput(example)}
							className="text-xs px-2 py-1 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
						>
							{example}
						</button>
					))}
				</div>
			</div>
		</div>
	);
};

export default ChatInterface;

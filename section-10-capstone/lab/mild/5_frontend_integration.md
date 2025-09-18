# 🌶️ Mild: Frontend Integration - Complete Working Code

**"I like to follow the recipe step-by-step"**

This guide gives you complete, working code for integrating the React frontend with the Flask backend. You'll understand every step of the frontend-backend integration!

## Step 1: Complete API Service

Here's the complete working code for the API service:

```javascript
// src/services/api.js
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000/api';

class ApiService {
    async request(endpoint, options = {}) {
        const url = `${API_BASE}${endpoint}`;
        const config = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
            ...options,
        };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    // Health check
    async healthCheck() {
        return this.request('/health');
    }

    // Query endpoints
    async query(query, options = {}) {
        return this.request('/query', {
            method: 'POST',
            body: JSON.stringify({ query, options })
        });
    }

    async queryWithFilters(query, filters, options = {}) {
        return this.request('/query', {
            method: 'POST',
            body: JSON.stringify({ query, filters, options })
        });
    }

    // Analytics endpoints
    async getAnalytics() {
        return this.request('/analytics');
    }

    async getDocumentStats() {
        return this.request('/documents/stats');
    }

    // Search endpoints
    async searchDocuments(query, options = {}) {
        return this.request('/documents/search', {
            method: 'POST',
            body: JSON.stringify({ query, options })
        });
    }

    // System endpoints
    async getSystemStatus() {
        return this.request('/system/status');
    }

    async validateSystem() {
        return this.request('/system/validate');
    }
}

// Create and export singleton instance
const apiService = new ApiService();
export default apiService;

// Export individual methods for convenience
export const {
    healthCheck,
    query,
    queryWithFilters,
    getAnalytics,
    getDocumentStats,
    searchDocuments,
    getSystemStatus,
    validateSystem
} = apiService;
```

## Step 2: Complete Chat Interface

Here's the complete working code for the chat interface:

```jsx
// src/components/ChatInterface.jsx
import React, { useState, useEffect, useRef } from 'react';
import { Send, Loader2, Bot, User, Copy, Check } from 'lucide-react';
import MessageComponent from './MessageComponent';
import apiService from '../services/api';

const ChatInterface = () => {
    const [messages, setMessages] = useState([]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [settings, setSettings] = useState({
        projectType: 'literature',
        similarityThreshold: 0.4,
        maxResults: 10
    });
    const messagesEndRef = useRef(null);

    // Auto-scroll to bottom when new messages arrive
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // Load settings from localStorage
    useEffect(() => {
        const savedSettings = localStorage.getItem('ragSettings');
        if (savedSettings) {
            setSettings(JSON.parse(savedSettings));
        }
    }, []);

    // Save settings to localStorage
    useEffect(() => {
        localStorage.setItem('ragSettings', JSON.stringify(settings));
    }, [settings]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (!inputValue.trim() || isLoading) return;

        const userMessage = {
            id: Date.now(),
            type: 'user',
            content: inputValue,
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMessage]);
        setInputValue('');
        setIsLoading(true);
        setError(null);

        try {
            const response = await apiService.query(inputValue, settings);
            
            const botMessage = {
                id: Date.now() + 1,
                type: 'bot',
                content: response.answer,
                sources: response.sources || [],
                confidence: response.confidence || 0,
                metadata: response.metadata || {},
                timestamp: new Date()
            };

            setMessages(prev => [...prev, botMessage]);
        } catch (err) {
            setError(err.message);
            const errorMessage = {
                id: Date.now() + 1,
                type: 'bot',
                content: `Sorry, I encountered an error: ${err.message}`,
                isError: true,
                timestamp: new Date()
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleClearChat = () => {
        setMessages([]);
        setError(null);
    };

    const handleSettingsChange = (newSettings) => {
        setSettings(prev => ({ ...prev, ...newSettings }));
    };

    return (
        <div className="flex flex-col h-full">
            {/* Header */}
            <div className="bg-white border-b border-gray-200 p-4">
                <div className="flex justify-between items-center">
                    <h2 className="text-xl font-semibold text-gray-900">RAG Chat</h2>
                    <div className="flex space-x-2">
                        <button
                            onClick={handleClearChat}
                            className="px-3 py-1 text-sm text-gray-600 hover:text-gray-800 border border-gray-300 rounded hover:bg-gray-50"
                        >
                            Clear Chat
                        </button>
                        <div className="text-sm text-gray-500">
                            {settings.projectType} • {Math.round(settings.similarityThreshold * 100)}% threshold
                        </div>
                    </div>
                </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.length === 0 ? (
                    <div className="text-center text-gray-500 mt-8">
                        <Bot className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                        <p className="text-lg font-medium">Welcome to RAG Chat!</p>
                        <p className="text-sm">Ask me anything about your documents.</p>
                    </div>
                ) : (
                    messages.map((message) => (
                        <MessageComponent
                            key={message.id}
                            message={message}
                        />
                    ))
                )}
                
                {isLoading && (
                    <div className="flex items-center space-x-2 text-gray-500">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span>Thinking...</span>
                    </div>
                )}
                
                <div ref={messagesEndRef} />
            </div>

            {/* Error Display */}
            {error && (
                <div className="bg-red-50 border border-red-200 rounded-md p-3 mx-4 mb-4">
                    <p className="text-sm text-red-800">{error}</p>
                </div>
            )}

            {/* Input Form */}
            <div className="bg-white border-t border-gray-200 p-4">
                <form onSubmit={handleSubmit} className="flex space-x-2">
                    <input
                        type="text"
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        placeholder="Ask me anything..."
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        disabled={isLoading}
                    />
                    <button
                        type="submit"
                        disabled={!inputValue.trim() || isLoading}
                        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                    >
                        <Send className="h-4 w-4" />
                        <span>Send</span>
                    </button>
                </form>
            </div>
        </div>
    );
};

export default ChatInterface;
```

## Step 3: Complete Message Component

Here's the complete working code for the message component:

```jsx
// src/components/MessageComponent.jsx
import React, { useState } from 'react';
import { Bot, User, Copy, Check, ExternalLink, Star } from 'lucide-react';

const MessageComponent = ({ message }) => {
    const [copied, setCopied] = useState(false);
    const [showSources, setShowSources] = useState(false);

    const handleCopy = async () => {
        try {
            await navigator.clipboard.writeText(message.content);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error('Failed to copy text:', err);
        }
    };

    const getConfidenceColor = (confidence) => {
        if (confidence >= 0.8) return 'text-green-600';
        if (confidence >= 0.6) return 'text-yellow-600';
        return 'text-red-600';
    };

    const getConfidenceText = (confidence) => {
        if (confidence >= 0.8) return 'High';
        if (confidence >= 0.6) return 'Medium';
        return 'Low';
    };

    return (
        <div className={`flex space-x-3 ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
            {/* Avatar */}
            <div className={`flex-shrink-0 ${message.type === 'user' ? 'order-2' : 'order-1'}`}>
                <div className={`h-8 w-8 rounded-full flex items-center justify-center ${
                    message.type === 'user' 
                        ? 'bg-blue-600 text-white' 
                        : 'bg-gray-100 text-gray-600'
                }`}>
                    {message.type === 'user' ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                </div>
            </div>

            {/* Message Content */}
            <div className={`flex-1 max-w-3xl ${message.type === 'user' ? 'order-1' : 'order-2'}`}>
                <div className={`rounded-lg p-4 ${
                    message.type === 'user'
                        ? 'bg-blue-600 text-white'
                        : message.isError
                        ? 'bg-red-50 border border-red-200 text-red-800'
                        : 'bg-gray-100 text-gray-900'
                }`}>
                    {/* Message Text */}
                    <div className="whitespace-pre-wrap text-sm">
                        {message.content}
                    </div>

                    {/* Bot Message Metadata */}
                    {message.type === 'bot' && !message.isError && (
                        <div className="mt-3 space-y-2">
                            {/* Confidence Score */}
                            {message.confidence !== undefined && (
                                <div className="flex items-center space-x-2 text-xs">
                                    <Star className="h-3 w-3" />
                                    <span className="text-gray-600">Confidence:</span>
                                    <span className={`font-medium ${getConfidenceColor(message.confidence)}`}>
                                        {getConfidenceText(message.confidence)} ({Math.round(message.confidence * 100)}%)
                                    </span>
                                </div>
                            )}

                            {/* Sources */}
                            {message.sources && message.sources.length > 0 && (
                                <div>
                                    <button
                                        onClick={() => setShowSources(!showSources)}
                                        className="text-xs text-blue-600 hover:text-blue-800 flex items-center space-x-1"
                                    >
                                        <span>{showSources ? 'Hide' : 'Show'} Sources ({message.sources.length})</span>
                                    </button>
                                    
                                    {showSources && (
                                        <div className="mt-2 space-y-2">
                                            {message.sources.map((source, index) => (
                                                <div key={index} className="bg-white rounded border p-2 text-xs">
                                                    <div className="font-medium text-gray-900">
                                                        {source.title || `Source ${source.source_number}`}
                                                    </div>
                                                    <div className="text-gray-600">
                                                        by {source.author || 'Unknown Author'}
                                                    </div>
                                                    <div className="text-gray-500 mt-1">
                                                        {source.content_preview}
                                                    </div>
                                                    <div className="flex items-center justify-between mt-2">
                                                        <span className="text-gray-500">
                                                            Relevance: {Math.round(source.similarity_score * 100)}%
                                                        </span>
                                                        <span className="text-gray-500">
                                                            {source.document_type}
                                                        </span>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* Metadata */}
                            {message.metadata && (
                                <div className="text-xs text-gray-500">
                                    <div>Model: {message.metadata.model_used || 'Unknown'}</div>
                                    <div>Context: {message.metadata.search_results || 0} sources</div>
                                </div>
                            )}
                        </div>
                    )}

                    {/* Timestamp */}
                    <div className="text-xs text-gray-500 mt-2">
                        {message.timestamp.toLocaleTimeString()}
                    </div>
                </div>

                {/* Copy Button */}
                <div className="mt-1 flex justify-end">
                    <button
                        onClick={handleCopy}
                        className="text-xs text-gray-500 hover:text-gray-700 flex items-center space-x-1"
                    >
                        {copied ? (
                            <>
                                <Check className="h-3 w-3" />
                                <span>Copied!</span>
                            </>
                        ) : (
                            <>
                                <Copy className="h-3 w-3" />
                                <span>Copy</span>
                            </>
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default MessageComponent;
```

## Step 4: Complete Settings Panel

Here's the complete working code for the settings panel:

```jsx
// src/components/SettingsPanel.jsx
import React, { useState, useEffect } from 'react';
import { Settings, Save, RefreshCw, Database, Search, Brain } from 'lucide-react';

const SettingsPanel = () => {
    const [settings, setSettings] = useState({
        projectType: 'literature',
        similarityThreshold: 0.4,
        maxResults: 10,
        apiBaseUrl: 'http://localhost:5000/api',
        useOpenAI: true,
        model: 'gpt-3.5-turbo'
    });

    const [saved, setSaved] = useState(false);
    const [systemStatus, setSystemStatus] = useState(null);

    // Load settings from localStorage
    useEffect(() => {
        const savedSettings = localStorage.getItem('ragSettings');
        if (savedSettings) {
            setSettings(JSON.parse(savedSettings));
        }
    }, []);

    // Check system status
    useEffect(() => {
        checkSystemStatus();
    }, []);

    const checkSystemStatus = async () => {
        try {
            const response = await fetch(`${settings.apiBaseUrl}/health`);
            if (response.ok) {
                setSystemStatus('connected');
            } else {
                setSystemStatus('error');
            }
        } catch (error) {
            setSystemStatus('disconnected');
        }
    };

    const handleSave = () => {
        localStorage.setItem('ragSettings', JSON.stringify(settings));
        setSaved(true);
        setTimeout(() => setSaved(false), 2000);
    };

    const handleReset = () => {
        setSettings({
            projectType: 'literature',
            similarityThreshold: 0.4,
            maxResults: 10,
            apiBaseUrl: 'http://localhost:5000/api',
            useOpenAI: true,
            model: 'gpt-3.5-turbo'
        });
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'connected': return 'text-green-600';
            case 'error': return 'text-yellow-600';
            case 'disconnected': return 'text-red-600';
            default: return 'text-gray-600';
        }
    };

    const getStatusText = (status) => {
        switch (status) {
            case 'connected': return 'Connected';
            case 'error': return 'Error';
            case 'disconnected': return 'Disconnected';
            default: return 'Unknown';
        }
    };

    return (
        <div className="max-w-4xl mx-auto space-y-6">
            <div className="flex items-center space-x-2">
                <Settings className="h-6 w-6 text-blue-600" />
                <h2 className="text-2xl font-bold text-gray-900">Settings</h2>
            </div>

            {/* System Status */}
            <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">System Status</h3>
                <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-2">
                        <Database className="h-5 w-5 text-gray-500" />
                        <span className="text-sm text-gray-600">Backend:</span>
                        <span className={`text-sm font-medium ${getStatusColor(systemStatus)}`}>
                            {getStatusText(systemStatus)}
                        </span>
                    </div>
                    <button
                        onClick={checkSystemStatus}
                        className="text-sm text-blue-600 hover:text-blue-800 flex items-center space-x-1"
                    >
                        <RefreshCw className="h-4 w-4" />
                        <span>Refresh</span>
                    </button>
                </div>
            </div>

            {/* Project Settings */}
            <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Project Settings</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Project Type */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Project Type
                        </label>
                        <select
                            value={settings.projectType}
                            onChange={(e) => setSettings({...settings, projectType: e.target.value})}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                            <option value="literature">Literature Analysis</option>
                            <option value="documentation">API Documentation</option>
                            <option value="research">Research Papers</option>
                            <option value="custom">Whatever You Fancy</option>
                        </select>
                    </div>

                    {/* Similarity Threshold */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Similarity Threshold: {Math.round(settings.similarityThreshold * 100)}%
                        </label>
                        <input
                            type="range"
                            min="0.1"
                            max="0.9"
                            step="0.1"
                            value={settings.similarityThreshold}
                            onChange={(e) => setSettings({...settings, similarityThreshold: parseFloat(e.target.value)})}
                            className="w-full"
                        />
                        <p className="text-xs text-gray-500 mt-1">
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
                            onChange={(e) => setSettings({...settings, maxResults: parseInt(e.target.value)})}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>

                    {/* API Base URL */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            API Base URL
                        </label>
                        <input
                            type="url"
                            value={settings.apiBaseUrl}
                            onChange={(e) => setSettings({...settings, apiBaseUrl: e.target.value})}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>
                </div>
            </div>

            {/* LLM Settings */}
            <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">LLM Settings</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* LLM Provider */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            LLM Provider
                        </label>
                        <div className="space-y-2">
                            <label className="flex items-center">
                                <input
                                    type="radio"
                                    name="llmProvider"
                                    value="openai"
                                    checked={settings.useOpenAI}
                                    onChange={(e) => setSettings({...settings, useOpenAI: true})}
                                    className="mr-2"
                                />
                                <span className="text-sm">OpenAI (GPT-3.5/4)</span>
                            </label>
                            <label className="flex items-center">
                                <input
                                    type="radio"
                                    name="llmProvider"
                                    value="ollama"
                                    checked={!settings.useOpenAI}
                                    onChange={(e) => setSettings({...settings, useOpenAI: false})}
                                    className="mr-2"
                                />
                                <span className="text-sm">Ollama (Local)</span>
                            </label>
                        </div>
                    </div>

                    {/* Model */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Model
                        </label>
                        <select
                            value={settings.model}
                            onChange={(e) => setSettings({...settings, model: e.target.value})}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                            {settings.useOpenAI ? (
                                <>
                                    <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                                    <option value="gpt-4">GPT-4</option>
                                    <option value="gpt-4-turbo">GPT-4 Turbo</option>
                                </>
                            ) : (
                                <>
                                    <option value="llama2">Llama 2</option>
                                    <option value="codellama">Code Llama</option>
                                    <option value="mistral">Mistral</option>
                                </>
                            )}
                        </select>
                    </div>
                </div>
            </div>

            {/* Action Buttons */}
            <div className="flex space-x-4">
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

            {/* System Info */}
            <div className="bg-gray-50 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">System Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600">
                    <div>
                        <strong>Frontend:</strong> React 18 + Vite
                    </div>
                    <div>
                        <strong>Backend:</strong> Flask + PostgreSQL + pgvector
                    </div>
                    <div>
                        <strong>Database:</strong> PostgreSQL with JSONB support
                    </div>
                    <div>
                        <strong>Embeddings:</strong> BGE-M3 via Ollama
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SettingsPanel;
```

## Step 5: Complete App Integration

Here's the complete working code for the main App component:

```jsx
// src/App.jsx
import React, { useState, useEffect } from 'react';
import ChatInterface from './components/ChatInterface';
import AnalyticsDashboard from './components/AnalyticsDashboard';
import SettingsPanel from './components/SettingsPanel';
import { getAnalytics, getSystemStatus } from './services/api';
import { MessageCircle, BarChart3, Settings, Database } from 'lucide-react';

function App() {
    const [currentView, setCurrentView] = useState('chat');
    const [analytics, setAnalytics] = useState(null);
    const [systemStatus, setSystemStatus] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        loadAnalytics();
        checkSystemStatus();
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

    const checkSystemStatus = async () => {
        try {
            const status = await getSystemStatus();
            setSystemStatus(status);
        } catch (error) {
            console.error('Failed to check system status:', error);
            setSystemStatus({ status: 'error', message: error.message });
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

    const getStatusColor = (status) => {
        if (!systemStatus) return 'text-gray-500';
        if (systemStatus.status === 'healthy') return 'text-green-600';
        if (systemStatus.status === 'warning') return 'text-yellow-600';
        return 'text-red-600';
    };

    const getStatusText = (status) => {
        if (!systemStatus) return 'Unknown';
        if (systemStatus.status === 'healthy') return 'Healthy';
        if (systemStatus.status === 'warning') return 'Warning';
        return 'Error';
    };

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Navigation Header */}
            <nav className="bg-white shadow-sm border-b">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between h-16">
                        <div className="flex items-center">
                            <Database className="h-8 w-8 text-blue-600 mr-3" />
                            <h1 className="text-xl font-semibold text-gray-900">
                                RAG System Capstone
                            </h1>
                        </div>
                        
                        <div className="flex items-center space-x-4">
                            {/* System Status */}
                            <div className="flex items-center space-x-2 text-sm">
                                <div className={`h-2 w-2 rounded-full ${getStatusColor(systemStatus)}`}></div>
                                <span className={getStatusColor(systemStatus)}>
                                    {getStatusText(systemStatus)}
                                </span>
                            </div>
                            
                            {/* Navigation Buttons */}
                            <button
                                onClick={() => setCurrentView('chat')}
                                className={`px-3 py-2 rounded-md text-sm font-medium flex items-center space-x-2 ${
                                    currentView === 'chat'
                                        ? 'bg-blue-100 text-blue-700'
                                        : 'text-gray-500 hover:text-gray-700'
                                }`}
                            >
                                <MessageCircle className="h-4 w-4" />
                                <span>Chat</span>
                            </button>
                            
                            <button
                                onClick={() => setCurrentView('analytics')}
                                className={`px-3 py-2 rounded-md text-sm font-medium flex items-center space-x-2 ${
                                    currentView === 'analytics'
                                        ? 'bg-blue-100 text-blue-700'
                                        : 'text-gray-500 hover:text-gray-700'
                                }`}
                            >
                                <BarChart3 className="h-4 w-4" />
                                <span>Analytics</span>
                            </button>
                            
                            <button
                                onClick={() => setCurrentView('settings')}
                                className={`px-3 py-2 rounded-md text-sm font-medium flex items-center space-x-2 ${
                                    currentView === 'settings'
                                        ? 'bg-blue-100 text-blue-700'
                                        : 'text-gray-500 hover:text-gray-700'
                                }`}
                            >
                                <Settings className="h-4 w-4" />
                                <span>Settings</span>
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
```

## Step 6: Test Your Frontend Integration

Create this test file to verify everything works:

```javascript
// src/test-integration.js
import apiService from './services/api';

const testFrontendIntegration = async () => {
    console.log('🌶️ Testing Frontend Integration...');
    
    try {
        // Test 1: Health Check
        console.log('1. Testing health check...');
        const health = await apiService.healthCheck();
        console.log('   ✅ Health check successful:', health);
        
        // Test 2: System Status
        console.log('2. Testing system status...');
        const status = await apiService.getSystemStatus();
        console.log('   ✅ System status:', status);
        
        // Test 3: Analytics
        console.log('3. Testing analytics...');
        const analytics = await apiService.getAnalytics();
        console.log('   ✅ Analytics loaded:', analytics);
        
        // Test 4: Query
        console.log('4. Testing query...');
        const queryResponse = await apiService.query('What is machine learning?');
        console.log('   ✅ Query successful:', queryResponse);
        
        console.log('🎉 All frontend integration tests passed!');
        
    } catch (error) {
        console.error('❌ Frontend integration test failed:', error);
    }
};

// Run tests if in browser
if (typeof window !== 'undefined') {
    testFrontendIntegration();
}

export default testFrontendIntegration;
```

## Step 7: Run the Frontend

```bash
cd frontend
npm run dev
```

## What You've Learned

✅ **API Integration**: Complete frontend-backend communication
✅ **React Components**: Chat interface, settings, and analytics
✅ **State Management**: Local state and localStorage integration
✅ **Error Handling**: Robust error handling and user feedback
✅ **User Experience**: Modern, responsive UI with real-time updates
✅ **Settings Management**: Persistent settings and configuration
✅ **System Monitoring**: Health checks and status display

## Next Steps

Once your frontend integration is working, you're ready for:
- **System Testing** - End-to-end testing of the complete system
- **Deployment** - Deploy your RAG system to production

## Troubleshooting

**If API calls fail:**
- Check if backend is running on port 5000
- Verify CORS settings in Flask app
- Check network connectivity
- Look at browser console for errors

**If components don't render:**
- Check React component imports
- Verify all dependencies are installed
- Look for JavaScript errors in console
- Check component prop passing

**If settings don't persist:**
- Check localStorage availability
- Verify settings object structure
- Look for JSON parsing errors
- Check browser storage limits

Need help? Check the [🆘 Troubleshooting Guide](../TROUBLESHOOTING.md) or ask questions! 🤝

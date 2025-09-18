# 🌶️🌶️ Medium: Frontend Integration - Guided Experimentation

**"I like to experiment and add my own flavors"**

This guide gives you working examples with some gaps to fill in. You'll learn by doing while having guidance when you need it!

## Step 1: Enhanced API Service

Here's the working structure with some improvements for you to implement:

```javascript
// src/services/api.js
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000/api';

class ApiService {
    constructor() {
        this.cache = new Map();
        this.requestQueue = [];
        this.isProcessingQueue = false;
    }

    async request(endpoint, options = {}) {
        // TODO: Add request caching
        // TODO: Add request queuing
        // TODO: Add retry logic
        // TODO: Add request deduplication
        
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
            
            // TODO: Cache successful responses
            this.cacheResponse(endpoint, data);
            
            return data;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    cacheResponse(endpoint, data) {
        // TODO: Implement intelligent caching
        // - Cache based on endpoint and parameters
        // - Add expiration times
        // - Implement cache invalidation
        // - Add cache size limits
    }

    async query(query, options = {}) {
        // TODO: Add query preprocessing
        // TODO: Add query caching
        // TODO: Add query optimization
        // TODO: Add query analytics
        
        return this.request('/query', {
            method: 'POST',
            body: JSON.stringify({ query, options })
        });
    }

    async queryWithStreaming(query, options = {}) {
        // TODO: Implement streaming queries
        // TODO: Add real-time updates
        // TODO: Add progress tracking
        // TODO: Add error handling
        
        return this.request('/query/stream', {
            method: 'POST',
            body: JSON.stringify({ query, options })
        });
    }

    async getAnalytics() {
        // TODO: Add analytics caching
        // TODO: Add analytics filtering
        // TODO: Add analytics aggregation
        // TODO: Add analytics visualization
        
        return this.request('/analytics');
    }

    // TODO: Add more advanced API methods
    // - Batch operations
    // - Real-time subscriptions
    // - File uploads
    // - Advanced search
}

// Create and export singleton instance
const apiService = new ApiService();
export default apiService;
```

## Step 2: Enhanced Chat Interface

Here's the working structure with some improvements for you to implement:

```jsx
// src/components/ChatInterface.jsx
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Send, Loader2, Bot, User, Copy, Check, Settings, Download } from 'lucide-react';
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
        maxResults: 10,
        enableStreaming: false,
        enableAutoComplete: true
    });
    const [suggestions, setSuggestions] = useState([]);
    const [showSuggestions, setShowSuggestions] = useState(false);
    const messagesEndRef = useRef(null);
    const inputRef = useRef(null);

    // TODO: Add auto-save functionality
    // TODO: Add message search
    // TODO: Add message filtering
    // TODO: Add message export

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    useEffect(() => {
        const savedSettings = localStorage.getItem('ragSettings');
        if (savedSettings) {
            setSettings(JSON.parse(savedSettings));
        }
    }, []);

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
            // TODO: Add streaming support
            // TODO: Add progress tracking
            // TODO: Add response validation
            // TODO: Add error recovery
            
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

    const handleInputChange = (e) => {
        const value = e.target.value;
        setInputValue(value);
        
        // TODO: Implement auto-complete
        // TODO: Add query suggestions
        // TODO: Add query validation
        // TODO: Add query history
        
        if (value.length > 2) {
            // Generate suggestions based on input
            generateSuggestions(value);
        } else {
            setSuggestions([]);
            setShowSuggestions(false);
        }
    };

    const generateSuggestions = async (query) => {
        // TODO: Implement suggestion generation
        // - Use query history
        // - Use popular queries
        // - Use auto-complete API
        // - Use machine learning
        
        try {
            const suggestions = await apiService.getSuggestions(query);
            setSuggestions(suggestions);
            setShowSuggestions(true);
        } catch (error) {
            console.error('Failed to generate suggestions:', error);
        }
    };

    const handleSuggestionClick = (suggestion) => {
        setInputValue(suggestion);
        setShowSuggestions(false);
        inputRef.current?.focus();
    };

    const handleClearChat = () => {
        setMessages([]);
        setError(null);
    };

    const handleExportChat = () => {
        // TODO: Implement chat export
        // - Export to JSON
        // - Export to Markdown
        // - Export to PDF
        // - Export to CSV
        
        const chatData = {
            messages,
            settings,
            timestamp: new Date().toISOString()
        };
        
        const blob = new Blob([JSON.stringify(chatData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `chat-export-${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
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
                            onClick={handleExportChat}
                            className="px-3 py-1 text-sm text-gray-600 hover:text-gray-800 border border-gray-300 rounded hover:bg-gray-50 flex items-center space-x-1"
                        >
                            <Download className="h-4 w-4" />
                            <span>Export</span>
                        </button>
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

            {/* Suggestions */}
            {showSuggestions && suggestions.length > 0 && (
                <div className="bg-white border-t border-gray-200 p-2">
                    <div className="flex flex-wrap gap-2">
                        {suggestions.map((suggestion, index) => (
                            <button
                                key={index}
                                onClick={() => handleSuggestionClick(suggestion)}
                                className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-full"
                            >
                                {suggestion}
                            </button>
                        ))}
                    </div>
                </div>
            )}

            {/* Error Display */}
            {error && (
                <div className="bg-red-50 border border-red-200 rounded-md p-3 mx-4 mb-4">
                    <p className="text-sm text-red-800">{error}</p>
                </div>
            )}

            {/* Input Form */}
            <div className="bg-white border-t border-gray-200 p-4">
                <form onSubmit={handleSubmit} className="flex space-x-2">
                    <div className="flex-1 relative">
                        <input
                            ref={inputRef}
                            type="text"
                            value={inputValue}
                            onChange={handleInputChange}
                            placeholder="Ask me anything..."
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            disabled={isLoading}
                        />
                    </div>
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

## Step 3: Enhanced Message Component

Here's the working structure with some improvements for you to implement:

```jsx
// src/components/MessageComponent.jsx
import React, { useState, useRef, useEffect } from 'react';
import { Bot, User, Copy, Check, ExternalLink, Star, ThumbsUp, ThumbsDown, Flag } from 'lucide-react';

const MessageComponent = ({ message }) => {
    const [copied, setCopied] = useState(false);
    const [showSources, setShowSources] = useState(false);
    const [userFeedback, setUserFeedback] = useState(null);
    const [isExpanded, setIsExpanded] = useState(false);
    const contentRef = useRef(null);

    // TODO: Add message analytics
    // TODO: Add message search
    // TODO: Add message editing
    // TODO: Add message sharing

    useEffect(() => {
        // Auto-expand long messages
        if (contentRef.current && contentRef.current.scrollHeight > 200) {
            setIsExpanded(false);
        }
    }, [message.content]);

    const handleCopy = async () => {
        try {
            await navigator.clipboard.writeText(message.content);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error('Failed to copy text:', err);
        }
    };

    const handleFeedback = async (feedback) => {
        // TODO: Implement feedback system
        // - Send feedback to backend
        // - Track user satisfaction
        // - Improve system based on feedback
        // - Display feedback analytics
        
        setUserFeedback(feedback);
        
        try {
            await fetch('/api/feedback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    messageId: message.id,
                    feedback: feedback,
                    timestamp: new Date().toISOString()
                })
            });
        } catch (error) {
            console.error('Failed to send feedback:', error);
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

    const shouldTruncate = contentRef.current && contentRef.current.scrollHeight > 200;

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
                    <div 
                        ref={contentRef}
                        className={`whitespace-pre-wrap text-sm ${
                            shouldTruncate && !isExpanded ? 'line-clamp-6' : ''
                        }`}
                    >
                        {message.content}
                    </div>

                    {/* Expand/Collapse Button */}
                    {shouldTruncate && (
                        <button
                            onClick={() => setIsExpanded(!isExpanded)}
                            className="text-xs text-blue-600 hover:text-blue-800 mt-2"
                        >
                            {isExpanded ? 'Show less' : 'Show more'}
                        </button>
                    )}

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

                            {/* User Feedback */}
                            {message.type === 'bot' && (
                                <div className="flex items-center space-x-2">
                                    <span className="text-xs text-gray-600">Was this helpful?</span>
                                    <button
                                        onClick={() => handleFeedback('positive')}
                                        className={`p-1 rounded ${
                                            userFeedback === 'positive' 
                                                ? 'bg-green-100 text-green-600' 
                                                : 'text-gray-400 hover:text-green-600'
                                        }`}
                                    >
                                        <ThumbsUp className="h-3 w-3" />
                                    </button>
                                    <button
                                        onClick={() => handleFeedback('negative')}
                                        className={`p-1 rounded ${
                                            userFeedback === 'negative' 
                                                ? 'bg-red-100 text-red-600' 
                                                : 'text-gray-400 hover:text-red-600'
                                        }`}
                                    >
                                        <ThumbsDown className="h-3 w-3" />
                                    </button>
                                    <button
                                        onClick={() => handleFeedback('flag')}
                                        className={`p-1 rounded ${
                                            userFeedback === 'flag' 
                                                ? 'bg-yellow-100 text-yellow-600' 
                                                : 'text-gray-400 hover:text-yellow-600'
                                        }`}
                                    >
                                        <Flag className="h-3 w-3" />
                                    </button>
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

                {/* Action Buttons */}
                <div className="mt-1 flex justify-end space-x-2">
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
                    
                    {/* TODO: Add more action buttons */}
                    {/* - Share message */}
                    {/* - Bookmark message */}
                    {/* - Edit message */}
                    {/* - Delete message */}
                </div>
            </div>
        </div>
    );
};

export default MessageComponent;
```

## Step 4: Test Your Enhanced Features

Create a comprehensive test:

```javascript
// src/test-enhanced-features.js
import apiService from './services/api';

const testEnhancedFeatures = async () => {
    console.log('🌶️🌶️ Testing Enhanced Frontend Features...');
    
    // Test your enhanced API features
    // Test your streaming functionality
    // Test your caching system
    // Test your analytics integration
    // Test your user feedback system
    // Add your own tests!
    
    console.log('🎉 Enhanced features tested!');
};

export default testEnhancedFeatures;
```

## What You've Learned

✅ **Enhanced API**: Caching, queuing, and optimization
✅ **Advanced UI**: Streaming, suggestions, and feedback
✅ **User Experience**: Auto-complete, export, and analytics
✅ **Performance**: Optimization and monitoring
✅ **Interactivity**: Real-time updates and user engagement

## Next Steps

Once you've implemented the enhanced features, you're ready for:
- **[Medium: System Testing](6_system_testing.md)** - End-to-end testing
- **[Medium: Deployment](7_deployment.md)** - Production deployment

## Challenges to Try

1. **Performance**: How can you make the frontend 10x faster?
2. **User Experience**: What features would improve usability?
3. **Analytics**: What metrics help you understand user behavior?
4. **Innovation**: What new features can you invent?

## Getting Help

- Check the [Troubleshooting Guide](../TROUBLESHOOTING.md)
- Ask questions in the discussion forum
- Look at the [Spicy version](../spicy/5_frontend_integration.md) for inspiration
- Experiment with different approaches!

Remember: There's no single "right" way to implement these features. Try different approaches and see what works best for your project! 🚀

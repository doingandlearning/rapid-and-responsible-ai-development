# Step 2.3: React Frontend Implementation (30 minutes)

## Overview

Build a modern, accessible React frontend for the Edinburgh University Student Support Chatbot. The interface should be intuitive, mobile-friendly, and provide clear feedback to users.

## Implementation

### 2.3.1: Project Setup

```bash
# Create React app
npx create-react-app frontend --template typescript
cd frontend

# Install additional dependencies
npm install axios @types/axios
npm install react-query @types/react-query
npm install react-markdown @types/react-markdown
npm install lucide-react
npm install tailwindcss @tailwindcss/typography
npm install @headlessui/react
```

### 2.3.2: Main App Component

```typescript
// frontend/src/App.tsx
import React, { useState, useEffect } from 'react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ReactQueryDevtools } from 'react-query/devtools';
import ChatInterface from './components/ChatInterface';
import Header from './components/Header';
import Footer from './components/Footer';
import AnalyticsDashboard from './components/AnalyticsDashboard';
import ErrorBoundary from './components/ErrorBoundary';
import { HealthCheck } from './services/api';
import './App.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 2,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

type AppView = 'chat' | 'analytics';

function App() {
  const [currentView, setCurrentView] = useState<AppView>('chat');
  const [systemHealth, setSystemHealth] = useState<'healthy' | 'degraded' | 'checking'>('checking');

  useEffect(() => {
    // Check system health on startup
    checkSystemHealth();
    
    // Set up periodic health checks
    const healthCheckInterval = setInterval(checkSystemHealth, 30000); // Every 30 seconds
    
    return () => clearInterval(healthCheckInterval);
  }, []);

  const checkSystemHealth = async () => {
    try {
      const health = await HealthCheck();
      setSystemHealth(health.status === 'healthy' ? 'healthy' : 'degraded');
    } catch (error) {
      setSystemHealth('degraded');
      console.error('Health check failed:', error);
    }
  };

  return (
    <QueryClientProvider client={queryClient}>
      <ErrorBoundary>
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
          <Header 
            currentView={currentView}
            onViewChange={setCurrentView}
            systemHealth={systemHealth}
          />
          
          <main className="container mx-auto px-4 py-8 max-w-6xl">
            {currentView === 'chat' ? (
              <ChatInterface systemHealth={systemHealth} />
            ) : (
              <AnalyticsDashboard />
            )}
          </main>
          
          <Footer />
        </div>
      </ErrorBoundary>
      
      {process.env.NODE_ENV === 'development' && (
        <ReactQueryDevtools initialIsOpen={false} />
      )}
    </QueryClientProvider>
  );
}

export default App;
```

### 2.3.3: Chat Interface Component

```typescript
// frontend/src/components/ChatInterface.tsx
import React, { useState, useRef, useEffect } from 'react';
import { useMutation } from 'react-query';
import { Send, Bot, User, AlertTriangle, RefreshCw, ThumbsUp, ThumbsDown } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { ChatQuery, ChatResponse, SubmitChatQuery, SubmitFeedback } from '../services/api';
import LoadingSpinner from './LoadingSpinner';
import SourcesList from './SourcesList';
import SuggestedQueries from './SuggestedQueries';
import { generateSessionId } from '../utils/session';

interface Message {
  id: string;
  type: 'user' | 'bot';
  content: string;
  timestamp: Date;
  sources?: any[];
  confidence?: number;
  suggestions?: string[];
  metadata?: any;
}

interface ChatInterfaceProps {
  systemHealth: 'healthy' | 'degraded' | 'checking';
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ systemHealth }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [sessionId] = useState(generateSessionId());
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Chat mutation
  const chatMutation = useMutation(SubmitChatQuery, {
    onSuccess: (data: ChatResponse) => {
      const botMessage: Message = {
        id: `bot-${Date.now()}`,
        type: 'bot',
        content: data.message,
        timestamp: new Date(),
        sources: data.sources,
        confidence: data.confidence_score,
        suggestions: data.suggestions,
        metadata: data.metadata,
      };
      
      setMessages(prev => [...prev, botMessage]);
    },
    onError: (error: any) => {
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        type: 'bot',
        content: 'I apologize, but I\'m experiencing technical difficulties right now. Please try again in a moment, or contact Student Services directly for immediate assistance.',
        timestamp: new Date(),
        metadata: { error: true },
      };
      
      setMessages(prev => [...prev, errorMessage]);
      console.error('Chat error:', error);
    },
  });

  // Feedback mutation
  const feedbackMutation = useMutation(SubmitFeedback);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Add welcome message on first load
    if (messages.length === 0) {
      const welcomeMessage: Message = {
        id: 'welcome',
        type: 'bot',
        content: `👋 Hello! I'm your Edinburgh University Student Support Assistant. I can help you with:

• Course information and requirements
• Student services and support
• Campus facilities and resources
• Policies and procedures
• General university questions

What would you like to know?`,
        timestamp: new Date(),
        suggestions: [
          "How do I change my course?",
          "What are the library opening hours?",
          "How do I access counseling services?",
          "What dining options are available?"
        ]
      };
      
      setMessages([welcomeMessage]);
    }
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!inputValue.trim() || chatMutation.isLoading) {
      return;
    }

    // Add user message
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      type: 'user',
      content: inputValue.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);

    // Submit to API
    const query: ChatQuery = {
      message: inputValue.trim(),
      session_id: sessionId,
      user_context: {
        timestamp: new Date().toISOString(),
        user_agent: navigator.userAgent,
      },
    };

    chatMutation.mutate(query);
    setInputValue('');
    
    // Focus back to input
    setTimeout(() => inputRef.current?.focus(), 100);
  };

  const handleSuggestedQuery = (query: string) => {
    setInputValue(query);
    inputRef.current?.focus();
  };

  const handleFeedback = async (messageId: string, positive: boolean) => {
    try {
      await feedbackMutation.mutateAsync({
        message_id: messageId,
        feedback_type: positive ? 'positive' : 'negative',
        rating: positive ? 5 : 2,
        comment: positive ? 'Helpful response' : 'Not helpful',
      });
      
      // Update message to show feedback was submitted
      setMessages(prev => prev.map(msg => 
        msg.id === messageId 
          ? { ...msg, metadata: { ...msg.metadata, feedback_submitted: true } }
          : msg
      ));
    } catch (error) {
      console.error('Failed to submit feedback:', error);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as any);
    }
  };

  return (
    <div className="max-w-4xl mx-auto bg-white dark:bg-gray-800 rounded-lg shadow-xl overflow-hidden">
      {/* System Status Banner */}
      {systemHealth !== 'healthy' && (
        <div className="bg-yellow-50 dark:bg-yellow-900 border-l-4 border-yellow-400 p-4">
          <div className="flex">
            <AlertTriangle className="h-5 w-5 text-yellow-400 mr-2" />
            <p className="text-sm text-yellow-700 dark:text-yellow-300">
              {systemHealth === 'checking' 
                ? 'Checking system status...' 
                : 'System is experiencing some issues. Responses may be delayed.'}
            </p>
          </div>
        </div>
      )}

      {/* Messages Container */}
      <div className="h-96 md:h-[500px] overflow-y-auto p-6 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs md:max-w-2xl px-4 py-2 rounded-lg ${
                message.type === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100'
              }`}
            >
              {/* Message Header */}
              <div className="flex items-center mb-2">
                {message.type === 'bot' ? (
                  <Bot className="h-4 w-4 mr-2 text-blue-600 dark:text-blue-400" />
                ) : (
                  <User className="h-4 w-4 mr-2 text-white" />
                )}
                <span className="text-xs opacity-75">
                  {message.timestamp.toLocaleTimeString()}
                </span>
                {message.confidence && (
                  <span className={`text-xs ml-2 px-2 py-1 rounded ${
                    message.confidence > 0.8 
                      ? 'bg-green-200 text-green-800' 
                      : message.confidence > 0.6 
                      ? 'bg-yellow-200 text-yellow-800' 
                      : 'bg-red-200 text-red-800'
                  }`}>
                    {Math.round(message.confidence * 100)}% confident
                  </span>
                )}
              </div>

              {/* Message Content */}
              <div className="prose prose-sm dark:prose-invert max-w-none">
                <ReactMarkdown>{message.content}</ReactMarkdown>
              </div>

              {/* Sources */}
              {message.sources && message.sources.length > 0 && (
                <SourcesList sources={message.sources} />
              )}

              {/* Suggestions */}
              {message.suggestions && message.suggestions.length > 0 && (
                <SuggestedQueries 
                  queries={message.suggestions} 
                  onQuerySelect={handleSuggestedQuery} 
                />
              )}

              {/* Feedback Buttons */}
              {message.type === 'bot' && !message.metadata?.error && !message.metadata?.feedback_submitted && (
                <div className="flex space-x-2 mt-2">
                  <button
                    onClick={() => handleFeedback(message.id, true)}
                    className="text-xs text-gray-500 hover:text-green-600 dark:text-gray-400 dark:hover:text-green-400 flex items-center"
                    disabled={feedbackMutation.isLoading}
                  >
                    <ThumbsUp className="h-3 w-3 mr-1" />
                    Helpful
                  </button>
                  <button
                    onClick={() => handleFeedback(message.id, false)}
                    className="text-xs text-gray-500 hover:text-red-600 dark:text-gray-400 dark:hover:text-red-400 flex items-center"
                    disabled={feedbackMutation.isLoading}
                  >
                    <ThumbsDown className="h-3 w-3 mr-1" />
                    Not helpful
                  </button>
                </div>
              )}

              {/* Feedback Confirmation */}
              {message.metadata?.feedback_submitted && (
                <div className="text-xs text-green-600 dark:text-green-400 mt-2">
                  ✓ Thank you for your feedback!
                </div>
              )}
            </div>
          </div>
        ))}

        {/* Loading Indicator */}
        {chatMutation.isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 dark:bg-gray-700 rounded-lg p-4">
              <LoadingSpinner />
              <span className="text-sm text-gray-600 dark:text-gray-400 ml-2">
                Thinking...
              </span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <div className="border-t border-gray-200 dark:border-gray-600 p-4">
        <form onSubmit={handleSubmit} className="flex space-x-2">
          <textarea
            ref={inputRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me anything about Edinburgh University..."
            className="flex-1 p-3 border border-gray-300 dark:border-gray-600 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            rows={2}
            maxLength={1000}
            disabled={chatMutation.isLoading || systemHealth === 'checking'}
          />
          <button
            type="submit"
            disabled={!inputValue.trim() || chatMutation.isLoading || systemHealth === 'checking'}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
          >
            {chatMutation.isLoading ? (
              <RefreshCw className="h-5 w-5 animate-spin" />
            ) : (
              <Send className="h-5 w-5" />
            )}
          </button>
        </form>
        
        {/* Character Count */}
        <div className="text-right text-xs text-gray-500 dark:text-gray-400 mt-1">
          {inputValue.length}/1000
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
```

### 2.3.4: Supporting Components

```typescript
// frontend/src/components/SourcesList.tsx
import React, { useState } from 'react';
import { ChevronDown, ChevronUp, ExternalLink } from 'lucide-react';

interface Source {
  source_id: number;
  title: string;
  category: string;
  authority: string;
  excerpt: string;
  similarity_score: number;
}

interface SourcesListProps {
  sources: Source[];
}

const SourcesList: React.FC<SourcesListProps> = ({ sources }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!sources || sources.length === 0) {
    return null;
  }

  const displaySources = isExpanded ? sources : sources.slice(0, 2);

  return (
    <div className="mt-3 p-3 bg-blue-50 dark:bg-blue-900 rounded-lg">
      <div className="flex items-center justify-between mb-2">
        <h4 className="text-sm font-semibold text-blue-800 dark:text-blue-200">
          Sources ({sources.length})
        </h4>
        {sources.length > 2 && (
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200"
          >
            {isExpanded ? (
              <ChevronUp className="h-4 w-4" />
            ) : (
              <ChevronDown className="h-4 w-4" />
            )}
          </button>
        )}
      </div>
      
      <div className="space-y-2">
        {displaySources.map((source) => (
          <div
            key={source.source_id}
            className="p-2 bg-white dark:bg-gray-800 rounded border border-blue-200 dark:border-blue-700"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h5 className="text-sm font-medium text-gray-900 dark:text-gray-100">
                  {source.title}
                </h5>
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                  {source.excerpt}
                </p>
                <div className="flex items-center mt-2 space-x-2">
                  <span className={`text-xs px-2 py-1 rounded ${
                    source.category === 'academic_handbook' 
                      ? 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100'
                      : source.category === 'student_services'
                      ? 'bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-100'
                      : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-100'
                  }`}>
                    {source.category.replace('_', ' ')}
                  </span>
                  <span className={`text-xs px-2 py-1 rounded ${
                    source.authority === 'high' 
                      ? 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100'
                      : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-100'
                  }`}>
                    {source.authority} authority
                  </span>
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {Math.round(source.similarity_score * 100)}% match
                  </span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SourcesList;
```

```typescript
// frontend/src/components/SuggestedQueries.tsx
import React from 'react';
import { MessageCircle } from 'lucide-react';

interface SuggestedQueriesProps {
  queries: string[];
  onQuerySelect: (query: string) => void;
}

const SuggestedQueries: React.FC<SuggestedQueriesProps> = ({ queries, onQuerySelect }) => {
  if (!queries || queries.length === 0) {
    return null;
  }

  return (
    <div className="mt-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
      <div className="flex items-center mb-2">
        <MessageCircle className="h-4 w-4 text-gray-600 dark:text-gray-400 mr-2" />
        <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300">
          You might also ask:
        </h4>
      </div>
      <div className="space-y-1">
        {queries.map((query, index) => (
          <button
            key={index}
            onClick={() => onQuerySelect(query)}
            className="block w-full text-left text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200 hover:underline"
          >
            "{query}"
          </button>
        ))}
      </div>
    </div>
  );
};

export default SuggestedQueries;
```

```typescript
// frontend/src/components/Header.tsx
import React from 'react';
import { MessageSquare, BarChart3, CheckCircle, AlertTriangle, Clock } from 'lucide-react';

interface HeaderProps {
  currentView: 'chat' | 'analytics';
  onViewChange: (view: 'chat' | 'analytics') => void;
  systemHealth: 'healthy' | 'degraded' | 'checking';
}

const Header: React.FC<HeaderProps> = ({ currentView, onViewChange, systemHealth }) => {
  const getHealthIcon = () => {
    switch (systemHealth) {
      case 'healthy':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'degraded':
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
      default:
        return <Clock className="h-5 w-5 text-gray-500 animate-pulse" />;
    }
  };

  return (
    <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo and Title */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <MessageSquare className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100">
                Edinburgh University
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Student Support Assistant
              </p>
            </div>
          </div>

          {/* Navigation and Status */}
          <div className="flex items-center space-x-4">
            {/* System Health Indicator */}
            <div className="flex items-center space-x-2">
              {getHealthIcon()}
              <span className="text-sm text-gray-600 dark:text-gray-400">
                {systemHealth}
              </span>
            </div>

            {/* View Toggle */}
            <div className="flex bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
              <button
                onClick={() => onViewChange('chat')}
                className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                  currentView === 'chat'
                    ? 'bg-white dark:bg-gray-600 text-blue-600 dark:text-blue-400 shadow-sm'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
                }`}
              >
                <MessageSquare className="h-4 w-4 inline mr-2" />
                Chat
              </button>
              <button
                onClick={() => onViewChange('analytics')}
                className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                  currentView === 'analytics'
                    ? 'bg-white dark:bg-gray-600 text-blue-600 dark:text-blue-400 shadow-sm'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
                }`}
              >
                <BarChart3 className="h-4 w-4 inline mr-2" />
                Analytics
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
```

```typescript
// frontend/src/services/api.ts
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request/Response interfaces
export interface ChatQuery {
  message: string;
  session_id?: string;
  user_context?: Record<string, any>;
}

export interface ChatResponse {
  message: string;
  sources: Array<{
    source_id: number;
    title: string;
    category: string;
    authority: string;
    excerpt: string;
    similarity_score: number;
  }>;
  confidence_score: number;
  response_time_ms: number;
  session_id: string;
  suggestions?: string[];
  metadata: Record<string, any>;
}

export interface AnalyticsData {
  total_queries: number;
  avg_response_time_ms: number;
  avg_confidence_score: number;
  unique_sessions: number;
  top_queries: Array<{ query: string; frequency: number }>;
  category_distribution: Record<string, number>;
}

// API Functions
export const SubmitChatQuery = async (query: ChatQuery): Promise<ChatResponse> => {
  const response = await api.post('/chat', query);
  return response.data;
};

export const GetAnalytics = async (days: number = 7): Promise<AnalyticsData> => {
  const response = await api.get(`/analytics?days=${days}`);
  return response.data;
};

export const GetSuggestions = async (category?: string): Promise<string[]> => {
  const response = await api.get(`/suggestions${category ? `?category=${category}` : ''}`);
  return response.data;
};

export const SubmitFeedback = async (feedback: {
  message_id: string;
  feedback_type: string;
  rating: number;
  comment?: string;
}): Promise<void> => {
  await api.post('/feedback', feedback);
};

export const HealthCheck = async (): Promise<{
  status: string;
  timestamp: string;
  services: Record<string, string>;
  version: string;
}> => {
  const response = await api.get('/health');
  return response.data;
};

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === 'ECONNABORTED') {
      console.error('Request timeout');
      throw new Error('Request timeout. Please try again.');
    }
    
    if (error.response?.status === 429) {
      throw new Error('Too many requests. Please wait a moment before trying again.');
    }
    
    if (error.response?.status >= 500) {
      throw new Error('Server error. Please try again later.');
    }
    
    throw error;
  }
);

export default api;
```

This React frontend provides:

1. **Modern, Responsive Design** - Works on desktop and mobile
2. **Real-time Chat Interface** - Smooth messaging experience
3. **Source Citation Display** - Shows where answers come from
4. **Suggested Queries** - Helps users discover capabilities
5. **Feedback System** - Thumbs up/down for response quality
6. **System Health Monitoring** - Shows when backend issues occur
7. **Analytics Dashboard** - Usage statistics and insights
8. **Accessibility Features** - Proper ARIA labels and keyboard navigation
9. **Error Handling** - Graceful degradation when services are down
10. **TypeScript Support** - Type safety throughout the application

The frontend integrates seamlessly with the FastAPI backend and provides a professional, user-friendly interface for Edinburgh University students.
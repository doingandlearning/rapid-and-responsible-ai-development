# Frontend - RAG System Capstone

Modern React frontend built with Vite for the RAG system capstone project.

## Tech Stack

- **React 18** - Modern React with hooks
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Beautiful icons
- **ESLint** - Code linting

## Features

- 🚀 **Fast Development** - Vite provides instant hot reload
- 🎨 **Modern UI** - Clean, responsive design with Tailwind
- 📊 **Analytics Dashboard** - Real-time system metrics
- ⚙️ **Settings Panel** - Configurable system parameters
- 💬 **Chat Interface** - Interactive RAG query interface

## Getting Started

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

3. **Build for production:**
   ```bash
   npm run build
   ```

4. **Preview production build:**
   ```bash
   npm run preview
   ```

## Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_BASE=http://localhost:5000/api
```

## Project Structure

```
src/
├── components/
│   ├── ChatInterface.jsx    # Main chat component
│   ├── MessageComponent.jsx # Individual message display
│   ├── AnalyticsDashboard.jsx # Analytics and metrics
│   └── SettingsPanel.jsx   # System configuration
├── services/
│   └── api.js              # API communication
├── App.jsx                 # Main application
├── main.jsx               # Entry point
└── index.css              # Global styles
```

## Development

The frontend uses Vite for development, which provides:

- ⚡ **Instant server start**
- 🔥 **Hot Module Replacement (HMR)**
- 📦 **Optimized builds**
- 🛠️ **Built-in TypeScript support**

## API Integration

The frontend communicates with the Flask backend through:

- `POST /api/query` - Submit RAG queries
- `GET /api/analytics` - Get system metrics
- `GET /api/documents/stats` - Document statistics
- `POST /api/documents/search` - Search documents

## Styling

Uses Tailwind CSS for styling with a clean, modern design:

- Responsive layout
- Dark/light theme support
- Consistent spacing and typography
- Interactive components with hover states

## Performance

Vite provides excellent performance:

- Fast cold start
- Instant HMR updates
- Optimized production builds
- Tree-shaking for smaller bundles

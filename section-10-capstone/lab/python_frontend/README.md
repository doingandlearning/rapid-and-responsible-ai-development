# Python Frontend for RAG System Capstone

**No Node.js Required!** 🐍

A pure Python Flask frontend that replicates the functionality of the React-based frontend without requiring any JavaScript build tools or Node.js installation.

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Your RAG backend running on port 5000
- No Node.js required! 🎉

### Installation

1. **Clone or navigate to this directory:**
   ```bash
   cd python_frontend
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```

5. **Open your browser:**
   ```
   http://localhost:3000
   ```

## 📁 Project Structure

```
python_frontend/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/            # HTML templates
│   ├── base.html         # Base template with navigation
│   ├── index.html        # Home page
│   ├── chat.html         # Chat interface
│   ├── analytics.html    # Analytics dashboard
│   ├── settings.html     # Settings and file upload
│   └── error.html        # Error pages
└── static/               # Static assets
    ├── css/
    │   └── style.css     # Custom styles
    └── js/
        └── app.js        # JavaScript functionality
```

## 🎯 Features

### ✅ Complete Feature Parity

- **Chat Interface**: Full conversational interface with the RAG system
- **Analytics Dashboard**: System performance monitoring and statistics
- **Settings Panel**: Document upload and system configuration
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-time Updates**: Live system status and health monitoring

### 🎨 Modern UI

- **Tailwind CSS**: Beautiful, responsive design using CDN
- **Font Awesome Icons**: Professional iconography
- **Smooth Animations**: Polished user experience
- **Dark Mode Ready**: Prepared for future dark mode support
- **Accessibility**: Keyboard navigation and screen reader support

### 🔧 Developer Friendly

- **No Build Process**: Just run `python app.py` and you're done
- **Hot Reload**: Flask development server with auto-reload
- **Error Handling**: Comprehensive error pages and user feedback
- **API Integration**: Clean separation between frontend and backend
- **Modular Code**: Well-organized templates and JavaScript

## 🛠️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# API Configuration
API_BASE=http://localhost:5000/api

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True

# Upload Configuration
MAX_CONTENT_LENGTH=10485760  # 10MB max file size
UPLOAD_FOLDER=uploads
```

### Backend Integration

The frontend expects your RAG backend to be running on `http://localhost:5000` with the following API endpoints:

- `POST /api/query` - Send queries to the RAG system
- `GET /api/analytics` - Get system analytics
- `GET /api/health` - Check system health
- `GET /api/documents/stats` - Get document statistics
- `POST /api/documents/upload` - Upload new documents

## 📱 Usage

### Chat Interface

1. Navigate to the Chat page
2. Type your question in the text area
3. Adjust similarity threshold and max results as needed
4. Click Send or press Enter
5. View sources and metadata by expanding the sections

### Analytics Dashboard

1. Go to the Analytics page
2. View system statistics and performance metrics
3. Click Refresh to get the latest data
4. Monitor system health status

### Settings Panel

1. Visit the Settings page
2. Upload new documents using the file upload form
3. Select appropriate project type
4. Monitor processing status
5. View system information and configuration

## 🔧 Development

### Running in Development Mode

```bash
# Enable debug mode
export FLASK_ENV=development
export FLASK_DEBUG=True

# Run the application
python app.py
```

### Customizing the UI

1. **Styles**: Edit `static/css/style.css` for custom styling
2. **JavaScript**: Modify `static/js/app.js` for additional functionality
3. **Templates**: Update HTML templates in the `templates/` directory
4. **API**: Modify `app.py` to add new routes or modify existing ones

### Adding New Features

1. **New Page**: Create a new template in `templates/` and add a route in `app.py`
2. **New API Endpoint**: Add a new route in `app.py` and update the JavaScript API calls
3. **New Static Asset**: Add files to the `static/` directory and reference them in templates

## 🚀 Deployment

### Production Deployment

1. **Install production dependencies:**
   ```bash
   pip install gunicorn
   ```

2. **Run with Gunicorn:**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:3000 app:app
   ```

3. **Or use a reverse proxy like Nginx:**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:3000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 3000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:3000", "app:app"]
```

## 🔍 Troubleshooting

### Common Issues

1. **Backend Connection Error**
   - Ensure your RAG backend is running on port 5000
   - Check the API_BASE environment variable
   - Verify network connectivity

2. **File Upload Issues**
   - Check file size limits (default: 10MB)
   - Ensure file types are supported (.txt, .pdf, .docx, .md)
   - Verify upload directory permissions

3. **Static Files Not Loading**
   - Check that files are in the `static/` directory
   - Verify Flask is serving static files correctly
   - Clear browser cache

4. **JavaScript Errors**
   - Open browser developer tools to see console errors
   - Check that all API endpoints are responding correctly
   - Verify JavaScript syntax in `static/js/app.js`

### Debug Mode

Enable debug mode for detailed error messages:

```bash
export FLASK_DEBUG=True
python app.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is part of the RAG System Capstone course materials.

## 🆚 Comparison with React Version

| Feature | React Version | Python Version |
|---------|---------------|----------------|
| **Setup** | Requires Node.js, npm install, build process | Just `pip install -r requirements.txt` |
| **Dependencies** | 20+ npm packages, complex build chain | 4 Python packages |
| **Development** | `npm run dev` | `python app.py` |
| **Build** | `npm run build` | No build required |
| **Deployment** | Static files + server | Single Python process |
| **Learning Curve** | React, JSX, build tools | Python, HTML, CSS |
| **Performance** | Optimized bundle | Slightly larger page loads |
| **Features** | ✅ Full feature parity | ✅ Full feature parity |

## 🎉 Benefits

- **No Node.js Required**: Perfect for Python developers
- **Simpler Setup**: One command to get started
- **Easier Debugging**: Direct Python error messages
- **Faster Development**: No build step required
- **Better Integration**: Native Python backend integration
- **Lower Resource Usage**: No JavaScript build process
- **Easier Deployment**: Single Python process

---

**Happy coding! 🐍✨**

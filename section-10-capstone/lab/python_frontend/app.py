#!/usr/bin/env python3
"""
Python Flask Frontend for RAG System Capstone
No Node.js required - pure Python implementation
"""

import os
import json
import time
import requests
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configuration
API_BASE = os.getenv('API_BASE', 'http://localhost:5000/api')
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'md'}

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class APIService:
    """API service to communicate with the RAG backend"""
    
    def __init__(self, base_url):
        self.base_url = base_url
    
    def request(self, endpoint, method='GET', data=None, files=None):
        """Make API request to backend"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(url, timeout=30)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files, data=data, timeout=30)
                else:
                    response = requests.post(url, json=data, timeout=30)
            else:
                response = requests.request(method, url, json=data, timeout=30)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            raise Exception(f"API request failed: {str(e)}")
    
    def send_query(self, query, options=None):
        """Send query to RAG system"""
        if options is None:
            options = {
                'max_results': 10,
                'similarity_threshold': 0.4,
                'include_metadata': True
            }
        
        return self.request('/query', 'POST', {
            'query': query,
            'options': options
        })
    
    def get_analytics(self):
        """Get system analytics"""
        return self.request('/analytics')
    
    def get_document_stats(self):
        """Get document statistics"""
        return self.request('/documents/stats')
    
    def get_health(self):
        """Get system health"""
        return self.request('/health')
    
    def upload_documents(self, files, project_type):
        """Upload documents"""
        file_data = []
        for file in files:
            file_data.append(('files', (file.filename, file.stream, file.content_type)))
        
        data = {'project_type': project_type}
        return self.request('/documents/upload', 'POST', data=data, files=file_data)

# Initialize API service
api_service = APIService(API_BASE)

@app.route('/')
def index():
    """Main page - redirect to chat"""
    return render_template('index.html')

@app.route('/chat')
def chat():
    """Chat interface"""
    return render_template('chat.html')

@app.route('/analytics')
def analytics():
    """Analytics dashboard"""
    try:
        analytics_data = api_service.get_analytics()
        document_stats = api_service.get_document_stats()
        
        return render_template('analytics.html', 
                             analytics=analytics_data,
                             document_stats=document_stats)
    except Exception as e:
        return render_template('analytics.html', 
                             error=str(e),
                             analytics=None,
                             document_stats=None)

@app.route('/settings')
def settings():
    """Settings panel"""
    return render_template('settings.html')

# API Routes
@app.route('/api/query', methods=['POST'])
def api_query():
    """Handle chat queries"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        options = data.get('options', {})
        
        if not query.strip():
            return jsonify({'error': 'Query cannot be empty'}), 400
        
        # Send query to RAG system
        response = api_service.send_query(query, options)
        
        # Add timestamp
        response['timestamp'] = datetime.now().isoformat()
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics')
def api_analytics():
    """Get analytics data"""
    try:
        analytics_data = api_service.get_analytics()
        return jsonify(analytics_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def api_health():
    """Get system health"""
    try:
        health_data = api_service.get_health()
        return jsonify(health_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents/stats')
def api_document_stats():
    """Get document statistics"""
    try:
        stats = api_service.get_document_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents/upload', methods=['POST'])
def api_upload_documents():
    """Upload documents"""
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        project_type = request.form.get('project_type', 'general')
        
        # Validate files
        valid_files = []
        for file in files:
            if file and file.filename and allowed_file(file.filename):
                valid_files.append(file)
        
        if not valid_files:
            return jsonify({'error': 'No valid files provided'}), 400
        
        # Upload to backend
        result = api_service.upload_documents(valid_files, project_type)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents/processing/status')
def api_processing_status():
    """Get document processing status"""
    try:
        # This would typically check processing status
        # For now, return a mock response
        return jsonify({
            'status': 'completed',
            'processed_documents': 0,
            'total_documents': 0,
            'errors': []
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', 
                         error_code=404,
                         error_message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html',
                         error_code=500,
                         error_message="Internal server error"), 500

if __name__ == '__main__':
    print("🚀 Starting Python RAG Frontend...")
    print(f"   API Base URL: {API_BASE}")
    print("   Frontend: http://localhost:3000")
    print("   Press Ctrl+C to stop")
    
    app.run(host='0.0.0.0', port=3000, debug=True)

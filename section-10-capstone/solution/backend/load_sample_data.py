#!/usr/bin/env python3
"""
Load Sample Data Script
Simple script to load sample data into the database for testing
"""

import os
import sys
import logging
from services import database_manager, document_processor

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_sample_data(project_type: str = "literature"):
    """Load sample data for the specified project type"""
    
    logger.info(f"Loading sample data for project type: {project_type}")
    
    # Initialize database
    database_manager.initialize_database()
    
    # Load sample documents
    sample_files = {
        "literature": "data/sample_literature.txt",
        "documentation": "data/sample_documentation.txt",
        "research": "data/sample_research.txt",  # TODO: Add sample research data
        "custom": "data/sample_custom.txt"  # TODO: Add sample custom data
    }
    
    sample_file = sample_files.get(project_type)
    if not sample_file or not os.path.exists(sample_file):
        logger.error(f"Sample file not found: {sample_file}")
        return
    
    # Read sample content
    with open(sample_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Process document
    chunks = document_processor.process_document(sample_file, content, project_type)
    
    # Generate embeddings (stub - in real implementation, use Ollama)
    # TODO: Implement actual embedding generation
    embeddings = [[0.1] * 1024 for _ in chunks]  # Placeholder embeddings
    
    # Store in database
    database_manager.store_chunks(chunks, embeddings)
    
    logger.info(f"Successfully loaded {len(chunks)} chunks for {project_type} project")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Load sample data for RAG system')
    parser.add_argument('--project-type', choices=['literature', 'documentation', 'research'], 
                       default='literature', help='Project type to load data for')
    
    args = parser.parse_args()
    
    try:
        load_sample_data(args.project_type)
        print(f"✅ Sample data loaded successfully for {args.project_type} project!")
        print("\nNext steps:")
        print("1. Start the Flask backend: python app.py")
        print("2. Start the React frontend: cd ../frontend && npm start")
        print("3. Open http://localhost:3000 to test the system")
        
    except Exception as e:
        logger.error(f"Failed to load sample data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

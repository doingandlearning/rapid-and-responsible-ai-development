"""
Test Suite for MCP Document Server
==================================

Comprehensive test suite for the MCP document server including:
- Unit tests for individual tools
- Integration tests for tool workflows
- Performance tests
- Error handling tests
"""

import pytest
import json
import asyncio
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Import the server classes
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solution.mcp_server import DocumentMCPServer

class TestDocumentMCPServer:
    """Test suite for DocumentMCPServer"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.server = DocumentMCPServer()
    
    def test_validate_search_params_valid(self):
        """Test search parameter validation with valid inputs"""
        is_valid, error_msg = self.server._validate_search_params("test query", 10)
        assert is_valid is True
        assert error_msg == ""
    
    def test_validate_search_params_empty_query(self):
        """Test search parameter validation with empty query"""
        is_valid, error_msg = self.server._validate_search_params("", 10)
        assert is_valid is False
        assert "Query must be at least 2 characters" in error_msg
    
    def test_validate_search_params_short_query(self):
        """Test search parameter validation with short query"""
        is_valid, error_msg = self.server._validate_search_params("a", 10)
        assert is_valid is False
        assert "Query must be at least 2 characters" in error_msg
    
    def test_validate_search_params_invalid_limit(self):
        """Test search parameter validation with invalid limit"""
        is_valid, error_msg = self.server._validate_search_params("test", 0)
        assert is_valid is False
        assert "Limit must be between 1 and 100" in error_msg
        
        is_valid, error_msg = self.server._validate_search_params("test", 101)
        assert is_valid is False
        assert "Limit must be between 1 and 100" in error_msg
    
    def test_generate_content_preview(self):
        """Test content preview generation"""
        metadata = {
            "title": "Test Book",
            "authors": ["Author One", "Author Two"],
            "first_publish_year": 2023,
            "subject": "Technology"
        }
        
        preview = self.server._generate_content_preview(metadata)
        expected = "Test Book by Author One, Author Two (2023) - Technology"
        assert preview == expected
    
    def test_generate_content_preview_missing_fields(self):
        """Test content preview with missing metadata fields"""
        metadata = {"title": "Test Book"}
        preview = self.server._generate_content_preview(metadata)
        assert "Test Book" in preview
        assert "Unknown Author" in preview
        assert "Unknown" in preview
    
    def test_generate_document_summary(self):
        """Test document summary generation"""
        metadata = {
            "title": "Python Programming",
            "authors": ["John Doe"],
            "first_publish_year": 2023,
            "subject": "Programming"
        }
        
        summary = self.server._generate_document_summary(metadata)
        assert "Python Programming" in summary
        assert "John Doe" in summary
        assert "2023" in summary
        assert "Programming" in summary
    
    def test_extract_key_topics(self):
        """Test key topic extraction"""
        metadata = {
            "title": "AI and Machine Learning",
            "authors": ["Jane Smith"],
            "first_publish_year": 2023,
            "subject": "Artificial Intelligence"
        }
        
        topics = self.server._extract_key_topics(metadata)
        assert "Artificial Intelligence" in topics
        assert "Author: Jane Smith" in topics
        assert "Contemporary Literature" in topics
    
    def test_calculate_metadata_similarity_identical(self):
        """Test similarity calculation for identical documents"""
        metadata1 = {
            "subject": "Programming",
            "authors": ["John Doe"],
            "first_publish_year": 2023
        }
        metadata2 = {
            "subject": "Programming", 
            "authors": ["John Doe"],
            "first_publish_year": 2023
        }
        
        similarity = self.server._calculate_metadata_similarity(metadata1, metadata2)
        assert similarity == 1.0
    
    def test_calculate_metadata_similarity_different(self):
        """Test similarity calculation for different documents"""
        metadata1 = {
            "subject": "Programming",
            "authors": ["John Doe"],
            "first_publish_year": 2023
        }
        metadata2 = {
            "subject": "History",
            "authors": ["Jane Smith"],
            "first_publish_year": 1990
        }
        
        similarity = self.server._calculate_metadata_similarity(metadata1, metadata2)
        assert similarity < 0.5
    
    def test_get_similarity_level(self):
        """Test similarity level classification"""
        assert self.server._get_similarity_level(0.9) == "Very High"
        assert self.server._get_similarity_level(0.7) == "High"
        assert self.server._get_similarity_level(0.5) == "Medium"
        assert self.server._get_similarity_level(0.3) == "Low"
        assert self.server._get_similarity_level(0.1) == "Very Low"
    
    def test_find_common_elements(self):
        """Test finding common elements between documents"""
        metadata1 = {
            "subject": "Programming",
            "authors": ["John Doe", "Jane Smith"],
            "first_publish_year": 2023
        }
        metadata2 = {
            "subject": "Programming",
            "authors": ["Jane Smith", "Bob Wilson"],
            "first_publish_year": 2024
        }
        
        common = self.server._find_common_elements(metadata1, metadata2)
        assert common["subject"] == "Programming"
        assert "Jane Smith" in common["authors"]
        assert "publication_era" in common
    
    @patch('solution.mcp_server.DocumentMCPServer.get_db_connection')
    def test_search_documents_success(self, mock_db):
        """Test successful document search"""
        # Mock database response
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            ("Test Book", '{"title": "Test Book", "authors": ["Author"]}', 0.1)
        ]
        mock_db.return_value.__enter__.return_value.cursor.return_value = mock_cursor
        
        # Mock embedding generation
        with patch.object(self.server, 'get_embedding', return_value=[0.1] * 1536):
            result = self.server.search_documents("test query", limit=5)
        
        assert result["success"] is True
        assert result["query"] == "test query"
        assert len(result["results"]) == 1
        assert result["results"][0]["title"] == "Test Book"
    
    @patch('solution.mcp_server.DocumentMCPServer.get_db_connection')
    def test_search_documents_validation_error(self, mock_db):
        """Test search with validation error"""
        result = self.server.search_documents("", limit=5)
        assert result["success"] is False
        assert "Query must be at least 2 characters" in result["error"]
    
    @patch('solution.mcp_server.DocumentMCPServer.get_db_connection')
    def test_get_document_success(self, mock_db):
        """Test successful document retrieval"""
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (
            "Test Book",
            '{"title": "Test Book", "authors": ["Author"]}',
            [0.1] * 1536
        )
        mock_db.return_value.__enter__.return_value.cursor.return_value = mock_cursor
        
        result = self.server.get_document("Test Book")
        assert result["success"] is True
        assert result["document"]["title"] == "Test Book"
    
    @patch('solution.mcp_server.DocumentMCPServer.get_db_connection')
    def test_get_document_not_found(self, mock_db):
        """Test document retrieval when document not found"""
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = None
        mock_db.return_value.__enter__.return_value.cursor.return_value = mock_cursor
        
        result = self.server.get_document("Non-existent Book")
        assert result["success"] is False
        assert "Document not found" in result["error"]
    
    def test_summarize_document_success(self):
        """Test successful document summarization"""
        with patch.object(self.server, 'get_document') as mock_get_doc:
            mock_get_doc.return_value = {
                "success": True,
                "document": {
                    "title": "Test Book",
                    "metadata": {
                        "title": "Test Book",
                        "authors": ["Author"],
                        "first_publish_year": 2023,
                        "subject": "Programming"
                    }
                }
            }
            
            result = self.server.summarize_document("Test Book")
            assert result["success"] is True
            assert "Test Book" in result["summary"]
            assert "Programming" in result["summary"]
    
    def test_analyze_document_similarity_success(self):
        """Test successful document similarity analysis"""
        with patch.object(self.server, 'get_document') as mock_get_doc:
            mock_get_doc.side_effect = [
                {
                    "success": True,
                    "document": {
                        "title": "Book 1",
                        "metadata": {
                            "subject": "Programming",
                            "authors": ["Author 1"],
                            "first_publish_year": 2023
                        }
                    }
                },
                {
                    "success": True,
                    "document": {
                        "title": "Book 2", 
                        "metadata": {
                            "subject": "Programming",
                            "authors": ["Author 2"],
                            "first_publish_year": 2024
                        }
                    }
                }
            ]
            
            result = self.server.analyze_document_similarity("Book 1", "Book 2")
            assert result["success"] is True
            assert result["doc1"]["title"] == "Book 1"
            assert result["doc2"]["title"] == "Book 2"
            assert "similarity_score" in result
            assert "similarity_level" in result

class TestMCPServerIntegration:
    """Integration tests for MCP server workflows"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.server = DocumentMCPServer()
    
    @patch('solution.mcp_server.DocumentMCPServer.get_db_connection')
    def test_search_and_retrieve_workflow(self, mock_db):
        """Test complete search and retrieve workflow"""
        # Mock search results
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            ("Book 1", '{"title": "Book 1", "authors": ["Author 1"]}', 0.1),
            ("Book 2", '{"title": "Book 2", "authors": ["Author 2"]}', 0.2)
        ]
        mock_db.return_value.__enter__.return_value.cursor.return_value = mock_cursor
        
        with patch.object(self.server, 'get_embedding', return_value=[0.1] * 1536):
            # Step 1: Search for documents
            search_result = self.server.search_documents("programming", limit=2)
            assert search_result["success"] is True
            assert len(search_result["results"]) == 2
            
            # Step 2: Get details for first document
            mock_cursor.fetchone.return_value = (
                "Book 1",
                '{"title": "Book 1", "authors": ["Author 1"]}',
                [0.1] * 1536
            )
            
            doc_result = self.server.get_document("Book 1")
            assert doc_result["success"] is True
            assert doc_result["document"]["title"] == "Book 1"

class TestMCPServerPerformance:
    """Performance tests for MCP server"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.server = DocumentMCPServer()
    
    def test_embedding_caching(self):
        """Test that embeddings are cached properly"""
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {"embeddings": [[0.1] * 1536]}
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response
            
            # First call should make HTTP request
            embedding1 = self.server.get_embedding("test query")
            assert mock_post.call_count == 1
            
            # Second call should use cache
            embedding2 = self.server.get_embedding("test query")
            assert mock_post.call_count == 1  # No additional HTTP request
            assert embedding1 == embedding2

def run_tests():
    """Run all tests"""
    pytest.main([__file__, "-v"])

if __name__ == "__main__":
    run_tests()

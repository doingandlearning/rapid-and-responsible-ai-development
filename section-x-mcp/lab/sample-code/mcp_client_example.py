"""
MCP Client Example
=================

This example shows how to use an MCP client to interact with the document server.
It demonstrates the complete workflow of using MCP tools with an LLM.
"""

import json
import asyncio
from typing import Dict, Any, List

# TODO: Install MCP client SDK
# from mcp import Client

class DocumentMCPClient:
    """Example MCP client for document operations"""
    
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
        # TODO: Initialize MCP client
        # self.client = Client(server_url)
    
    async def search_documents(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search for documents using MCP tools"""
        # TODO: Implement MCP client call
        # result = await self.client.call_tool("search_documents", {
        #     "query": query,
        #     "limit": limit
        # })
        # return result
        
        # Placeholder implementation
        return {
            "success": True,
            "query": query,
            "results": [
                {
                    "id": "example-doc-1",
                    "title": "Example Document",
                    "similarity_score": 0.95,
                    "content_preview": "This is an example document..."
                }
            ],
            "count": 1
        }
    
    async def get_document(self, document_id: str) -> Dict[str, Any]:
        """Retrieve a specific document"""
        # TODO: Implement MCP client call
        # result = await self.client.call_tool("get_document", {
        #     "document_id": document_id
        # })
        # return result
        
        # Placeholder implementation
        return {
            "success": True,
            "document": {
                "id": document_id,
                "title": f"Document: {document_id}",
                "content": "This is the full content of the document..."
            }
        }
    
    async def summarize_document(self, document_id: str) -> Dict[str, Any]:
        """Get document summary"""
        # TODO: Implement MCP client call
        # result = await self.client.call_tool("summarize_document", {
        #     "document_id": document_id
        # })
        # return result
        
        # Placeholder implementation
        return {
            "success": True,
            "document_id": document_id,
            "summary": "This document discusses important topics related to...",
            "key_topics": ["Topic 1", "Topic 2", "Topic 3"]
        }
    
    async def analyze_similarity(self, doc1_id: str, doc2_id: str) -> Dict[str, Any]:
        """Analyze similarity between documents"""
        # TODO: Implement MCP client call
        # result = await self.client.call_tool("analyze_document_similarity", {
        #     "doc1_id": doc1_id,
        #     "doc2_id": doc2_id
        # })
        # return result
        
        # Placeholder implementation
        return {
            "success": True,
            "doc1": {"id": doc1_id, "title": f"Document {doc1_id}"},
            "doc2": {"id": doc2_id, "title": f"Document {doc2_id}"},
            "similarity_score": 0.75,
            "similarity_level": "High"
        }

class LLMWithMCPTools:
    """Example LLM integration with MCP tools"""
    
    def __init__(self, mcp_client: DocumentMCPClient):
        self.mcp_client = mcp_client
    
    async def answer_question(self, question: str) -> str:
        """Answer a question using MCP tools"""
        # Step 1: Search for relevant documents
        search_results = await self.mcp_client.search_documents(question, limit=5)
        
        if not search_results["success"] or not search_results["results"]:
            return "I couldn't find any relevant documents to answer your question."
        
        # Step 2: Get detailed information from top documents
        document_details = []
        for doc in search_results["results"][:3]:  # Top 3 results
            doc_detail = await self.mcp_client.get_document(doc["id"])
            if doc_detail["success"]:
                document_details.append(doc_detail["document"])
        
        # Step 3: Generate answer based on retrieved documents
        context = self._build_context(document_details)
        answer = self._generate_answer(question, context)
        
        return answer
    
    def _build_context(self, documents: List[Dict[str, Any]]) -> str:
        """Build context from retrieved documents"""
        context_parts = []
        for i, doc in enumerate(documents, 1):
            context_parts.append(f"Document {i}: {doc.get('title', 'Untitled')}")
            context_parts.append(f"Content: {doc.get('content_preview', 'No preview available')}")
            context_parts.append("---")
        
        return "\n".join(context_parts)
    
    def _generate_answer(self, question: str, context: str) -> str:
        """Generate answer based on question and context"""
        # In a real implementation, this would call an LLM API
        return f"""Based on the available documents, here's what I found regarding your question: "{question}"

{context}

This information was retrieved using MCP document tools that searched through the available knowledge base."""

async def main():
    """Example usage of MCP client"""
    # Initialize MCP client
    client = DocumentMCPClient()
    
    # Example 1: Search for documents
    print("=== Document Search Example ===")
    search_result = await client.search_documents("programming", limit=3)
    print(f"Found {search_result['count']} documents")
    for doc in search_result['results']:
        print(f"- {doc['title']} (similarity: {doc['similarity_score']:.2f})")
    
    # Example 2: Get document details
    print("\n=== Document Retrieval Example ===")
    if search_result['results']:
        doc_id = search_result['results'][0]['id']
        doc_detail = await client.get_document(doc_id)
        print(f"Document: {doc_detail['document']['title']}")
    
    # Example 3: Document summarization
    print("\n=== Document Summarization Example ===")
    if search_result['results']:
        doc_id = search_result['results'][0]['id']
        summary = await client.summarize_document(doc_id)
        print(f"Summary: {summary['summary']}")
        print(f"Key topics: {', '.join(summary['key_topics'])}")
    
    # Example 4: LLM integration
    print("\n=== LLM Integration Example ===")
    llm = LLMWithMCPTools(client)
    answer = await llm.answer_question("What are the best programming books?")
    print(f"Answer: {answer}")

if __name__ == "__main__":
    asyncio.run(main())

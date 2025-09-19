import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.document_processor import process_document

def test_document_processing():
    """Test document processing for all project types"""
    print("🌶️ Testing Document Processing...")
    
    # Test literature processing
    print("1. Testing literature processing...")
    literature_content = """
    Romeo and Juliet by William Shakespeare
    
    Act 1, Scene 1
    Two households, both alike in dignity,
    In fair Verona, where we lay our scene,
    From ancient grudge break to new mutiny,
    Where civil blood makes civil hands unclean.
    """
    
    literature_chunks = process_document("romeo_juliet.txt", literature_content, "literature")
    print(f"   ✅ Processed {len(literature_chunks)} literature chunks")
    print(f"   Sample metadata: {literature_chunks[0]['metadata']}")
    
    # Test documentation processing
    print("2. Testing documentation processing...")
    doc_content = """
    # API Reference
    
    ## GET /api/users
    Retrieve a list of users.
    
    ### Parameters
    - `limit` (optional): Number of users to return
    - `offset` (optional): Number of users to skip
    
    ### Example
    ```bash
    curl -X GET "https://api.example.com/users?limit=10"
    ```
    """
    
    doc_chunks = process_document("api_docs.md", doc_content, "documentation")
    print(f"   ✅ Processed {len(doc_chunks)} documentation chunks")
    print(f"   Sample metadata: {doc_chunks[0]['metadata']}")
    
    # Test research processing
    print("3. Testing research processing...")
    research_content = """
    Abstract
    This study examines the effects of machine learning on document processing.
    
    Methodology
    We conducted a survey of 100 participants using a mixed-methods approach.
    
    Results
    Our findings show significant improvements in processing speed (Smith et al. 2023).
    """
    
    research_chunks = process_document("research_paper.txt", research_content, "research")
    print(f"   ✅ Processed {len(research_chunks)} research chunks")
    print(f"   Sample metadata: {research_chunks[0]['metadata']}")
    
    # Test custom processing
    print("4. Testing custom processing...")
    custom_content = """
    # My Custom Project
    
    This is my custom content about cooking recipes.
    
    ## Recipe 1: Chocolate Cake
    Ingredients: flour, sugar, eggs, chocolate
    Instructions: Mix ingredients and bake at 350°F for 30 minutes.
    """
    
    custom_chunks = process_document("my_project.txt", custom_content, "custom")
    print(f"   ✅ Processed {len(custom_chunks)} custom chunks")
    print(f"   Sample metadata: {custom_chunks[0]['metadata']}")
    
    print("\n🎉 All document processing tests passed!")
    return True

if __name__ == "__main__":
    test_document_processing()
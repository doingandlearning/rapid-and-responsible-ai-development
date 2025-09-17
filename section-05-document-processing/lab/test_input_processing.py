#!/usr/bin/env python3
"""
Test Script for Input Folder Processing
======================================

This script demonstrates how the lab now processes files from the input folder
instead of using hardcoded data.
"""

import sys
from pathlib import Path

# Add solution directory to path
sys.path.append('solution')

def test_input_processing():
    """Test processing files from the input folder."""
    print("🧪 Testing Input Folder Processing")
    print("=" * 50)
    
    # Check if input folder exists
    input_dir = Path("input")
    if not input_dir.exists():
        print("❌ Input folder not found!")
        print("   The input folder should contain sample documents.")
        return False
    
    # List files in input folder
    files = list(input_dir.glob("*"))
    print(f"📁 Found {len(files)} files in input folder:")
    for file in files:
        print(f"   - {file.name}")
    
    if not files:
        print("⚠️  No files found in input folder!")
        print("   Add some .txt, .pdf, or .html files to test processing.")
        return False
    
    # Test Part 1: Text Extraction
    print(f"\n🔍 Testing Part 1: Text Extraction")
    try:
        from part1_text_extraction import process_all_input_files
        documents = process_all_input_files("input")
        
        if documents:
            print(f"✅ Successfully processed {len(documents)} documents")
            for filename, doc in documents.items():
                print(f"   📄 {filename}: {doc['metadata']['word_count']} words, {len(doc['pages'])} pages")
        else:
            print("❌ No documents were processed")
            return False
            
    except Exception as e:
        print(f"❌ Error in Part 1: {e}")
        return False
    
    # Test Part 2: Fixed-Size Chunking
    print(f"\n🔧 Testing Part 2: Fixed-Size Chunking")
    try:
        from part2_fixed_chunking import test_different_chunk_sizes
        first_doc = list(documents.values())[0]
        result = test_different_chunk_sizes(first_doc)
        print(f"✅ Chunking test completed")
        
    except Exception as e:
        print(f"❌ Error in Part 2: {e}")
        return False
    
    # Test Part 3: Content-Aware Chunking
    print(f"\n🧠 Testing Part 3: Content-Aware Chunking")
    try:
        from part3_content_aware_chunking import compare_chunking_strategies
        first_doc = list(documents.values())[0]
        best_chunks, best_quality = compare_chunking_strategies(first_doc)
        print(f"✅ Content-aware chunking test completed")
        
    except Exception as e:
        print(f"❌ Error in Part 3: {e}")
        return False
    
    print(f"\n🎉 All tests passed!")
    print(f"💡 You can now add your own files to the input folder and run the individual part scripts.")
    return True

if __name__ == "__main__":
    success = test_input_processing()
    sys.exit(0 if success else 1)

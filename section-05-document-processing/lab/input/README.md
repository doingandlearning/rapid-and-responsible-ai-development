# Input Files for Document Processing Lab

This folder contains sample documents for the document processing lab. You can add your own files here to test the processing pipeline.

## Sample Files

### **Text Files (.txt)**
- **it-support-handbook.txt**: IT Support Documentation with procedures and troubleshooting
- **student-wifi-guide.txt**: Step-by-step WiFi setup instructions
- **vpn-policy.txt**: Formal policy document with rules and compliance information

### **PDF Files (.pdf)**
- **it-support-handbook.pdf**: Same content as .txt version, but in PDF format
- **student-wifi-guide.pdf**: WiFi guide in PDF format
- **vpn-policy.pdf**: Policy document in PDF format

### **HTML Files (.html)**
- **it-support-handbook.html**: Basic HTML version with Bootstrap styling
- **student-wifi-guide.html**: WiFi guide in HTML format
- **vpn-policy.html**: Policy document in HTML format
- **advanced-it-guide.html**: Complex HTML with CSS styling, code blocks, and interactive elements

### **Markdown Files (.md)**
- **software-installation-guide.md**: Technical documentation with code examples and structured formatting

## Adding Your Own Files

### **Supported Formats**
- **Text files** (`.txt`) - Plain text documents
- **PDF files** (`.pdf`) - Portable Document Format (requires PyPDF2)
- **HTML files** (`.html`, `.htm`) - Web pages (requires BeautifulSoup4)
- **Markdown files** (`.md`) - Markdown formatted text

### **File Naming**
- Use descriptive names that indicate the document type
- Avoid spaces in filenames (use hyphens or underscores)
- Examples: `research-paper.pdf`, `user-manual.txt`, `policy-document.html`

### **File Size Recommendations**
- **Small files** (< 10KB): Good for testing and debugging
- **Medium files** (10KB - 1MB): Ideal for lab exercises
- **Large files** (> 1MB): Test performance and scalability

### **Content Suggestions**
- **Academic papers**: Research documents, course materials
- **Technical documentation**: User guides, API references
- **Policy documents**: Rules, procedures, compliance
- **Creative content**: Articles, blog posts, stories

## Processing Your Files

The lab solution files will automatically:
1. **Scan the input folder** for supported file types
2. **Extract text** from each file
3. **Process and chunk** the content
4. **Generate embeddings** for vector search
5. **Store in database** with metadata

## Tips for Best Results

### **Text Quality**
- Use clean, well-formatted text
- Include proper headings and structure
- Avoid excessive formatting or special characters

### **Document Structure**
- Use consistent heading styles
- Include page numbers if relevant
- Maintain logical content flow

### **File Organization**
- Group related documents in subfolders
- Use consistent naming conventions
- Keep file sizes reasonable for processing

## Troubleshooting

### **File Not Processed**
- Check file format is supported
- Verify file is not corrupted
- Ensure file is readable (not password protected)

### **Poor Chunking Results**
- Check document structure and formatting
- Verify text extraction worked correctly
- Try different chunking parameters

### **Processing Errors**
- Check file encoding (UTF-8 recommended)
- Verify file permissions
- Look for special characters or formatting issues

---

**Ready to process?** Run the lab solution files and they'll automatically detect and process all files in this folder!

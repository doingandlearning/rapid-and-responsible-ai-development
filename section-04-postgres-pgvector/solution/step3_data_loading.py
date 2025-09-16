#!/usr/bin/env python3
"""
Step 3: Edinburgh Documents Data Loading
Complete solution for loading documents with embeddings.
"""

import psycopg
import requests
import json
import time
import sys
from datetime import datetime, date

# Database configuration
DB_CONFIG = {
    "dbname": "pgvector",
    "user": "postgres", 
    "password": "postgres",
    "host": "localhost",
    "port": "5050",
}

# Ollama configuration
OLLAMA_URL = "http://localhost:11434/api/embed"
EMBEDDING_MODEL = "bge-m3"

def get_embedding(text, max_retries=3):
    """
    Get embedding from Ollama with retry logic and error handling.
    
    Args:
        text: Text to embed
        max_retries: Number of retry attempts
    
    Returns:
        List of floats (embedding) or None if failed
    """
    for attempt in range(max_retries):
        try:
            payload = {
                "model": EMBEDDING_MODEL,
                "input": text
            }
            
            response = requests.post(OLLAMA_URL, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            embedding = result.get("embeddings", [])
            
            if embedding and len(embedding[0]) == 1024:
                return embedding[0]
            else:
                print(f"⚠️  Invalid embedding format (attempt {attempt + 1})")
                continue
                
        except requests.exceptions.ConnectionError:
            print(f"⚠️  Connection failed to Ollama (attempt {attempt + 1})")
            if attempt < max_retries - 1:
                time.sleep(2)  # Wait before retry
        except requests.exceptions.Timeout:
            print(f"⚠️  Timeout waiting for embedding (attempt {attempt + 1})")
            if attempt < max_retries - 1:
                time.sleep(1)
        except Exception as e:
            print(f"⚠️  Embedding error: {e} (attempt {attempt + 1})")
            if attempt < max_retries - 1:
                time.sleep(1)
    
    return None

def get_edinburgh_documents():
    """
    Get comprehensive set of Edinburgh University documents.
    
    Returns:
        List of document dictionaries with metadata
    """
    return [
        {
            "title": "Password Reset Self-Service Guide",
            "content": """Edinburgh University provides self-service password reset through the MyEd portal. To reset your password: 1) Visit https://www.ed.ac.uk/is/password-reset using any web browser. 2) Enter your university username (not your email address). 3) Check your university email account for the reset link within 5 minutes. 4) Click the link and follow instructions (link expires after 24 hours for security). 5) Create a new password meeting complexity requirements: at least 8 characters with uppercase letters, lowercase letters, numbers, and special characters. If self-service fails, contact the IT Service Desk on 0131 650 4500 during office hours or submit a ticket through the IT portal.""",
            "category": "IT Support",
            "subcategory": "Authentication",
            "source_url": "https://www.ed.ac.uk/is/password-reset",
            "source_type": "webpage",
            "last_updated": date(2024, 1, 15)
        },
        {
            "title": "EdUni WiFi Connection Instructions",
            "content": """Edinburgh University provides wireless internet access through multiple networks across all campuses. Primary network: EdUni (for registered university devices). Guest network: EdUni-Guest (24-hour access for visitors). International network: Eduroam (use your home institution credentials). To register devices for EdUni: 1) Connect to EdUni-Setup network first. 2) Open any web browser. 3) Login with your university username and password. 4) Register your device by confirming the MAC address. Network performance: Up to 100Mbps download speed. Coverage includes all university buildings, student accommodations, and most outdoor campus areas. For connection problems, forget and re-add the network, or contact IT support.""",
            "category": "IT Support", 
            "subcategory": "Networking",
            "source_url": "https://www.ed.ac.uk/is/wifi",
            "source_type": "webpage",
            "last_updated": date(2024, 2, 1)
        },
        {
            "title": "Library Study Room Booking System",
            "content": """Edinburgh University Library provides bookable study spaces for individual and group study. Access the booking system through the MyEd student portal under 'Library Services'. Available locations include Main Library (floors 1-6 with variety of room sizes), George Square Library (levels 2-7 with silent and group study options), Informatics Library (ground floor group rooms), and Medical Library (basement level quiet study). Booking rules: Reserve up to 7 days in advance, maximum 4 hours per booking, cancel at least 1 hour before start time to avoid late cancellation fees. Accessibility: Accessible study rooms available on request through the booking system or by calling library reception. Peak times (9am-5pm weekdays) have highest demand, so book early.""",
            "category": "Library Services",
            "subcategory": "Facilities",
            "source_url": "https://www.ed.ac.uk/library/using-the-library/study-spaces",
            "source_type": "webpage",
            "last_updated": date(2024, 1, 20)
        },
        {
            "title": "Student Email Setup and Troubleshooting", 
            "content": """Edinburgh student email accounts are hosted on Microsoft Office 365 platform. Your email address format is s[student-number]@ed.ac.uk (e.g., s1234567@ed.ac.uk). Email client configuration: IMAP server is outlook.office365.com on port 993 with SSL encryption required. SMTP server is smtp.office365.com on port 587 with TLS encryption required. Use your full email address as username and your university password. Storage quota is 50GB per account. For mobile devices: Download Microsoft Outlook app from app store, enter your email address, and authenticate with university credentials. Common troubleshooting: Check spam/junk folder, verify password is correct, ensure two-factor authentication is properly configured, clear email client cache if experiencing sync issues.""",
            "category": "IT Support",
            "subcategory": "Email", 
            "source_url": "https://www.ed.ac.uk/is/email",
            "source_type": "webpage",
            "last_updated": date(2024, 1, 10)
        },
        {
            "title": "VPN Access for Remote University Resources",
            "content": """Edinburgh University VPN (Virtual Private Network) provides secure access to university resources when off-campus. VPN is required for: accessing library databases and digital resources, connecting to internal file shares and research data systems, using administrative systems, and secure remote desktop access. VPN client: Download FortiClient (free) from the IT Services website. Connection settings: Server address is vpn.ed.ac.uk on port 443. Authentication uses your standard university username and password. Two-factor authentication is required for all staff accounts and recommended for students. Connection limits: Maximum 3 simultaneous sessions per user. Service availability: 24/7 with scheduled maintenance windows announced via email and website. For technical issues, restart the VPN client, check firewall settings, or contact IT Service Desk.""",
            "category": "IT Support",
            "subcategory": "Remote Access",
            "source_url": "https://www.ed.ac.uk/is/vpn",
            "source_type": "webpage",
            "last_updated": date(2024, 2, 5)
        },
        {
            "title": "Student Accommodation Internet and WiFi Setup",
            "content": """All Edinburgh University student accommodations provide high-speed internet access in individual rooms and common areas. Network name: EdResNet for wired connections in rooms. Connection process: 1) Connect ethernet cable from wall port to your device. 2) Open web browser and navigate to any website. 3) Login page will appear automatically - use your university credentials. 4) Register your device by confirming the displayed MAC address. Wireless access: EdUni network available in all common areas (lounges, kitchens, study spaces). Connection speeds: Up to 1Gbps in newer accommodations (Salisbury Green, Easter Bush), 100Mbps in traditional halls. Technical support: Contact your accommodation office first for room-specific issues, then IT Service Desk for broader network problems. Gaming consoles and smart devices: Use ethernet connection where possible, or contact accommodation IT support for WiFi setup assistance.""",
            "category": "Accommodation",
            "subcategory": "IT Services",
            "source_url": "https://www.ed.ac.uk/accommodation/current-residents/it-services",
            "source_type": "webpage",
            "last_updated": date(2024, 1, 30)
        },
        {
            "title": "Academic Referencing and Citation Support",
            "content": """Edinburgh University Library provides comprehensive support for academic referencing and citation management. Common referencing styles supported: Harvard, APA, MLA, Chicago, Vancouver, and discipline-specific styles. Reference management software: EndNote is available free to all students and staff through the IT Services software portal. Getting started: Download EndNote, attend weekly library training sessions (Tuesdays 2-4pm in George Square Library), or use self-paced online tutorials. Plagiarism prevention: All assignments should use Turnitin similarity checker, accessible through the Learn VLE (Virtual Learning Environment). Additional support: Drop-in referencing help sessions Monday-Friday 10am-4pm at Main Library information desk, comprehensive online guides for all citation styles available on library website, email support at library.skills@ed.ac.uk with responses within 24 hours during term time.""",
            "category": "Library Services", 
            "subcategory": "Academic Support",
            "source_url": "https://www.ed.ac.uk/library/help/referencing",
            "source_type": "webpage",
            "last_updated": date(2024, 2, 10)
        },
        {
            "title": "MyEd Student Portal Access and Features",
            "content": """MyEd is Edinburgh University's student portal providing access to essential services and information. Login: Use your university username and password at www.myed.ed.ac.uk. Key features include: course enrollment and timetable management, exam results and academic transcripts, library account and study room booking, accommodation services and payments, student finance and fee payments, personal information updates, and university email access. Mobile access: MyEd is mobile-optimized and works on all devices. Troubleshooting login issues: Ensure your account is activated (check welcome email), verify username format (no @ed.ac.uk needed), reset password if necessary via self-service portal, contact Student Systems if account appears locked. Important: MyEd contains sensitive academic and financial information - always log out completely when using shared computers and never share your credentials.""",
            "category": "Student Services",
            "subcategory": "Online Services",
            "source_url": "https://www.ed.ac.uk/students/myed",
            "source_type": "webpage",
            "last_updated": date(2024, 1, 25)
        },
        {
            "title": "IT Service Desk Contact and Support Options",
            "content": """Edinburgh University IT Service Desk provides technical support for all students and staff. Contact methods: Phone 0131 650 4500 (Monday-Friday 8:30am-5:00pm), email servicedesk@ed.ac.uk with response within 4 hours, or submit online tickets through the IT portal for non-urgent issues. Walk-in support: George Square Library ground floor IT help desk (Monday-Friday 9am-5pm), drop-in sessions for common issues like WiFi setup and software installation. Emergency support: Out-of-hours support available for critical system failures affecting teaching and research. Self-help resources: Comprehensive online knowledge base, video tutorials for common tasks, and step-by-step guides available 24/7 on the IT Services website. When contacting support: Have your university username ready, describe the problem clearly including error messages, mention what device and operating system you're using.""",
            "category": "IT Support",
            "subcategory": "Help Desk",
            "source_url": "https://www.ed.ac.uk/is/contact",
            "source_type": "webpage",
            "last_updated": date(2024, 2, 8)
        },
        {
            "title": "Software Installation and Licensing for Students",
            "content": """Edinburgh University provides free access to essential software for academic work. Available software includes Microsoft Office 365 suite, MATLAB for mathematical computing, Adobe Creative Suite for design and media, SPSS for statistical analysis, and specialized academic software by school/department. Access method: Login to IT Services software portal using university credentials, select required software from catalog, download installer and license key. Installation support: Self-service installation guides for all platforms (Windows, Mac, Linux), weekly drop-in sessions Tuesdays 2-4pm at George Square IT desk, remote assistance available via screen sharing. Licensing terms: Software licensed for academic use only during enrollment period, some software (like Office 365) continues after graduation, transferring licenses to others is prohibited. Technical requirements: Check system requirements before downloading, ensure adequate disk space, temporarily disable antivirus during installation if required.""",
            "category": "IT Support",
            "subcategory": "Software",
            "source_url": "https://www.ed.ac.uk/is/software",
            "source_type": "webpage", 
            "last_updated": date(2024, 2, 12)
        }
    ]

def load_edinburgh_documents():
    """Load Edinburgh documents with embeddings into the database."""
    print("📚 LOADING EDINBURGH DOCUMENTS WITH EMBEDDINGS")
    print("=" * 60)
    
    documents = get_edinburgh_documents()
    print(f"📄 Total documents to process: {len(documents)}")
    
    loaded_count = 0
    failed_count = 0
    
    try:
        with psycopg.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                # Check if table exists
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_name = 'edinburgh_docs'
                    );
                """)
                
                if not cur.fetchone()[0]:
                    print("❌ Table 'edinburgh_docs' does not exist!")
                    print("   Run step2_schema_creation.py first")
                    return 0
                
                # Process each document
                for i, doc in enumerate(documents, 1):
                    print(f"\n🔄 Processing document {i}/{len(documents)}: {doc['title']}")
                    
                    # Generate embeddings with progress indication
                    print("   🧠 Generating title embedding...")
                    title_embedding = get_embedding(doc['title'])
                    
                    if not title_embedding:
                        print(f"   ❌ Failed to generate title embedding")
                        failed_count += 1
                        continue
                    
                    print("   🧠 Generating content embedding...")
                    content_embedding = get_embedding(doc['content'])
                    
                    if not content_embedding:
                        print(f"   ❌ Failed to generate content embedding")
                        failed_count += 1
                        continue
                    
                    # Insert document into database
                    try:
                        cur.execute("""
                            INSERT INTO edinburgh_docs 
                            (title, content, category, subcategory, source_url, 
                             source_type, last_updated, title_embedding, content_embedding)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            RETURNING id, word_count, char_count;
                        """, (
                            doc['title'],
                            doc['content'],
                            doc['category'], 
                            doc['subcategory'],
                            doc['source_url'],
                            doc['source_type'],
                            doc['last_updated'],
                            title_embedding,
                            content_embedding
                        ))
                        
                        result = cur.fetchone()
                        doc_id, word_count, char_count = result
                        
                        print(f"   ✅ Stored successfully (ID: {doc_id})")
                        print(f"      Words: {word_count}, Characters: {char_count}")
                        
                        loaded_count += 1
                        
                    except Exception as e:
                        print(f"   ❌ Database insertion failed: {e}")
                        failed_count += 1
                        continue
                    
                    # Brief delay to be considerate to Ollama
                    if i < len(documents):  # Don't delay after last document
                        time.sleep(0.5)
                
                # Commit all changes
                conn.commit()
                
    except Exception as e:
        print(f"❌ Fatal error during document loading: {e}")
        return 0
    
    # Summary
    print(f"\n📊 LOADING COMPLETE")
    print(f"   ✅ Successfully loaded: {loaded_count}")
    print(f"   ❌ Failed to load: {failed_count}")
    print(f"   📄 Total attempted: {len(documents)}")
    
    return loaded_count

def verify_loaded_data():
    """Verify that documents were loaded correctly."""
    print("\n🔍 VERIFYING LOADED DATA")
    print("=" * 50)
    
    try:
        with psycopg.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                # Count total documents
                cur.execute("SELECT COUNT(*) FROM edinburgh_docs;")
                total_docs = cur.fetchone()[0]
                print(f"📊 Total documents in database: {total_docs}")
                
                if total_docs == 0:
                    print("⚠️  No documents found! Check loading process.")
                    return False
                
                # Count documents with embeddings
                cur.execute("""
                    SELECT 
                        COUNT(*) as total,
                        COUNT(title_embedding) as with_title_embedding,
                        COUNT(content_embedding) as with_content_embedding
                    FROM edinburgh_docs;
                """)
                embedding_stats = cur.fetchone()
                total, title_embs, content_embs = embedding_stats
                
                print(f"🧠 Embedding statistics:")
                print(f"   Documents with title embeddings: {title_embs}/{total}")
                print(f"   Documents with content embeddings: {content_embs}/{total}")
                
                # Show category breakdown
                cur.execute("""
                    SELECT category, subcategory, COUNT(*) as count
                    FROM edinburgh_docs
                    GROUP BY category, subcategory
                    ORDER BY category, subcategory;
                """)
                categories = cur.fetchall()
                
                print(f"\n📁 Category breakdown:")
                for category, subcategory, count in categories:
                    print(f"   {category} → {subcategory}: {count} docs")
                
                # Show sample document info
                cur.execute("""
                    SELECT title, category, word_count, char_count, last_updated
                    FROM edinburgh_docs
                    ORDER BY id
                    LIMIT 3;
                """)
                samples = cur.fetchall()
                
                print(f"\n📝 Sample documents:")
                for title, category, words, chars, updated in samples:
                    print(f"   '{title}' ({category})")
                    print(f"      {words} words, {chars} chars, updated: {updated}")
                
                # Test embeddings are proper size
                cur.execute("SELECT vector_dims(title_embedding) FROM edinburgh_docs LIMIT 1;")
                embedding_size = cur.fetchone()[0]
                print(f"\n🔢 Embedding dimensions: {embedding_size} (should be 1024 for BGE-M3)")
                
                if embedding_size == 1024:
                    print("✅ Embeddings are correct size")
                else:
                    print("⚠️  Unexpected embedding size")
                
    except Exception as e:
        print(f"❌ Data verification failed: {e}")
        return False
    
    print("\n✅ Data verification successful!")
    return True

def show_sample_queries():
    """Show examples of how to query the loaded data."""
    print("\n📖 SAMPLE QUERIES")
    print("=" * 50)
    
    queries = [
        ("Count documents by category", """
SELECT category, COUNT(*) as document_count
FROM edinburgh_docs
GROUP BY category
ORDER BY document_count DESC;
        """),
        ("Find documents about passwords", """
SELECT title, category
FROM edinburgh_docs
WHERE content_tsvector @@ plainto_tsquery('password reset');
        """),
        ("Show recent documents", """
SELECT title, category, last_updated
FROM edinburgh_docs
ORDER BY last_updated DESC
LIMIT 5;
        """),
        ("Get summary statistics", """
SELECT * FROM edinburgh_docs_summary;
        """)
    ]
    
    for title, sql in queries:
        print(f"\n💡 {title}:")
        print(sql.strip())

def main():
    """Main data loading workflow."""
    print("🚀 EDINBURGH DOCUMENTS DATA LOADING")
    print("=" * 60)
    print("Loading realistic Edinburgh documents with embeddings.\n")
    
    # Load documents
    loaded_count = load_edinburgh_documents()
    
    if loaded_count == 0:
        print("❌ No documents loaded successfully!")
        return 1
    
    # Verify loaded data
    if not verify_loaded_data():
        print("❌ Data verification failed!")
        return 1
    
    # Show sample queries
    show_sample_queries()
    
    print("\n" + "=" * 60)
    print("✅ DATA LOADING COMPLETE!")
    print(f"Successfully loaded {loaded_count} Edinburgh documents with embeddings.")
    print("\n💡 Next steps:")
    print("   • Create vector indexes for performance")
    print("   • Test similarity search functionality")
    print("   • Run performance benchmarks")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
<!-- Slide 1 -->

# Capstone Lab: Student Support Chatbot

### Bringing It All Together

- <span class="fragment">Apply everything learned: vectors, RAG, ethics, production deployment</span>
- <span class="fragment">Build a complete AI system from scratch</span>
- <span class="fragment">Real-world scenario: Edinburgh University student support</span>
- <span class="fragment">Measure, evaluate, and present your findings</span>

<!-- 🗣️ Speaker Notes:
This capstone represents the culmination of the entire course. Participants will integrate all concepts learned - from vector embeddings to ethical AI governance - in building a practical student support system. -->

---

<!-- Slide 2 -->

## Project Overview

### What You'll Build

- <span class="fragment">**Intelligent Student Support Chatbot** for Edinburgh University</span>
- <span class="fragment">**Knowledge Base**: Course handbooks, policies, FAQs, procedures</span>
- <span class="fragment">**RAG Pipeline**: Vector search + LLM completion with source citation</span>
- <span class="fragment">**Web Interface**: Clean, accessible UI for student interactions</span>
- <span class="fragment">**Analytics Dashboard**: Performance metrics and usage insights</span>

<!-- 🗣️ Speaker Notes:
The system will handle real student queries like "How do I change my course?" or "What are the library opening hours?" with accurate, cited responses. -->

---

<!-- Slide 3 -->

## Architecture Review

```mermaid
graph TB
    A[Student Query] --> B[FastAPI Backend]
    B --> C[pgvector Database]
    C --> D[Vector Similarity Search]
    D --> E[Context Assembly]
    E --> F[OpenAI API]
    F --> G[Response Generation]
    G --> H[Citation & Sources]
    H --> I[React Frontend]
    I --> A
    
    J[Document Ingestion] --> K[PDF Processing]
    K --> L[Text Chunking]
    L --> M[BGE-M3 Embeddings]
    M --> C
    
    N[Ollama Service] --> M
    O[Monitoring & Analytics] --> B
    P[Ethics & Governance] --> B
```

<!-- 🗣️ Speaker Notes:
This diagram shows how all course components integrate: document processing (Section 5), vector database (Section 4), RAG pipeline (Section 6), production deployment (Section 8), and ethical governance (Section 9). -->

---

<!-- Slide 4 -->

## Success Criteria

### Technical Performance
- <span class="fragment">**Response Time**: < 3 seconds for typical queries</span>
- <span class="fragment">**Accuracy**: 85%+ relevant responses in evaluation dataset</span>
- <span class="fragment">**Source Citation**: All responses include verifiable sources</span>
- <span class="fragment">**System Reliability**: 99%+ uptime during demonstration</span>

### User Experience
- <span class="fragment">**Intuitive Interface**: Clear, accessible design</span>
- <span class="fragment">**Helpful Responses**: Actually solve student problems</span>
- <span class="fragment">**Transparent AI**: Users understand when AI is being used</span>

### Ethical Compliance
- <span class="fragment">**Privacy Protection**: No personal data stored unnecessarily</span>
- <span class="fragment">**Bias Monitoring**: Fair responses across all student groups</span>
- <span class="fragment">**Human Oversight**: Clear escalation paths</span>

---

<!-- Slide 5 -->

## Lab Structure & Timeline

### Phase 1: Foundation (90 minutes)
- <span class="fragment">Set up integrated development environment</span>
- <span class="fragment">Ingest and process Edinburgh University documents</span>
- <span class="fragment">Build and optimize vector database</span>

### Phase 2: Core Development (120 minutes)
- <span class="fragment">Implement RAG pipeline with advanced querying</span>
- <span class="fragment">Build FastAPI backend with proper error handling</span>
- <span class="fragment">Create responsive React frontend</span>

### Phase 3: Production & Ethics (90 minutes)
- <span class="fragment">Add monitoring, logging, and analytics</span>
- <span class="fragment">Implement ethical safeguards and governance</span>
- <span class="fragment">Deploy with production-ready configuration</span>

### Phase 4: Evaluation & Presentation (60 minutes)
- <span class="fragment">Test system performance and accuracy</span>
- <span class="fragment">Analyze results and identify improvements</span>
- <span class="fragment">Present findings and demo to group</span>

---

<!-- Slide 6 -->

## Knowledge Base Content

### Edinburgh University Documents
- <span class="fragment">**Student Handbooks**: Academic regulations, degree requirements</span>
- <span class="fragment">**Course Catalogs**: Module descriptions, prerequisites, timetables</span>
- <span class="fragment">**Support Services**: Counseling, accessibility, financial aid</span>
- <span class="fragment">**Campus Information**: Facilities, accommodation, dining</span>
- <span class="fragment">**Policies & Procedures**: Academic integrity, appeals, complaints</span>

### Document Processing Strategy
- <span class="fragment">**Chunking**: Semantic segmentation preserving context</span>
- <span class="fragment">**Metadata**: Document type, authority level, last updated</span>
- <span class="fragment">**Quality Control**: Remove outdated or contradictory information</span>
- <span class="fragment">**Accessibility**: Ensure content works for all students</span>

---

<!-- Slide 7 -->

## Key Implementation Challenges

### Technical Challenges
- <span class="fragment">**Context Window Management**: Balance completeness vs. token limits</span>
- <span class="fragment">**Multi-Document Synthesis**: Combine information from multiple sources</span>
- <span class="fragment">**Query Understanding**: Handle ambiguous or incomplete questions</span>
- <span class="fragment">**Performance Optimization**: Sub-3-second response times</span>

### Content Challenges
- <span class="fragment">**Information Currency**: Ensure answers reflect current policies</span>
- <span class="fragment">**Authority Hierarchy**: Prioritize official vs. unofficial sources</span>
- <span class="fragment">**Contradiction Resolution**: Handle conflicting information gracefully</span>

### User Experience Challenges
- <span class="fragment">**Query Refinement**: Help users ask better questions</span>
- <span class="fragment">**Fallback Handling**: Graceful degradation when AI can't help</span>
- <span class="fragment">**Accessibility**: Support users with different needs and abilities</span>

---

<!-- Slide 8 -->

## Evaluation Framework

### Automated Testing
- <span class="fragment">**Response Quality**: Semantic similarity to expected answers</span>
- <span class="fragment">**Source Accuracy**: Correct citation and attribution</span>
- <span class="fragment">**Performance Metrics**: Latency, throughput, error rates</span>
- <span class="fragment">**Bias Detection**: Fairness across different query types</span>

### Manual Evaluation
- <span class="fragment">**User Testing**: Real student scenarios and feedback</span>
- <span class="fragment">**Expert Review**: Subject matter expert validation</span>
- <span class="fragment">**Edge Case Analysis**: How system handles unusual queries</span>

### Test Query Categories
- <span class="fragment">**Factual**: "What are the library opening hours?"</span>
- <span class="fragment">**Procedural**: "How do I change my course?"</span>
- <span class="fragment">**Policy**: "What happens if I miss an exam?"</span>
- <span class="fragment">**Comparative**: "What's the difference between BSc and MA degrees?"</span>

---

<!-- Slide 9 -->

## Production Deployment Considerations

### Infrastructure Requirements
- <span class="fragment">**Scalability**: Handle 1000+ concurrent users</span>
- <span class="fragment">**Reliability**: 99.9% uptime with proper failover</span>
- <span class="fragment">**Security**: Protect against common web vulnerabilities</span>
- <span class="fragment">**Monitoring**: Real-time performance and error tracking</span>

### Operational Procedures
- <span class="fragment">**Content Updates**: Process for updating knowledge base</span>
- <span class="fragment">**Performance Monitoring**: Ongoing quality assessment</span>
- <span class="fragment">**User Feedback**: Collection and response mechanisms</span>
- <span class="fragment">**Incident Response**: Clear escalation and resolution procedures</span>

### Integration Points
- <span class="fragment">**University Systems**: SSO, student records, course management</span>
- <span class="fragment">**Support Services**: Handoff to human advisors when needed</span>
- <span class="fragment">**Analytics**: Integration with institutional dashboards</span>

---

<!-- Slide 10 -->

## Ethical Implementation

### Privacy Protection
- <span class="fragment">**Data Minimization**: Only collect necessary information</span>
- <span class="fragment">**Anonymization**: No personal identifiers in logs</span>
- <span class="fragment">**Retention Policies**: Clear data lifecycle management</span>
- <span class="fragment">**GDPR Compliance**: Full data subject rights implementation</span>

### Fairness & Bias Prevention
- <span class="fragment">**Representative Training**: Diverse document sources</span>
- <span class="fragment">**Bias Testing**: Regular evaluation across student groups</span>
- <span class="fragment">**Inclusive Language**: Respectful, accessible communication</span>

### Transparency & Accountability
- <span class="fragment">**AI Disclosure**: Clear indication when AI is being used</span>
- <span class="fragment">**Source Attribution**: All responses include citations</span>
- <span class="fragment">**Limitations**: Honest about what the system can/cannot do</span>
- <span class="fragment">**Human Oversight**: Clear escalation to human support</span>

---

<!-- Slide 11 -->

## Presentation Requirements

### Technical Demonstration (10 minutes)
- <span class="fragment">**Live System Demo**: Show the chatbot answering real queries</span>
- <span class="fragment">**Architecture Walkthrough**: Explain key technical decisions</span>
- <span class="fragment">**Performance Metrics**: Present quantitative results</span>

### Analysis & Reflection (10 minutes)
- <span class="fragment">**What Worked Well**: Successful implementation aspects</span>
- <span class="fragment">**Challenges Encountered**: Problems and how you solved them</span>
- <span class="fragment">**Lessons Learned**: Key insights from the development process</span>
- <span class="fragment">**Future Improvements**: What you would do differently/additionally</span>

### Team Q&A (5 minutes)
- <span class="fragment">Be prepared to discuss technical choices and trade-offs</span>
- <span class="fragment">Explain ethical considerations and compliance measures</span>
- <span class="fragment">Share insights about production deployment challenges</span>

---

<!-- Slide 12 -->

## Getting Started

### Pre-Lab Setup
- <span class="fragment">Ensure Docker environment is running smoothly</span>
- <span class="fragment">Clone the capstone starter repository</span>
- <span class="fragment">Download Edinburgh University document corpus</span>
- <span class="fragment">Verify API keys and external service connections</span>

### Team Formation
- <span class="fragment">Work in pairs or small teams (2-3 people)</span>
- <span class="fragment">Designate roles: backend, frontend, DevOps, evaluation</span>
- <span class="fragment">Set up shared development environment</span>

### Success Mindset
- <span class="fragment">**Iterate Quickly**: Start simple, add complexity gradually</span>
- <span class="fragment">**Measure Everything**: Make decisions based on data</span>
- <span class="fragment">**Think Like Users**: Prioritize actual student needs</span>
- <span class="fragment">**Embrace Failure**: Learn from what doesn't work</span>

---

<!-- Slide 13 -->

## Course Integration Checklist

Make sure your capstone demonstrates:

### ✅ Technical Skills
- <span class="fragment">Vector embeddings and similarity search (Sections 2-4)</span>
- <span class="fragment">Document processing and chunking strategies (Section 5)</span>
- <span class="fragment">RAG pipeline implementation (Section 6)</span>
- <span class="fragment">Advanced hybrid queries (Section 7)</span>
- <span class="fragment">Production deployment practices (Section 8)</span>

### ✅ Ethical Considerations
- <span class="fragment">AI governance framework application (Section 9)</span>
- <span class="fragment">Privacy protection and GDPR compliance</span>
- <span class="fragment">Bias detection and mitigation measures</span>
- <span class="fragment">Transparency and user rights</span>

### ✅ Professional Skills
- <span class="fragment">Project planning and execution</span>
- <span class="fragment">Technical communication and presentation</span>
- <span class="fragment">Problem-solving and debugging</span>
- <span class="fragment">Quality assurance and testing</span>

---

<!-- Slide 14 -->

# Ready to Build?

### Let's Create Something Amazing! 🚀

- <span class="fragment">You have all the knowledge and skills needed</span>
- <span class="fragment">Work together, learn from each other</span>
- <span class="fragment">Focus on solving real student problems</span>
- <span class="fragment">Build something you'd be proud to deploy</span>

### Remember: This is **your** capstone project
- <span class="fragment">Make technical choices you can justify</span>
- <span class="fragment">Prioritize features that add real value</span>
- <span class="fragment">Document your learning journey</span>
- <span class="fragment">Have fun building the future of student support!</span>

---

<!-- Slide 15 -->

## Lab Instructions Overview

### 🎯 **Your Mission**
Build a production-ready student support chatbot that Edinburgh University could actually deploy.

### 📋 **Deliverables**
1. Working chatbot with web interface
2. Performance evaluation report
3. Technical architecture documentation
4. Ethical compliance assessment
5. 25-minute team presentation

### ⏰ **Timeline**
- **Setup & Ingestion**: 90 minutes
- **Core Development**: 120 minutes  
- **Production & Ethics**: 90 minutes
- **Testing & Presentation Prep**: 60 minutes

### 🏆 **Success Criteria**
A system that's technically sound, ethically compliant, and genuinely helpful to students.

**Let's begin!** 

<!-- 🗣️ Speaker Notes:
Transition to hands-on lab. Emphasize that this is their chance to showcase everything they've learned. The next 6 hours will be intensive but rewarding. Remind them to ask for help when needed and support each other. -->
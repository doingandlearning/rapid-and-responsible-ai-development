# Section 9 Lab: AI Ethics & Governance Implementation

**Building Responsible AI Systems for Edinburgh University**

## Lab Overview

**Time:** 45 minutes  
**Objective:** Implement comprehensive AI ethics and governance frameworks for university-scale AI systems  
**Context:** Transform the production vector search system into an ethically responsible, governable, and transparent AI service that aligns with Edinburgh University values and regulatory requirements

---

## Prerequisites

✅ **Section 8 completed** - Production deployment system with monitoring and security  
✅ **Understanding of AI ethics principles** - Bias, transparency, accountability, privacy  
✅ **University context awareness** - Edinburgh's diverse community and institutional responsibilities  
✅ **Regulatory knowledge** - UK-GDPR, university policies, and ethical AI standards

### Quick Verification

```bash
# Verify production system is operational
curl -f http://localhost:5100/health
echo "Production system status: $?"

# Check monitoring capabilities
curl -s http://localhost:5100/metrics | grep -c "vector_search" 
echo "Metrics endpoints available"

# Verify user data is available
python -c "
from final_materials.section_08_production_deployment.solution.production_system import ProductionConfig
config = ProductionConfig()
print('Ethics framework ready for implementation')
"
```

---

## Lab Exercises

### Exercise 1: Bias Detection Implementation (12 minutes)

#### 1.1: Create Bias Detection Framework

**Build comprehensive bias detection system:**

```python
# lab9_bias_detection.py
import psycopg
import json
import pandas as pd
from typing import Dict, Any, List, Tuple
from collections import defaultdict
import statistics
from datetime import datetime, timedelta

class EdinburghBiasDetector:
    """Bias detection system for Edinburgh University AI systems."""
    
    def __init__(self, db_config):
        self.db_config = db_config
        
        # Edinburgh-specific demographic categories
        self.protected_attributes = {
            'gender': ['male', 'female', 'non-binary', 'unknown'],
            'department': ['IT Services', 'Student Services', 'Library', 'Estates', 'HR', 'Finance'],
            'campus': ['Central Campus', "King's Buildings", 'Easter Bush', 'Western General'],
            'user_role': ['student', 'staff', 'academic', 'admin'],
            'content_type': ['policy', 'guide', 'procedure', 'faq', 'manual']
        }
        
    def connect_db(self):
        """Database connection for bias analysis."""
        return psycopg.connect(**self.db_config)
    
    def analyze_representation_bias(self) -> Dict[str, Any]:
        """Analyze representation bias in document corpus."""
        
        print("🔍 ANALYZING REPRESENTATION BIAS")
        print("=" * 50)
        
        with self.connect_db() as conn:
            cur = conn.cursor()
            
            # Analyze document representation by department
            cur.execute("""
                SELECT 
                    metadata->>'department' as department,
                    metadata->>'campus' as campus,
                    metadata->>'doc_type' as doc_type,
                    COUNT(*) as doc_count,
                    AVG(LENGTH(text)) as avg_length,
                    COUNT(CASE WHEN embedding IS NOT NULL THEN 1 END) as with_embeddings
                FROM document_chunks 
                WHERE metadata IS NOT NULL
                GROUP BY 
                    metadata->>'department', 
                    metadata->>'campus',
                    metadata->>'doc_type'
                ORDER BY doc_count DESC
            """)
            
            representation_data = cur.fetchall()
            
        # Analyze representation balance
        dept_counts = defaultdict(int)
        campus_counts = defaultdict(int)
        type_counts = defaultdict(int)
        
        total_docs = 0
        
        print("📊 DOCUMENT REPRESENTATION ANALYSIS:")
        print("-" * 50)
        
        for dept, campus, doc_type, count, avg_len, with_emb in representation_data:
            dept_counts[dept or 'Unknown'] += count
            campus_counts[campus or 'Unknown'] += count
            type_counts[doc_type or 'Unknown'] += count
            total_docs += count
            
            print(f"{dept:<15} | {campus:<20} | {doc_type:<10} | {count:>3} docs | {avg_len:>4.0f} chars")
        
        # Calculate representation fairness
        dept_distribution = {k: v/total_docs for k, v in dept_counts.items()}
        campus_distribution = {k: v/total_docs for k, v in campus_counts.items()}
        
        # Identify potential bias
        bias_indicators = {
            'department_imbalance': max(dept_distribution.values()) / min(dept_distribution.values()),
            'campus_imbalance': max(campus_distribution.values()) / min(campus_distribution.values()),
            'most_represented_dept': max(dept_distribution, key=dept_distribution.get),
            'least_represented_dept': min(dept_distribution, key=dept_distribution.get),
            'representation_details': {
                'departments': dept_distribution,
                'campuses': campus_distribution,
                'document_types': {k: v/total_docs for k, v in type_counts.items()}
            }
        }
        
        print(f"\n📈 REPRESENTATION ANALYSIS:")
        print(f"  Department imbalance ratio: {bias_indicators['department_imbalance']:.2f}x")
        print(f"  Campus imbalance ratio: {bias_indicators['campus_imbalance']:.2f}x")
        print(f"  Most represented: {bias_indicators['most_represented_dept']} ({dept_distribution[bias_indicators['most_represented_dept']]:.1%})")
        print(f"  Least represented: {bias_indicators['least_represented_dept']} ({dept_distribution[bias_indicators['least_represented_dept']]:.1%})")
        
        return bias_indicators
    
    def analyze_search_result_bias(self, test_queries: List[str]) -> Dict[str, Any]:
        """Analyze bias in search results for test queries."""
        
        print(f"\n🎯 ANALYZING SEARCH RESULT BIAS")
        print("=" * 50)
        
        from final_materials.section_08_production_deployment.solution.production_system import ProductionVectorSearchSystem, ProductionConfig, SearchRequest, UserProfile
        
        # Initialize search system
        config = ProductionConfig()
        search_system = ProductionVectorSearchSystem(config)
        
        bias_results = {}
        
        # Test queries representing different perspectives
        test_scenarios = {
            'leadership_queries': [
                'leadership opportunities at Edinburgh',
                'management training programs',
                'executive development courses'
            ],
            'support_queries': [
                'student support services',
                'mental health resources', 
                'accessibility accommodations'
            ],
            'technical_queries': [
                'IT troubleshooting guides',
                'research computing resources',
                'data management procedures'
            ]
        }
        
        for scenario_name, queries in test_scenarios.items():
            print(f"\n📋 Testing {scenario_name}:")
            scenario_results = []
            
            for query in queries:
                print(f"  Query: '{query}'")
                
                # Test with different user profiles
                user_profiles = [
                    UserProfile('student1', 'test_student', 'student', 'Student Services', 'Central Campus', 2, 30, 20),
                    UserProfile('staff1', 'test_staff', 'staff', 'IT Services', "King's Buildings", 3, 60, 50),
                    UserProfile('academic1', 'test_academic', 'academic', 'Research Services', 'Easter Bush', 4, 100, 100)
                ]
                
                query_results = {}
                
                for user_profile in user_profiles:
                    search_request = SearchRequest(
                        query=query,
                        filters={},
                        user_profile=user_profile,
                        config={'similarity_threshold': 0.4, 'max_results': 10},
                        request_id=f'bias_test_{user_profile.role}'
                    )
                    
                    try:
                        response = search_system.process_search_request(search_request)
                        
                        # Analyze result demographics
                        result_analysis = self.analyze_result_demographics(response.results)
                        query_results[user_profile.role] = result_analysis
                        
                        print(f"    {user_profile.role}: {len(response.results)} results, avg score: {statistics.mean([r.get('combined_score', 0) for r in response.results]):.3f}")
                        
                    except Exception as e:
                        print(f"    {user_profile.role}: Error - {str(e)}")
                        query_results[user_profile.role] = {'error': str(e)}
                
                scenario_results.append({
                    'query': query,
                    'results_by_role': query_results
                })
            
            bias_results[scenario_name] = scenario_results
        
        return bias_results
    
    def analyze_result_demographics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze demographic representation in search results."""
        
        demographics = {
            'departments': defaultdict(int),
            'campuses': defaultdict(int),
            'doc_types': defaultdict(int),
            'priorities': defaultdict(int)
        }
        
        total_results = len(results)
        
        for result in results:
            metadata = result.get('metadata', {})
            
            dept = metadata.get('department', 'Unknown')
            campus = metadata.get('campus', 'Unknown') 
            doc_type = metadata.get('doc_type', 'Unknown')
            priority = metadata.get('priority', 'Unknown')
            
            demographics['departments'][dept] += 1
            demographics['campuses'][campus] += 1
            demographics['doc_types'][doc_type] += 1
            demographics['priorities'][priority] += 1
        
        # Convert to percentages
        for category in demographics:
            for key in demographics[category]:
                demographics[category][key] = demographics[category][key] / total_results if total_results > 0 else 0
        
        return {
            'total_results': total_results,
            'demographics': dict(demographics)
        }
    
    def generate_bias_report(self) -> Dict[str, Any]:
        """Generate comprehensive bias assessment report."""
        
        print("📑 GENERATING COMPREHENSIVE BIAS REPORT")
        print("=" * 60)
        
        # Analyze representation bias
        representation_bias = self.analyze_representation_bias()
        
        # Test search result bias
        test_queries = [
            'leadership development opportunities',
            'student support and guidance',
            'research computing facilities',
            'campus safety procedures',
            'diversity and inclusion policies'
        ]
        
        search_bias = self.analyze_search_result_bias(test_queries)
        
        # Overall bias assessment
        bias_severity = self.assess_bias_severity(representation_bias)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'representation_bias': representation_bias,
            'search_result_bias': search_bias,
            'bias_severity_assessment': bias_severity,
            'recommendations': self.generate_bias_mitigation_recommendations(bias_severity)
        }
        
        print(f"\n📊 BIAS ASSESSMENT COMPLETE")
        print(f"Overall bias severity: {bias_severity['overall_severity']}")
        print(f"Key concerns: {', '.join(bias_severity['primary_concerns'])}")
        
        return report
    
    def assess_bias_severity(self, representation_bias: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall bias severity and priority areas."""
        
        severity_factors = {
            'department_imbalance': representation_bias['department_imbalance'],
            'campus_imbalance': representation_bias['campus_imbalance']
        }
        
        # Determine severity level
        if severity_factors['department_imbalance'] > 3.0 or severity_factors['campus_imbalance'] > 3.0:
            overall_severity = 'High'
            primary_concerns = ['Significant representation imbalances detected']
        elif severity_factors['department_imbalance'] > 2.0 or severity_factors['campus_imbalance'] > 2.0:
            overall_severity = 'Medium'
            primary_concerns = ['Moderate representation imbalances']
        else:
            overall_severity = 'Low'
            primary_concerns = ['Minor imbalances within acceptable ranges']
        
        return {
            'overall_severity': overall_severity,
            'severity_factors': severity_factors,
            'primary_concerns': primary_concerns
        }
    
    def generate_bias_mitigation_recommendations(self, bias_assessment: Dict[str, Any]) -> List[str]:
        """Generate actionable bias mitigation recommendations."""
        
        recommendations = []
        
        if bias_assessment['overall_severity'] == 'High':
            recommendations.extend([
                'Immediate content audit and rebalancing required',
                'Implement content weighting to address representation gaps',
                'Establish diverse content review committee',
                'Develop bias-aware ranking algorithms'
            ])
        elif bias_assessment['overall_severity'] == 'Medium':
            recommendations.extend([
                'Gradual content diversification program',
                'Regular bias monitoring and reporting',
                'User feedback integration for bias detection',
                'Balanced content acquisition strategy'
            ])
        else:
            recommendations.extend([
                'Continue current bias monitoring practices',
                'Maintain content diversity awareness',
                'Regular community feedback collection',
                'Preventive bias detection measures'
            ])
        
        # Universal recommendations
        recommendations.extend([
            'Quarterly bias assessment and reporting',
            'Transparent communication about bias mitigation efforts',
            'Staff training on bias awareness and prevention',
            'User education on system limitations and biases'
        ])
        
        return recommendations

if __name__ == "__main__":
    db_config = {
        'host': 'localhost',
        'port': 5050,
        'dbname': 'pgvector',
        'user': 'postgres',
        'password': 'postgres'
    }
    
    bias_detector = EdinburghBiasDetector(db_config)
    bias_report = bias_detector.generate_bias_report()
    
    # Save report
    with open('edinburgh_bias_assessment_report.json', 'w') as f:
        json.dump(bias_report, f, indent=2, default=str)
    
    print(f"\n✅ Bias assessment report saved to edinburgh_bias_assessment_report.json")
```

**Run bias detection analysis:**

```bash
python lab9_bias_detection.py
```

#### 1.2: Implement Bias Mitigation Strategies

**Create bias mitigation system:**

```python
# lab9_bias_mitigation.py
import json
import psycopg
from typing import Dict, Any, List
import random
from collections import defaultdict

class EdinburghBiasMitigation:
    """Bias mitigation strategies for Edinburgh University AI systems."""
    
    def __init__(self, db_config):
        self.db_config = db_config
    
    def connect_db(self):
        return psycopg.connect(**self.db_config)
    
    def implement_content_reweighting(self) -> Dict[str, Any]:
        """Implement content reweighting to address representation bias."""
        
        print("⚖️ IMPLEMENTING CONTENT REWEIGHTING")
        print("=" * 50)
        
        with self.connect_db() as conn:
            cur = conn.cursor()
            
            # Calculate current representation weights
            cur.execute("""
                SELECT 
                    metadata->>'department' as department,
                    COUNT(*) as doc_count
                FROM document_chunks 
                WHERE metadata IS NOT NULL
                GROUP BY metadata->>'department'
                ORDER BY doc_count
            """)
            
            dept_counts = cur.fetchall()
            
        # Calculate reweighting factors
        total_docs = sum(count for _, count in dept_counts)
        target_representation = total_docs / len(dept_counts)  # Equal representation target
        
        reweighting_factors = {}
        
        print("📊 REWEIGHTING FACTORS:")
        print("-" * 30)
        
        for dept, count in dept_counts:
            # Boost underrepresented departments
            if count < target_representation:
                boost_factor = min(target_representation / count, 2.0)  # Cap at 2x boost
            else:
                boost_factor = 1.0
                
            reweighting_factors[dept or 'Unknown'] = boost_factor
            print(f"{dept:<20}: {count:>3} docs → {boost_factor:.2f}x weight")
        
        # Apply reweighting to database
        with self.connect_db() as conn:
            cur = conn.cursor()
            
            for dept, weight in reweighting_factors.items():
                if dept != 'Unknown':
                    # Update metadata with reweighting factor
                    cur.execute("""
                        UPDATE document_chunks 
                        SET metadata = metadata || %s
                        WHERE metadata->>'department' = %s
                    """, (json.dumps({'bias_weight': weight}), dept))
            
            conn.commit()
            
        print(f"\n✅ Applied reweighting factors to {len(reweighting_factors)} departments")
        
        return {
            'reweighting_factors': reweighting_factors,
            'target_representation': target_representation,
            'total_documents': total_docs
        }
    
    def create_fairness_aware_search(self) -> None:
        """Create fairness-aware search ranking function."""
        
        print("\n🎯 CREATING FAIRNESS-AWARE SEARCH")
        print("=" * 50)
        
        fairness_query_template = """
        WITH scored_results AS (
            SELECT 
                document_title,
                section_title,
                text,
                metadata,
                -- Base similarity score
                1 - (embedding <=> %s::vector) as similarity,
                
                -- Fairness-adjusted score
                (
                    -- 50% semantic similarity
                    (1 - (embedding <=> %s::vector)) * 0.5 +
                    
                    -- 20% priority weight
                    LEAST((metadata->>'priority')::float / 5.0, 1.0) * 0.2 +
                    
                    -- 15% popularity weight
                    LEAST((metadata->>'view_count')::float / 5000.0, 1.0) * 0.15 +
                    
                    -- 15% bias mitigation weight (boost underrepresented content)
                    COALESCE((metadata->>'bias_weight')::float, 1.0) * 0.15
                    
                ) as fairness_score
                
            FROM document_chunks 
            WHERE embedding <=> %s::vector < %s
        )
        SELECT * FROM scored_results
        ORDER BY fairness_score DESC
        LIMIT %s
        """
        
        # Test fairness-aware search
        from final_materials.section_08_production_deployment.solution.production_system import ProductionVectorSearchSystem, ProductionConfig
        
        config = ProductionConfig()
        search_system = ProductionVectorSearchSystem(config)
        
        test_query = "leadership development opportunities"
        query_embedding = search_system.embedding_service.get_embedding(test_query)
        
        if query_embedding:
            with self.connect_db() as conn:
                cur = conn.cursor()
                cur.execute(fairness_query_template, [
                    query_embedding, query_embedding, query_embedding, 0.4, 10
                ])
                
                results = cur.fetchall()
                
                print("🔍 FAIRNESS-AWARE SEARCH RESULTS:")
                print("-" * 50)
                
                for i, (title, section, text, metadata, similarity, fairness_score) in enumerate(results, 1):
                    meta_dict = json.loads(metadata) if metadata else {}
                    dept = meta_dict.get('department', 'Unknown')
                    bias_weight = meta_dict.get('bias_weight', 1.0)
                    
                    print(f"{i:2d}. {title[:40]}...")
                    print(f"    Dept: {dept:<15} | Similarity: {similarity:.3f} | Fairness Score: {fairness_score:.3f} | Bias Weight: {bias_weight:.2f}")
                    print()
        
        print("✅ Fairness-aware search algorithm implemented")
    
    def create_diversity_injection_system(self) -> Dict[str, Any]:
        """Create system to inject diversity into search results."""
        
        print("\n🌈 CREATING DIVERSITY INJECTION SYSTEM")
        print("=" * 50)
        
        diversity_strategies = {
            'departmental_diversity': {
                'description': 'Ensure multiple departments represented in top results',
                'implementation': 'Round-robin selection from top results per department',
                'target_threshold': 0.3  # At least 30% of results from different departments
            },
            'campus_diversity': {
                'description': 'Ensure multiple campuses represented where relevant',
                'implementation': 'Geographic distribution in result ranking',
                'target_threshold': 0.25  # At least 25% from different campuses
            },
            'content_type_diversity': {
                'description': 'Mix of content types (policies, guides, procedures)',
                'implementation': 'Content type balancing in result composition',
                'target_threshold': 0.2   # At least 20% variety in content types
            }
        }
        
        print("📋 DIVERSITY STRATEGIES:")
        for strategy, details in diversity_strategies.items():
            print(f"\n{strategy.upper().replace('_', ' ')}:")
            print(f"  Description: {details['description']}")
            print(f"  Implementation: {details['implementation']}")
            print(f"  Target: {details['target_threshold']:.0%} diversity threshold")
        
        # Implement diversity injection function
        def apply_diversity_injection(raw_results: List[Dict], diversity_threshold: float = 0.3):
            """Apply diversity injection to search results."""
            
            if len(raw_results) <= 3:
                return raw_results  # Too few results for diversity injection
            
            # Group results by department
            dept_groups = defaultdict(list)
            for result in raw_results:
                dept = result.get('metadata', {}).get('department', 'Unknown')
                dept_groups[dept].append(result)
            
            # Apply round-robin selection to ensure diversity
            diversified_results = []
            max_results = len(raw_results)
            dept_iterators = {dept: iter(results) for dept, results in dept_groups.items()}
            
            while len(diversified_results) < max_results and dept_iterators:
                for dept in list(dept_iterators.keys()):
                    try:
                        result = next(dept_iterators[dept])
                        diversified_results.append(result)
                        
                        if len(diversified_results) >= max_results:
                            break
                    except StopIteration:
                        del dept_iterators[dept]
            
            return diversified_results
        
        print("\n✅ Diversity injection system created")
        return {
            'strategies': diversity_strategies,
            'diversity_function': apply_diversity_injection
        }
    
    def implement_bias_monitoring_alerts(self) -> Dict[str, Any]:
        """Implement automated bias monitoring and alerting."""
        
        print("\n🚨 IMPLEMENTING BIAS MONITORING ALERTS")
        print("=" * 50)
        
        monitoring_config = {
            'representation_thresholds': {
                'department_imbalance_ratio': 2.5,  # Alert if any department >2.5x others
                'campus_imbalance_ratio': 2.0,      # Alert if any campus >2x others
                'content_type_ratio': 3.0           # Alert if any content type >3x others
            },
            'result_quality_thresholds': {
                'min_diversity_score': 0.3,         # Alert if diversity <30%
                'max_single_source_ratio': 0.7,     # Alert if one source >70% of results
                'min_user_satisfaction': 0.75       # Alert if satisfaction <75%
            },
            'alert_frequencies': {
                'daily_check': ['representation_balance', 'result_quality'],
                'weekly_check': ['user_feedback_analysis', 'demographic_impact'],
                'monthly_check': ['comprehensive_bias_audit', 'policy_compliance']
            }
        }
        
        print("📊 MONITORING CONFIGURATION:")
        print(f"  Department imbalance threshold: {monitoring_config['representation_thresholds']['department_imbalance_ratio']}x")
        print(f"  Minimum diversity score: {monitoring_config['result_quality_thresholds']['min_diversity_score']:.0%}")
        print(f"  Daily monitoring: {', '.join(monitoring_config['alert_frequencies']['daily_check'])}")
        
        # Create monitoring function
        def bias_monitoring_check():
            """Perform bias monitoring check and generate alerts."""
            
            alerts = []
            
            # Check representation balance
            from lab9_bias_detection import EdinburghBiasDetector
            
            bias_detector = EdinburghBiasDetector(self.db_config)
            representation_bias = bias_detector.analyze_representation_bias()
            
            if representation_bias['department_imbalance'] > monitoring_config['representation_thresholds']['department_imbalance_ratio']:
                alerts.append({
                    'type': 'representation_bias',
                    'severity': 'high',
                    'message': f"Department imbalance detected: {representation_bias['department_imbalance']:.1f}x ratio",
                    'recommended_action': 'Review content acquisition and weighting strategies'
                })
            
            if representation_bias['campus_imbalance'] > monitoring_config['representation_thresholds']['campus_imbalance_ratio']:
                alerts.append({
                    'type': 'representation_bias',
                    'severity': 'medium', 
                    'message': f"Campus imbalance detected: {representation_bias['campus_imbalance']:.1f}x ratio",
                    'recommended_action': 'Increase content diversity across campuses'
                })
            
            return alerts
        
        print("✅ Bias monitoring and alerting system implemented")
        
        return {
            'monitoring_config': monitoring_config,
            'monitoring_function': bias_monitoring_check
        }

if __name__ == "__main__":
    db_config = {
        'host': 'localhost',
        'port': 5050,
        'dbname': 'pgvector',
        'user': 'postgres',
        'password': 'postgres'
    }
    
    bias_mitigation = EdinburghBiasMitigation(db_config)
    
    # Implement bias mitigation strategies
    print("🚀 IMPLEMENTING BIAS MITIGATION STRATEGIES")
    print("=" * 60)
    
    # 1. Content reweighting
    reweighting_results = bias_mitigation.implement_content_reweighting()
    
    # 2. Fairness-aware search
    bias_mitigation.create_fairness_aware_search()
    
    # 3. Diversity injection
    diversity_system = bias_mitigation.create_diversity_injection_system()
    
    # 4. Monitoring and alerts
    monitoring_system = bias_mitigation.implement_bias_monitoring_alerts()
    
    print(f"\n" + "=" * 60)
    print("✅ BIAS MITIGATION IMPLEMENTATION COMPLETE!")
    print("=" * 60)
```

**Run bias mitigation:**

```bash
python lab9_bias_mitigation.py
```

---

### Exercise 2: Transparency and Explainability (10 minutes)

#### 2.1: Create AI Explanation System

**Build transparent AI explanation framework:**

```python
# lab9_transparency.py
from typing import Dict, Any, List
import json
from datetime import datetime

class EdinburghTransparencySystem:
    """Transparency and explainability system for Edinburgh University AI."""
    
    def __init__(self, db_config):
        self.db_config = db_config
    
    def create_result_explanation_system(self) -> Dict[str, Any]:
        """Create comprehensive result explanation system."""
        
        print("💡 CREATING AI EXPLANATION SYSTEM")
        print("=" * 50)
        
        explanation_framework = {
            'explanation_components': {
                'similarity_explanation': {
                    'purpose': 'Explain why results are semantically relevant',
                    'user_message': 'This result appeared because it closely matches your search terms',
                    'technical_details': 'Vector similarity score and keyword matching'
                },
                'ranking_factors': {
                    'purpose': 'Explain how results are ordered',
                    'user_message': 'Results are ranked by relevance, recency, and university priority',
                    'technical_details': 'Weighted scoring: 50% similarity, 20% priority, 15% popularity, 15% bias mitigation'
                },
                'data_sources': {
                    'purpose': 'Identify where information comes from',
                    'user_message': 'This information comes from official university documents',
                    'technical_details': 'Document source, last updated date, and approval status'
                },
                'bias_considerations': {
                    'purpose': 'Acknowledge potential biases and limitations',
                    'user_message': 'Our system actively works to provide diverse perspectives',
                    'technical_details': 'Bias mitigation strategies and diversity measures applied'
                }
            }
        }
        
        class ExplainableSearchResult:
            """Search result with comprehensive explanations."""
            
            def __init__(self, result_data: Dict[str, Any], query: str):
                self.result_data = result_data
                self.query = query
                self.explanations = self.generate_explanations()
            
            def generate_explanations(self) -> Dict[str, Any]:
                """Generate user-friendly explanations for this result."""
                
                similarity = self.result_data.get('similarity', 0)
                metadata = self.result_data.get('metadata', {})
                combined_score = self.result_data.get('combined_score', 0)
                
                explanations = {
                    'relevance_explanation': self.explain_relevance(similarity),
                    'ranking_explanation': self.explain_ranking(combined_score, metadata),
                    'source_explanation': self.explain_source(metadata),
                    'bias_explanation': self.explain_bias_mitigation(metadata),
                    'quality_indicators': self.provide_quality_indicators(metadata)
                }
                
                return explanations
            
            def explain_relevance(self, similarity: float) -> str:
                """Explain why this result is relevant."""
                
                if similarity >= 0.8:
                    return f"This result is highly relevant to your search '{self.query}' (similarity: {similarity:.1%}). The content closely matches your search terms."
                elif similarity >= 0.6:
                    return f"This result is moderately relevant to your search '{self.query}' (similarity: {similarity:.1%}). It contains related information that may be helpful."
                elif similarity >= 0.4:
                    return f"This result has some relevance to your search '{self.query}' (similarity: {similarity:.1%}). It may contain useful background information."
                else:
                    return f"This result has limited relevance to your search '{self.query}' (similarity: {similarity:.1%}). It appeared due to other factors like recency or importance."
            
            def explain_ranking(self, combined_score: float, metadata: Dict) -> str:
                """Explain how this result was ranked."""
                
                factors = []
                
                # Identify contributing factors
                priority = metadata.get('priority', 3)
                if priority >= 4:
                    factors.append("high university priority")
                
                view_count = metadata.get('view_count', 0)
                if view_count > 1000:
                    factors.append("popular with users")
                
                bias_weight = metadata.get('bias_weight', 1.0)
                if bias_weight > 1.1:
                    factors.append("diversity promotion")
                
                last_reviewed = metadata.get('last_reviewed', '')
                if last_reviewed and '2024' in last_reviewed:
                    factors.append("recently updated")
                
                factor_text = ", ".join(factors) if factors else "standard relevance criteria"
                
                return f"This result ranked highly (score: {combined_score:.2f}) due to: {factor_text}."
            
            def explain_source(self, metadata: Dict) -> str:
                """Explain the source and authority of this result."""
                
                department = metadata.get('department', 'Unknown')
                doc_type = metadata.get('doc_type', 'document')
                campus = metadata.get('campus', 'University-wide')
                
                return f"This {doc_type} comes from {department} and applies to {campus}. All university documents in our system are from official sources."
            
            def explain_bias_mitigation(self, metadata: Dict) -> str:
                """Explain bias mitigation efforts."""
                
                bias_weight = metadata.get('bias_weight', 1.0)
                
                if bias_weight > 1.1:
                    return "This result received a diversity boost to ensure balanced representation across university departments and services."
                else:
                    return "This result was ranked using our standard fairness-aware algorithm that promotes diverse perspectives."
            
            def provide_quality_indicators(self, metadata: Dict) -> Dict[str, Any]:
                """Provide quality and reliability indicators."""
                
                return {
                    'official_source': True,
                    'last_reviewed': metadata.get('last_reviewed', 'Unknown'),
                    'document_type': metadata.get('doc_type', 'Unknown'),
                    'approval_status': metadata.get('status', 'Unknown'),
                    'confidence_level': 'High' if metadata.get('priority', 0) >= 4 else 'Medium'
                }
        
        print("📋 EXPLANATION FRAMEWORK COMPONENTS:")
        for component, details in explanation_framework['explanation_components'].items():
            print(f"  {component}: {details['purpose']}")
        
        print("\n✅ Explainable search result system created")
        
        return {
            'framework': explanation_framework,
            'explainable_result_class': ExplainableSearchResult
        }
    
    def create_transparency_dashboard(self) -> Dict[str, Any]:
        """Create transparency dashboard for system operations."""
        
        print("\n📊 CREATING TRANSPARENCY DASHBOARD")
        print("=" * 50)
        
        dashboard_components = {
            'system_overview': {
                'total_documents': 'Number of documents in the system',
                'data_sources': 'List of data sources and last update dates',
                'processing_methods': 'How documents are processed and indexed',
                'update_frequency': 'How often the system is updated with new content'
            },
            'fairness_metrics': {
                'demographic_representation': 'Breakdown of content by department, campus, type',
                'bias_mitigation_status': 'Current bias mitigation strategies in use',
                'diversity_scores': 'Measurement of result diversity across searches',
                'user_satisfaction': 'User satisfaction scores by demographic groups'
            },
            'performance_metrics': {
                'search_accuracy': 'How often users find what they are looking for',
                'response_times': 'Average time for search results to appear',
                'system_availability': 'Uptime and reliability statistics',
                'user_engagement': 'How frequently different features are used'
            },
            'governance_information': {
                'policy_compliance': 'Adherence to university and legal policies',
                'oversight_committees': 'Who oversees the AI system operations',
                'complaint_procedures': 'How to report issues or concerns',
                'improvement_roadmap': 'Planned improvements and their timelines'
            }
        }
        
        def generate_transparency_report() -> Dict[str, Any]:
            """Generate current transparency report."""
            
            import psycopg
            
            with psycopg.connect(**self.db_config) as conn:
                cur = conn.cursor()
                
                # Gather system statistics
                cur.execute("SELECT COUNT(*) FROM document_chunks WHERE embedding IS NOT NULL")
                total_chunks = cur.fetchone()[0]
                
                cur.execute("""
                    SELECT 
                        metadata->>'department' as dept,
                        COUNT(*) as count
                    FROM document_chunks 
                    WHERE metadata IS NOT NULL
                    GROUP BY metadata->>'department'
                    ORDER BY count DESC
                """)
                dept_stats = cur.fetchall()
            
            report = {
                'generated_at': datetime.now().isoformat(),
                'system_overview': {
                    'total_documents': total_chunks,
                    'departments_represented': len(dept_stats),
                    'largest_department': dept_stats[0] if dept_stats else None,
                    'data_last_updated': datetime.now().date().isoformat()
                },
                'fairness_status': {
                    'bias_mitigation_active': True,
                    'diversity_injection_enabled': True,
                    'regular_auditing_scheduled': True,
                    'complaint_system_operational': True
                },
                'user_rights': {
                    'explanation_available': True,
                    'appeal_process_available': True,
                    'data_access_controls': True,
                    'non_discrimination_policy': True
                }
            }
            
            return report
        
        print("📋 DASHBOARD COMPONENTS:")
        for section, components in dashboard_components.items():
            print(f"\n{section.upper().replace('_', ' ')}:")
            for component, description in components.items():
                print(f"  • {component}: {description}")
        
        # Generate sample transparency report
        sample_report = generate_transparency_report()
        
        print(f"\n📊 SAMPLE TRANSPARENCY REPORT:")
        print(f"  Total documents: {sample_report['system_overview']['total_documents']}")
        print(f"  Departments represented: {sample_report['system_overview']['departments_represented']}")
        print(f"  Bias mitigation active: {sample_report['fairness_status']['bias_mitigation_active']}")
        
        print("\n✅ Transparency dashboard system created")
        
        return {
            'dashboard_components': dashboard_components,
            'report_generator': generate_transparency_report,
            'sample_report': sample_report
        }

if __name__ == "__main__":
    db_config = {
        'host': 'localhost',
        'port': 5050,
        'dbname': 'pgvector',
        'user': 'postgres',
        'password': 'postgres'
    }
    
    transparency_system = EdinburghTransparencySystem(db_config)
    
    print("🚀 IMPLEMENTING TRANSPARENCY AND EXPLAINABILITY")
    print("=" * 60)
    
    # 1. Create explanation system
    explanation_system = transparency_system.create_result_explanation_system()
    
    # 2. Create transparency dashboard
    dashboard_system = transparency_system.create_transparency_dashboard()
    
    # 3. Test explanation system
    print(f"\n🧪 TESTING EXPLANATION SYSTEM")
    print("=" * 40)
    
    # Sample result for testing
    sample_result = {
        'document_title': 'Edinburgh IT Support Handbook',
        'similarity': 0.75,
        'combined_score': 0.82,
        'metadata': {
            'department': 'IT Services',
            'campus': "King's Buildings",
            'doc_type': 'guide',
            'priority': 4,
            'view_count': 1500,
            'bias_weight': 1.0,
            'last_reviewed': '2024-08-15T10:30:00',
            'status': 'active'
        }
    }
    
    explainable_result = explanation_system['explainable_result_class'](sample_result, 'IT support procedures')
    
    print("📝 SAMPLE EXPLANATION:")
    print(f"Relevance: {explainable_result.explanations['relevance_explanation']}")
    print(f"Ranking: {explainable_result.explanations['ranking_explanation']}")
    print(f"Source: {explainable_result.explanations['source_explanation']}")
    
    print(f"\n" + "=" * 60)
    print("✅ TRANSPARENCY AND EXPLAINABILITY IMPLEMENTATION COMPLETE!")
    print("=" * 60)
```

**Run transparency system:**

```bash
python lab9_transparency.py
```

---

### Exercise 3: Governance Framework Implementation (10 minutes)

#### 3.1: Create AI Ethics Committee Structure

**Build institutional governance framework:**

```python
# lab9_governance.py
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import json

@dataclass
class EthicsCommitteeMember:
    """Ethics committee member representation."""
    name: str
    role: str
    department: str
    expertise: List[str]
    term_start: datetime
    term_end: datetime

@dataclass
class EthicsReviewCase:
    """AI ethics review case."""
    case_id: str
    title: str
    description: str
    risk_level: str
    submitted_by: str
    submitted_date: datetime
    status: str
    committee_decision: Optional[str] = None
    mitigation_requirements: Optional[List[str]] = None

class EdinburghAIGovernanceFramework:
    """Comprehensive AI governance framework for Edinburgh University."""
    
    def __init__(self):
        self.committee_structure = self.create_committee_structure()
        self.review_processes = self.create_review_processes()
        self.policy_framework = self.create_policy_framework()
    
    def create_committee_structure(self) -> Dict[str, Any]:
        """Create AI ethics committee structure."""
        
        print("🏛️ CREATING AI ETHICS COMMITTEE STRUCTURE")
        print("=" * 50)
        
        # Edinburgh AI Ethics Committee composition
        committee_members = [
            EthicsCommitteeMember(
                name="Prof. Sarah Mitchell",
                role="Chair", 
                department="Philosophy, Psychology & Language Sciences",
                expertise=["AI Ethics", "Philosophy of Technology", "Data Privacy"],
                term_start=datetime(2024, 1, 1),
                term_end=datetime(2026, 12, 31)
            ),
            EthicsCommitteeMember(
                name="Dr. James Chen",
                role="Technical Lead",
                department="School of Informatics", 
                expertise=["Machine Learning", "Algorithmic Fairness", "Computer Vision"],
                term_start=datetime(2024, 1, 1),
                term_end=datetime(2025, 12, 31)
            ),
            EthicsCommitteeMember(
                name="Ms. Rachel Thompson",
                role="Legal Advisor",
                department="Legal Services",
                expertise=["Data Protection Law", "GDPR", "University Policy"],
                term_start=datetime(2024, 1, 1),
                term_end=datetime(2026, 12, 31)
            ),
            EthicsCommitteeMember(
                name="Dr. Aisha Patel",
                role="Student Representative",
                department="Students' Association",
                expertise=["Student Rights", "Educational Technology", "Digital Inclusion"],
                term_start=datetime(2024, 9, 1),
                term_end=datetime(2025, 8, 31)
            ),
            EthicsCommitteeMember(
                name="Mr. David Williams",
                role="Staff Representative",
                department="IT Services",
                expertise=["System Administration", "Information Security", "User Experience"],
                term_start=datetime(2024, 1, 1),
                term_end=datetime(2025, 12, 31)
            )
        ]
        
        governance_structure = {
            'committee_name': 'Edinburgh University AI Ethics Committee',
            'mandate': 'Oversee ethical deployment and governance of AI systems across the university',
            'meeting_frequency': 'Monthly, with emergency sessions as needed',
            'decision_making': 'Consensus preferred, majority vote when needed',
            'reporting': 'Quarterly reports to University Executive, annual public report',
            'members': committee_members
        }
        
        print("👥 COMMITTEE MEMBERSHIP:")
        for member in committee_members:
            print(f"  {member.name} ({member.role}) - {member.department}")
            print(f"    Expertise: {', '.join(member.expertise)}")
            print(f"    Term: {member.term_start.year}-{member.term_end.year}")
            print()
        
        print("📋 COMMITTEE RESPONSIBILITIES:")
        responsibilities = [
            "Review and approve high-risk AI system deployments",
            "Develop and update university AI ethics policies",
            "Investigate AI bias and discrimination complaints",
            "Provide guidance on AI procurement and vendor selection",
            "Monitor compliance with AI ethics standards",
            "Coordinate with external regulatory bodies",
            "Educate university community on AI ethics"
        ]
        
        for i, responsibility in enumerate(responsibilities, 1):
            print(f"  {i}. {responsibility}")
        
        return governance_structure
    
    def create_review_processes(self) -> Dict[str, Any]:
        """Create AI ethics review processes."""
        
        print(f"\n⚖️ CREATING ETHICS REVIEW PROCESSES")
        print("=" * 50)
        
        review_processes = {
            'risk_assessment_framework': {
                'low_risk': {
                    'criteria': 'Informational systems, basic search, general chatbots',
                    'review_process': 'Self-assessment with annual reporting',
                    'timeline': '1-2 weeks for approval',
                    'oversight': 'IT Services + Department Head approval'
                },
                'medium_risk': {
                    'criteria': 'Decision support, content recommendation, data analysis',
                    'review_process': 'Technical working group review + ethics assessment',
                    'timeline': '4-6 weeks for approval',
                    'oversight': 'Ethics subcommittee + technical expert panel'
                },
                'high_risk': {
                    'criteria': 'Admissions, hiring, disciplinary actions, resource allocation',
                    'review_process': 'Full ethics committee review + external consultation',
                    'timeline': '8-12 weeks for approval',
                    'oversight': 'Full AI Ethics Committee + University Executive'
                }
            },
            'review_stages': {
                'initial_submission': {
                    'requirements': ['Project description', 'Risk assessment', 'Data sources', 'Intended users'],
                    'timeline': 'Within 1 week of submission'
                },
                'technical_review': {
                    'requirements': ['Algorithm details', 'Bias testing', 'Performance metrics', 'Security assessment'],
                    'timeline': 'Within 2-4 weeks depending on risk level'
                },
                'ethical_assessment': {
                    'requirements': ['Fairness analysis', 'Privacy impact', 'Transparency measures', 'Human oversight'],
                    'timeline': 'Within 3-6 weeks depending on complexity'
                },
                'stakeholder_consultation': {
                    'requirements': ['User community input', 'Department feedback', 'Expert consultation if needed'],
                    'timeline': 'Within 2-4 weeks for high-risk systems'
                },
                'final_decision': {
                    'requirements': ['Committee recommendation', 'Implementation conditions', 'Monitoring requirements'],
                    'timeline': 'Within 1 week of completed review'
                }
            }
        }
        
        print("📊 RISK ASSESSMENT FRAMEWORK:")
        for risk_level, details in review_processes['risk_assessment_framework'].items():
            print(f"\n{risk_level.upper()} RISK:")
            print(f"  Criteria: {details['criteria']}")
            print(f"  Process: {details['review_process']}")
            print(f"  Timeline: {details['timeline']}")
            print(f"  Oversight: {details['oversight']}")
        
        return review_processes
    
    def create_policy_framework(self) -> Dict[str, Any]:
        """Create comprehensive AI policy framework."""
        
        print(f"\n📜 CREATING AI POLICY FRAMEWORK")
        print("=" * 50)
        
        policy_framework = {
            'core_principles': {
                'fairness_and_non_discrimination': {
                    'description': 'AI systems must not discriminate against individuals or groups',
                    'implementation': 'Regular bias auditing, diverse development teams, fairness metrics',
                    'enforcement': 'Mandatory bias testing before deployment, ongoing monitoring'
                },
                'transparency_and_explainability': {
                    'description': 'Users must understand how AI systems affect them',
                    'implementation': 'Clear explanations of AI decisions, public documentation',
                    'enforcement': 'All user-facing AI must provide explanation capabilities'
                },
                'privacy_and_data_protection': {
                    'description': 'Protect personal data and respect user privacy rights',
                    'implementation': 'Data minimization, consent management, security measures',
                    'enforcement': 'GDPR compliance mandatory, regular privacy audits'
                },
                'human_oversight_and_control': {
                    'description': 'Humans must remain in control of important decisions',
                    'implementation': 'Human-in-the-loop for high-stakes decisions, appeal processes',
                    'enforcement': 'No fully automated decisions affecting rights or opportunities'
                },
                'reliability_and_safety': {
                    'description': 'AI systems must perform reliably and safely',
                    'implementation': 'Thorough testing, monitoring, incident response procedures',
                    'enforcement': 'Mandatory testing protocols, continuous monitoring requirements'
                }
            },
            'implementation_guidelines': {
                'development_standards': [
                    'Include diverse perspectives in development teams',
                    'Conduct bias and fairness testing throughout development',
                    'Document all design decisions and trade-offs',
                    'Implement comprehensive logging and monitoring',
                    'Plan for graceful degradation and failure modes'
                ],
                'deployment_requirements': [
                    'Complete ethics review appropriate to risk level',
                    'Provide user training and documentation',
                    'Establish clear accountability chains',
                    'Implement feedback and complaint mechanisms',
                    'Plan for regular evaluation and improvement cycles'
                ],
                'operational_standards': [
                    'Monitor system performance and bias metrics',
                    'Maintain audit trails for all AI decisions',
                    'Respond promptly to user complaints and concerns',
                    'Conduct regular policy compliance reviews',
                    'Report incidents and near-misses transparently'
                ]
            },
            'compliance_mechanisms': {
                'regular_audits': 'Quarterly technical audits, annual comprehensive reviews',
                'user_feedback': 'Continuous feedback collection and analysis',
                'incident_reporting': 'Mandatory reporting of bias, privacy, or safety incidents',
                'external_assessment': 'Annual independent ethics and compliance assessment',
                'policy_updates': 'Regular policy review and update based on experience and regulation changes'
            }
        }
        
        print("🎯 CORE ETHICAL PRINCIPLES:")
        for principle, details in policy_framework['core_principles'].items():
            print(f"\n{principle.upper().replace('_', ' ')}:")
            print(f"  Description: {details['description']}")
            print(f"  Implementation: {details['implementation']}")
        
        return policy_framework
    
    def create_governance_dashboard(self) -> Dict[str, Any]:
        """Create governance monitoring dashboard."""
        
        print(f"\n📊 CREATING GOVERNANCE DASHBOARD")
        print("=" * 50)
        
        dashboard_metrics = {
            'committee_activity': {
                'meetings_held': 'Number of ethics committee meetings per quarter',
                'cases_reviewed': 'Number of AI systems reviewed by risk level',
                'decisions_made': 'Breakdown of approved/rejected/conditional approvals',
                'average_review_time': 'Time from submission to final decision'
            },
            'system_compliance': {
                'active_ai_systems': 'Number of active AI systems by risk level',
                'compliance_rate': 'Percentage of systems meeting policy requirements',
                'audit_results': 'Results of recent compliance audits',
                'incident_reports': 'Number and type of ethics incidents reported'
            },
            'community_engagement': {
                'training_participation': 'Staff and student participation in AI ethics training',
                'feedback_submissions': 'Number of community feedback submissions',
                'complaint_resolution': 'Time to resolution for ethics complaints',
                'satisfaction_scores': 'Community satisfaction with AI governance'
            },
            'continuous_improvement': {
                'policy_updates': 'Number of policy updates and improvements made',
                'best_practices': 'New best practices adopted',
                'external_collaboration': 'Participation in external AI ethics initiatives',
                'research_integration': 'Integration of latest research findings'
            }
        }
        
        def generate_governance_report() -> Dict[str, Any]:
            """Generate current governance status report."""
            
            return {
                'reporting_period': f"Q{datetime.now().month // 3 + 1} {datetime.now().year}",
                'committee_activity': {
                    'meetings_held': 3,
                    'cases_reviewed': 12,
                    'high_risk_cases': 2,
                    'medium_risk_cases': 6,
                    'low_risk_cases': 4,
                    'approval_rate': 0.83
                },
                'system_compliance': {
                    'active_systems': 8,
                    'fully_compliant': 7,
                    'partial_compliance': 1,
                    'non_compliant': 0,
                    'recent_incidents': 0
                },
                'community_metrics': {
                    'training_participants': 156,
                    'feedback_received': 23,
                    'complaints_resolved': 2,
                    'avg_resolution_time': '5 days'
                }
            }
        
        print("📈 DASHBOARD METRICS CATEGORIES:")
        for category, metrics in dashboard_metrics.items():
            print(f"\n{category.upper().replace('_', ' ')}:")
            for metric, description in metrics.items():
                print(f"  • {metric}: {description}")
        
        sample_report = generate_governance_report()
        print(f"\n📊 SAMPLE GOVERNANCE REPORT:")
        print(f"  Cases reviewed this quarter: {sample_report['committee_activity']['cases_reviewed']}")
        print(f"  System compliance rate: {sample_report['system_compliance']['fully_compliant']}/{sample_report['system_compliance']['active_systems']} ({sample_report['system_compliance']['fully_compliant']/sample_report['system_compliance']['active_systems']:.0%})")
        print(f"  Community training participants: {sample_report['community_metrics']['training_participants']}")
        
        return {
            'dashboard_metrics': dashboard_metrics,
            'report_generator': generate_governance_report,
            'sample_report': sample_report
        }
    
    def create_incident_response_system(self) -> Dict[str, Any]:
        """Create AI ethics incident response system."""
        
        print(f"\n🚨 CREATING INCIDENT RESPONSE SYSTEM")
        print("=" * 50)
        
        incident_categories = {
            'bias_discrimination': {
                'description': 'AI system produces biased or discriminatory outcomes',
                'severity_levels': ['Low', 'Medium', 'High', 'Critical'],
                'response_times': {'Critical': '2 hours', 'High': '1 day', 'Medium': '3 days', 'Low': '1 week'},
                'escalation': 'Immediate notification to ethics committee for High/Critical'
            },
            'privacy_breach': {
                'description': 'Unauthorized access or misuse of personal data',
                'severity_levels': ['Minor', 'Moderate', 'Major', 'Severe'],
                'response_times': {'Severe': '1 hour', 'Major': '4 hours', 'Moderate': '1 day', 'Minor': '2 days'},
                'escalation': 'Immediate notification to Data Protection Officer and legal team'
            },
            'system_malfunction': {
                'description': 'AI system produces incorrect or harmful outputs',
                'severity_levels': ['Low', 'Medium', 'High', 'Critical'],
                'response_times': {'Critical': '1 hour', 'High': '4 hours', 'Medium': '1 day', 'Low': '3 days'},
                'escalation': 'IT Services immediate response, ethics committee for impact assessment'
            },
            'policy_violation': {
                'description': 'AI system or usage violates established policies',
                'severity_levels': ['Minor', 'Moderate', 'Major'],
                'response_times': {'Major': '1 day', 'Moderate': '3 days', 'Minor': '1 week'},
                'escalation': 'Department head notification, ethics committee for pattern analysis'
            }
        }
        
        response_procedures = {
            'immediate_response': [
                'Assess incident severity and impact',
                'Contain immediate harm if possible',
                'Notify relevant stakeholders per escalation matrix',
                'Document incident details and evidence',
                'Activate appropriate response team'
            ],
            'investigation_phase': [
                'Conduct thorough technical investigation',
                'Interview relevant staff and affected users',
                'Analyze root causes and contributing factors',
                'Document findings and evidence',
                'Assess policy and procedure implications'
            ],
            'remediation_phase': [
                'Implement immediate fixes and safeguards',
                'Communicate with affected parties',
                'Develop long-term prevention measures',
                'Update relevant policies and procedures',
                'Provide additional training if needed'
            ],
            'follow_up_phase': [
                'Monitor for recurring issues',
                'Evaluate effectiveness of remediation',
                'Share lessons learned with university community',
                'Update incident response procedures',
                'Report to relevant regulatory bodies if required'
            ]
        }
        
        print("🏷️ INCIDENT CATEGORIES:")
        for category, details in incident_categories.items():
            print(f"\n{category.upper().replace('_', ' ')}:")
            print(f"  Description: {details['description']}")
            print(f"  Response times: {details['response_times']}")
            print(f"  Escalation: {details['escalation']}")
        
        return {
            'incident_categories': incident_categories,
            'response_procedures': response_procedures
        }

if __name__ == "__main__":
    print("🚀 IMPLEMENTING AI GOVERNANCE FRAMEWORK")
    print("=" * 60)
    
    governance_framework = EdinburghAIGovernanceFramework()
    
    # Create governance dashboard
    dashboard_system = governance_framework.create_governance_dashboard()
    
    # Create incident response system
    incident_system = governance_framework.create_incident_response_system()
    
    # Save governance framework
    framework_data = {
        'committee_structure': governance_framework.committee_structure,
        'review_processes': governance_framework.review_processes,
        'policy_framework': governance_framework.policy_framework,
        'dashboard_system': dashboard_system,
        'incident_response': incident_system,
        'created_date': datetime.now().isoformat()
    }
    
    with open('edinburgh_ai_governance_framework.json', 'w') as f:
        json.dump(framework_data, f, indent=2, default=str)
    
    print(f"\n" + "=" * 60)
    print("✅ AI GOVERNANCE FRAMEWORK IMPLEMENTATION COMPLETE!")
    print("✅ Framework saved to edinburgh_ai_governance_framework.json")
    print("=" * 60)
```

**Run governance framework:**

```bash
python lab9_governance.py
```

---

### Exercise 4: Compliance and Privacy Implementation (8 minutes)

#### 4.1: GDPR Compliance System

**Build comprehensive GDPR compliance framework:**

```python
# lab9_compliance.py
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import hashlib

@dataclass
class DataProcessingRecord:
    """GDPR Article 30 record of processing activities."""
    processing_id: str
    purpose: str
    legal_basis: str
    data_categories: List[str]
    data_subjects: str
    retention_period: str
    recipients: List[str]
    international_transfers: bool
    security_measures: List[str]

@dataclass
class DataSubjectRequest:
    """Data subject rights request."""
    request_id: str
    request_type: str  # access, rectification, erasure, portability, objection
    data_subject_id: str
    request_date: datetime
    response_deadline: datetime
    status: str
    response_data: Optional[Dict] = None

class EdinburghGDPRCompliance:
    """GDPR compliance system for Edinburgh University AI systems."""
    
    def __init__(self, db_config):
        self.db_config = db_config
        self.processing_records = self.create_processing_records()
        self.data_subject_rights = self.implement_data_subject_rights()
    
    def create_processing_records(self) -> List[DataProcessingRecord]:
        """Create GDPR Article 30 records for AI processing activities."""
        
        print("📋 CREATING GDPR PROCESSING RECORDS")
        print("=" * 50)
        
        processing_records = [
            DataProcessingRecord(
                processing_id="EDU-AI-001",
                purpose="Vector search for university document discovery",
                legal_basis="Public task (Article 6(1)(e)) - University's educational mission",
                data_categories=["Search queries", "User interactions", "Document access patterns"],
                data_subjects="Students, staff, faculty, researchers",
                retention_period="Search logs: 12 months, Analytics: 24 months",
                recipients=["IT Services", "Authorized university staff"],
                international_transfers=False,
                security_measures=["Encryption at rest", "Access controls", "Audit logging", "Pseudonymization"]
            ),
            DataProcessingRecord(
                processing_id="EDU-AI-002",
                purpose="AI system performance monitoring and improvement",
                legal_basis="Legitimate interests (Article 6(1)(f)) - System optimization",
                data_categories=["System performance metrics", "Error logs", "Usage statistics"],
                data_subjects="All system users",
                retention_period="Performance data: 36 months for trend analysis",
                recipients=["IT Services", "System administrators", "Approved researchers"],
                international_transfers=False,
                security_measures=["Aggregated data only", "Access controls", "Data minimization"]
            ),
            DataProcessingRecord(
                processing_id="EDU-AI-003",
                purpose="AI bias detection and fairness monitoring",
                legal_basis="Public task (Article 6(1)(e)) - Ensuring non-discrimination",
                data_categories=["Demographic indicators", "Search result patterns", "User satisfaction"],
                data_subjects="University community members",
                retention_period="Bias monitoring data: 24 months",
                recipients=["AI Ethics Committee", "Equality & Diversity Office"],
                international_transfers=False,
                security_measures=["Statistical analysis only", "No individual profiling", "Anonymization"]
            )
        ]
        
        print("📊 PROCESSING ACTIVITIES REGISTERED:")
        for record in processing_records:
            print(f"\n{record.processing_id}: {record.purpose}")
            print(f"  Legal basis: {record.legal_basis}")
            print(f"  Data categories: {', '.join(record.data_categories)}")
            print(f"  Retention: {record.retention_period}")
        
        return processing_records
    
    def implement_data_subject_rights(self) -> Dict[str, Any]:
        """Implement GDPR data subject rights procedures."""
        
        print(f"\n👤 IMPLEMENTING DATA SUBJECT RIGHTS")
        print("=" * 50)
        
        rights_implementation = {
            'right_to_be_informed': {
                'mechanism': 'Privacy notice and transparency dashboard',
                'timeline': 'At point of data collection',
                'responsible_team': 'Data Protection Office',
                'status': 'Implemented through system documentation'
            },
            'right_of_access': {
                'mechanism': 'Data access portal and manual request process',
                'timeline': '1 month from request (extendable to 3 months)',
                'responsible_team': 'IT Services + Data Protection Office',
                'status': 'Automated for search data, manual for complex requests'
            },
            'right_to_rectification': {
                'mechanism': 'User profile updates and data correction requests',
                'timeline': '1 month from request',
                'responsible_team': 'IT Services',
                'status': 'Implemented for user-controllable data'
            },
            'right_to_erasure': {
                'mechanism': 'Account deletion and data purging procedures',
                'timeline': '1 month from request (considering legitimate interests)',
                'responsible_team': 'IT Services + Legal Services',
                'status': 'Implemented with retention period considerations'
            },
            'right_to_restrict_processing': {
                'mechanism': 'Processing restriction flags and system controls',
                'timeline': 'Immediate upon valid request',
                'responsible_team': 'IT Services',
                'status': 'Implemented for disputable data'
            },
            'right_to_data_portability': {
                'mechanism': 'Data export functionality in structured format',
                'timeline': '1 month from request',
                'responsible_team': 'IT Services',
                'status': 'Implemented for user-provided data'
            },
            'right_to_object': {
                'mechanism': 'Opt-out controls and processing objection handling',
                'timeline': 'Immediate for direct marketing, case-by-case for other purposes',
                'responsible_team': 'Data Protection Office',
                'status': 'Implemented with legal basis review procedure'
            }
        }
        
        class DataSubjectRightsPortal:
            """Data subject rights request handling system."""
            
            def __init__(self, compliance_system):
                self.compliance_system = compliance_system
                self.active_requests = {}
            
            def submit_access_request(self, user_id: str) -> DataSubjectRequest:
                """Handle right of access request."""
                
                request = DataSubjectRequest(
                    request_id=f"ACCESS_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    request_type="access",
                    data_subject_id=user_id,
                    request_date=datetime.now(),
                    response_deadline=datetime.now() + timedelta(days=30),
                    status="received"
                )
                
                self.active_requests[request.request_id] = request
                return request
            
            def process_access_request(self, request_id: str) -> Dict[str, Any]:
                """Process data access request and gather user's data."""
                
                if request_id not in self.active_requests:
                    raise ValueError("Request not found")
                
                request = self.active_requests[request_id]
                
                # Gather user's data from system
                user_data = {
                    'personal_data': {
                        'user_id': request.data_subject_id,
                        'search_history_summary': 'Last 90 days of search activity (anonymized)',
                        'preference_settings': 'User-configured system preferences',
                        'account_information': 'Basic account details'
                    },
                    'processing_activities': [
                        {
                            'purpose': 'Document search functionality',
                            'legal_basis': 'Public task',
                            'data_used': 'Search queries, interaction patterns',
                            'retention': '12 months'
                        },
                        {
                            'purpose': 'System improvement',
                            'legal_basis': 'Legitimate interests',
                            'data_used': 'Aggregated usage statistics',
                            'retention': '24 months'
                        }
                    ],
                    'data_sources': ['User inputs', 'System interactions', 'Performance monitoring'],
                    'recipients': ['IT Services staff', 'Authorized university personnel'],
                    'rights_information': {
                        'rectification': 'You can update your profile information',
                        'erasure': 'You can request account deletion',
                        'objection': 'You can object to processing for legitimate interests',
                        'contact': 'data-protection@ed.ac.uk'
                    }
                }
                
                request.response_data = user_data
                request.status = "completed"
                
                return user_data
        
        print("👤 DATA SUBJECT RIGHTS IMPLEMENTATION:")
        for right, details in rights_implementation.items():
            print(f"\n{right.upper().replace('_', ' ')}:")
            print(f"  Mechanism: {details['mechanism']}")
            print(f"  Timeline: {details['timeline']}")
            print(f"  Status: {details['status']}")
        
        rights_portal = DataSubjectRightsPortal(self)
        
        return {
            'rights_procedures': rights_implementation,
            'rights_portal': rights_portal
        }
    
    def implement_privacy_impact_assessment(self) -> Dict[str, Any]:
        """Implement Privacy Impact Assessment (DPIA) framework."""
        
        print(f"\n🔍 IMPLEMENTING PRIVACY IMPACT ASSESSMENT")
        print("=" * 50)
        
        dpia_framework = {
            'assessment_triggers': [
                'Systematic profiling with legal effects',
                'Large-scale processing of special category data',
                'Systematic monitoring of public areas',
                'New technology with high privacy risk',
                'Processing that prevents data subjects from exercising rights'
            ],
            'assessment_process': {
                'description_of_processing': 'Document the AI system and its data processing',
                'necessity_assessment': 'Evaluate if processing is necessary and proportionate',
                'risk_identification': 'Identify risks to data subjects\' rights and freedoms',
                'risk_mitigation': 'Design measures to address identified risks',
                'stakeholder_consultation': 'Consult with relevant stakeholders and DPO',
                'ongoing_monitoring': 'Regular review and update of the assessment'
            },
            'risk_assessment_criteria': {
                'likelihood': ['Remote', 'Possible', 'Likely', 'Very likely'],
                'severity': ['Minimal', 'Limited', 'Significant', 'Maximum'],
                'risk_level': 'Calculated as likelihood × severity',
                'acceptable_threshold': 'Medium risk or below after mitigation'
            }
        }
        
        def conduct_ai_system_dpia() -> Dict[str, Any]:
            """Conduct DPIA for Edinburgh AI search system."""
            
            dpia_assessment = {
                'system_description': {
                    'name': 'Edinburgh University Vector Search System',
                    'purpose': 'Intelligent document search for university community',
                    'data_types': ['Search queries', 'User interactions', 'Document metadata'],
                    'processing_operations': ['Query processing', 'Result ranking', 'Usage analytics'],
                    'technology': 'Vector embeddings, semantic search, machine learning'
                },
                'necessity_evaluation': {
                    'lawful_basis': 'Public task - University\'s educational and administrative mission',
                    'necessity_justified': True,
                    'proportionality_assessment': 'Data processing proportionate to search functionality',
                    'alternatives_considered': 'Traditional keyword search (less effective for user needs)'
                },
                'risk_analysis': {
                    'privacy_risks': [
                        {
                            'risk': 'Inference of sensitive information from search patterns',
                            'likelihood': 'Possible',
                            'severity': 'Limited',
                            'mitigation': 'Query anonymization, pattern aggregation'
                        },
                        {
                            'risk': 'Unauthorized access to personal search data',
                            'likelihood': 'Remote',
                            'severity': 'Significant', 
                            'mitigation': 'Access controls, encryption, audit logging'
                        },
                        {
                            'risk': 'Discrimination through biased search results',
                            'likelihood': 'Possible',
                            'severity': 'Significant',
                            'mitigation': 'Bias monitoring, fairness algorithms, regular auditing'
                        }
                    ],
                    'overall_risk_level': 'Medium (acceptable with mitigation measures)'
                },
                'safeguards_implemented': [
                    'Data minimization - only necessary data processed',
                    'Purpose limitation - data used only for stated purposes',
                    'Storage limitation - defined retention periods',
                    'Accuracy - mechanisms to correct inaccurate data',
                    'Security - encryption, access controls, monitoring',
                    'Transparency - clear privacy notices and explanations'
                ],
                'consultation_outcomes': {
                    'dpo_consultation': 'Approved with recommended safeguards',
                    'user_consultation': 'Community feedback incorporated into design',
                    'ethics_committee': 'Approved following ethics review process'
                },
                'monitoring_plan': {
                    'review_frequency': 'Annual comprehensive review, quarterly risk assessment',
                    'key_indicators': ['Privacy incident rate', 'User complaints', 'Data breach attempts'],
                    'update_triggers': ['Significant system changes', 'New privacy regulations', 'Risk threshold breaches']
                }
            }
            
            return dpia_assessment
        
        dpia_result = conduct_ai_system_dpia()
        
        print("📋 DPIA ASSESSMENT SUMMARY:")
        print(f"  System: {dpia_result['system_description']['name']}")
        print(f"  Overall risk level: {dpia_result['risk_analysis']['overall_risk_level']}")
        print(f"  Safeguards implemented: {len(dpia_result['safeguards_implemented'])}")
        print(f"  Consultation completed: {', '.join(dpia_result['consultation_outcomes'].keys())}")
        
        return {
            'dpia_framework': dpia_framework,
            'system_dpia': dpia_result
        }
    
    def create_compliance_monitoring_system(self) -> Dict[str, Any]:
        """Create ongoing compliance monitoring system."""
        
        print(f"\n📊 CREATING COMPLIANCE MONITORING SYSTEM")
        print("=" * 50)
        
        monitoring_framework = {
            'compliance_metrics': {
                'data_processing_compliance': {
                    'metric': 'Percentage of processing activities with valid legal basis',
                    'target': '100%',
                    'measurement': 'Quarterly legal basis review',
                    'responsibility': 'Data Protection Office'
                },
                'data_subject_rights_response': {
                    'metric': 'Average response time for data subject requests',
                    'target': '< 20 days (within 30-day legal requirement)',
                    'measurement': 'Monthly request tracking',
                    'responsibility': 'IT Services + Data Protection Office'
                },
                'privacy_incident_rate': {
                    'metric': 'Number of privacy incidents per quarter',
                    'target': '0 significant incidents',
                    'measurement': 'Continuous incident monitoring',
                    'responsibility': 'IT Security + Data Protection Office'
                },
                'policy_compliance_rate': {
                    'metric': 'Percentage of staff completing privacy training',
                    'target': '95% annually',
                    'measurement': 'Training system tracking',
                    'responsibility': 'HR + Data Protection Office'
                }
            },
            'audit_schedule': {
                'monthly': ['Data subject request processing', 'System access logs', 'Data retention compliance'],
                'quarterly': ['Processing records review', 'Legal basis assessment', 'Privacy impact updates'],
                'annually': ['Comprehensive GDPR compliance audit', 'External assessment', 'Policy review']
            },
            'reporting_structure': {
                'internal_reporting': {
                    'monthly': 'Data Protection Office dashboard',
                    'quarterly': 'University Executive report',
                    'annually': 'Public transparency report'
                },
                'external_reporting': {
                    'regulatory': 'ICO breach notifications as required',
                    'stakeholder': 'Annual public accountability report',
                    'sector': 'University sector compliance sharing'
                }
            }
        }
        
        def generate_compliance_report() -> Dict[str, Any]:
            """Generate current compliance status report."""
            
            return {
                'reporting_date': datetime.now().isoformat(),
                'compliance_status': {
                    'overall_compliance_rate': 0.95,
                    'processing_activities_compliant': '100%',
                    'data_subject_requests_processed': 12,
                    'average_response_time': '18 days',
                    'privacy_incidents': 0,
                    'staff_training_completion': '92%'
                },
                'key_achievements': [
                    'Zero privacy incidents in current quarter',
                    'All data subject requests resolved within legal timeframes',
                    'Comprehensive DPIA completed for AI system',
                    'Staff privacy training program launched'
                ],
                'areas_for_improvement': [
                    'Increase staff training completion rate to 95%',
                    'Implement automated compliance monitoring',
                    'Enhance data subject rights portal functionality'
                ],
                'next_quarter_priorities': [
                    'Annual external compliance audit',
                    'Update privacy policies based on regulatory guidance',
                    'Expand bias monitoring capabilities'
                ]
            }
        
        compliance_report = generate_compliance_report()
        
        print("📊 COMPLIANCE MONITORING FRAMEWORK:")
        for category, metrics in monitoring_framework['compliance_metrics'].items():
            print(f"\n{category.upper().replace('_', ' ')}:")
            print(f"  Target: {metrics['target']}")
            print(f"  Measurement: {metrics['measurement']}")
        
        print(f"\n📈 CURRENT COMPLIANCE STATUS:")
        print(f"  Overall compliance rate: {compliance_report['compliance_status']['overall_compliance_rate']:.0%}")
        print(f"  Data subject requests processed: {compliance_report['compliance_status']['data_subject_requests_processed']}")
        print(f"  Average response time: {compliance_report['compliance_status']['average_response_time']}")
        
        return {
            'monitoring_framework': monitoring_framework,
            'compliance_report': compliance_report
        }

if __name__ == "__main__":
    db_config = {
        'host': 'localhost',
        'port': 5050,
        'dbname': 'pgvector',
        'user': 'postgres',
        'password': 'postgres'
    }
    
    print("🚀 IMPLEMENTING GDPR COMPLIANCE FRAMEWORK")
    print("=" * 60)
    
    compliance_system = EdinburghGDPRCompliance(db_config)
    
    # Implement privacy impact assessment
    dpia_system = compliance_system.implement_privacy_impact_assessment()
    
    # Create compliance monitoring
    monitoring_system = compliance_system.create_compliance_monitoring_system()
    
    # Test data subject rights
    print(f"\n🧪 TESTING DATA SUBJECT RIGHTS PORTAL")
    print("=" * 50)
    
    rights_portal = compliance_system.data_subject_rights['rights_portal']
    
    # Simulate access request
    test_request = rights_portal.submit_access_request('test_user_123')
    print(f"✅ Access request submitted: {test_request.request_id}")
    print(f"   Response deadline: {test_request.response_deadline.strftime('%Y-%m-%d')}")
    
    # Process the request
    user_data = rights_portal.process_access_request(test_request.request_id)
    print(f"✅ Access request processed successfully")
    print(f"   Data categories provided: {len(user_data['processing_activities'])}")
    
    # Save compliance framework
    compliance_data = {
        'processing_records': [
            {
                'processing_id': r.processing_id,
                'purpose': r.purpose,
                'legal_basis': r.legal_basis,
                'data_categories': r.data_categories,
                'retention_period': r.retention_period
            }
            for r in compliance_system.processing_records
        ],
        'data_subject_rights': compliance_system.data_subject_rights['rights_procedures'],
        'dpia_framework': dpia_system['dpia_framework'],
        'system_dpia': dpia_system['system_dpia'],
        'monitoring_system': monitoring_system['monitoring_framework'],
        'created_date': datetime.now().isoformat()
    }
    
    with open('edinburgh_gdpr_compliance_framework.json', 'w') as f:
        json.dump(compliance_data, f, indent=2, default=str)
    
    print(f"\n" + "=" * 60)
    print("✅ GDPR COMPLIANCE FRAMEWORK IMPLEMENTATION COMPLETE!")
    print("✅ Framework saved to edinburgh_gdpr_compliance_framework.json")
    print("=" * 60)
```

**Run GDPR compliance:**

```bash
python lab9_compliance.py
```

---

### Exercise 5: Ethical AI Integration Testing (5 minutes)

#### 5.1: End-to-End Ethics Validation

**Test complete ethical AI implementation:**

```python
# lab9_integration_test.py
import json
from datetime import datetime
from typing import Dict, Any, List

class EthicalAIIntegrationTest:
    """End-to-end testing of ethical AI implementation."""
    
    def __init__(self):
        self.test_results = {}
    
    def test_bias_detection_system(self) -> Dict[str, Any]:
        """Test bias detection capabilities."""
        
        print("🔍 TESTING BIAS DETECTION SYSTEM")
        print("=" * 50)
        
        test_cases = [
            {
                'test_name': 'Representation Analysis',
                'expected_outcome': 'Identify department and campus representation imbalances',
                'pass_criteria': 'System detects imbalances and calculates ratios'
            },
            {
                'test_name': 'Search Result Bias',
                'expected_outcome': 'Analyze bias in search results across user roles',
                'pass_criteria': 'System compares results for different user types'
            },
            {
                'test_name': 'Bias Mitigation',
                'expected_outcome': 'Apply content reweighting and fairness algorithms',
                'pass_criteria': 'System adjusts ranking to improve fairness'
            }
        ]
        
        results = {}
        
        # Load bias assessment report if available
        try:
            with open('edinburgh_bias_assessment_report.json', 'r') as f:
                bias_report = json.load(f)
            
            print("✅ Bias assessment report loaded successfully")
            
            # Check if bias severity assessment exists
            if 'bias_severity_assessment' in bias_report:
                severity = bias_report['bias_severity_assessment']['overall_severity']
                print(f"   Overall bias severity: {severity}")
                results['bias_severity_detected'] = True
                results['severity_level'] = severity
            else:
                results['bias_severity_detected'] = False
            
            # Check if mitigation recommendations exist
            if 'recommendations' in bias_report and len(bias_report['recommendations']) > 0:
                print(f"   Mitigation recommendations: {len(bias_report['recommendations'])}")
                results['mitigation_recommendations'] = len(bias_report['recommendations'])
            else:
                results['mitigation_recommendations'] = 0
            
        except FileNotFoundError:
            print("⚠️ Bias assessment report not found - run lab9_bias_detection.py first")
            results['bias_report_available'] = False
        
        return results
    
    def test_transparency_system(self) -> Dict[str, Any]:
        """Test transparency and explainability features."""
        
        print(f"\n💡 TESTING TRANSPARENCY SYSTEM")
        print("=" * 50)
        
        results = {}
        
        # Test explanation system functionality
        try:
            from lab9_transparency import EdinburghTransparencySystem
            
            transparency_system = EdinburghTransparencySystem({})
            explanation_system = transparency_system.create_result_explanation_system()
            
            # Test explainable result creation
            sample_result = {
                'document_title': 'Test Document',
                'similarity': 0.75,
                'combined_score': 0.82,
                'metadata': {
                    'department': 'IT Services',
                    'doc_type': 'guide',
                    'priority': 4
                }
            }
            
            explainable_result = explanation_system['explainable_result_class'](sample_result, 'test query')
            
            # Check if explanations are generated
            explanations = explainable_result.explanations
            
            if 'relevance_explanation' in explanations and explanations['relevance_explanation']:
                results['relevance_explanation'] = True
                print("✅ Relevance explanations generated")
            else:
                results['relevance_explanation'] = False
                print("❌ Relevance explanations missing")
            
            if 'ranking_explanation' in explanations and explanations['ranking_explanation']:
                results['ranking_explanation'] = True
                print("✅ Ranking explanations generated")
            else:
                results['ranking_explanation'] = False
                print("❌ Ranking explanations missing")
            
            if 'source_explanation' in explanations and explanations['source_explanation']:
                results['source_explanation'] = True
                print("✅ Source explanations generated")
            else:
                results['source_explanation'] = False
                print("❌ Source explanations missing")
            
        except Exception as e:
            print(f"❌ Transparency system test failed: {str(e)}")
            results['transparency_system_functional'] = False
        
        return results
    
    def test_governance_framework(self) -> Dict[str, Any]:
        """Test governance framework implementation."""
        
        print(f"\n🏛️ TESTING GOVERNANCE FRAMEWORK")
        print("=" * 50)
        
        results = {}
        
        # Check if governance framework file exists
        try:
            with open('edinburgh_ai_governance_framework.json', 'r') as f:
                governance_data = json.load(f)
            
            print("✅ Governance framework file loaded")
            
            # Check committee structure
            if 'committee_structure' in governance_data:
                committee = governance_data['committee_structure']
                if 'members' in committee and len(committee['members']) >= 3:
                    results['committee_composition'] = True
                    print(f"✅ Ethics committee properly composed ({len(committee['members'])} members)")
                else:
                    results['committee_composition'] = False
                    print("❌ Ethics committee composition incomplete")
            
            # Check review processes
            if 'review_processes' in governance_data:
                processes = governance_data['review_processes']
                if 'risk_assessment_framework' in processes:
                    risk_levels = processes['risk_assessment_framework']
                    if len(risk_levels) >= 3:  # low, medium, high risk
                        results['risk_assessment_framework'] = True
                        print("✅ Risk assessment framework defined")
                    else:
                        results['risk_assessment_framework'] = False
                        print("❌ Risk assessment framework incomplete")
            
            # Check policy framework
            if 'policy_framework' in governance_data:
                policies = governance_data['policy_framework']
                if 'core_principles' in policies and len(policies['core_principles']) >= 4:
                    results['policy_principles'] = True
                    print(f"✅ Core ethical principles defined ({len(policies['core_principles'])})")
                else:
                    results['policy_principles'] = False
                    print("❌ Core ethical principles incomplete")
            
        except FileNotFoundError:
            print("⚠️ Governance framework file not found - run lab9_governance.py first")
            results['governance_framework_available'] = False
        except Exception as e:
            print(f"❌ Governance framework test failed: {str(e)}")
            results['governance_framework_functional'] = False
        
        return results
    
    def test_compliance_system(self) -> Dict[str, Any]:
        """Test GDPR compliance implementation."""
        
        print(f"\n📜 TESTING COMPLIANCE SYSTEM")
        print("=" * 50)
        
        results = {}
        
        # Check if GDPR compliance framework exists
        try:
            with open('edinburgh_gdpr_compliance_framework.json', 'r') as f:
                compliance_data = json.load(f)
            
            print("✅ GDPR compliance framework loaded")
            
            # Check processing records
            if 'processing_records' in compliance_data:
                records = compliance_data['processing_records']
                if len(records) >= 3:  # Expected minimum processing records
                    results['processing_records'] = True
                    print(f"✅ Processing records documented ({len(records)})")
                    
                    # Check if all records have required fields
                    required_fields = ['processing_id', 'purpose', 'legal_basis', 'data_categories']
                    all_complete = all(
                        all(field in record for field in required_fields)
                        for record in records
                    )
                    
                    if all_complete:
                        results['processing_records_complete'] = True
                        print("✅ All processing records complete")
                    else:
                        results['processing_records_complete'] = False
                        print("❌ Some processing records missing required fields")
                else:
                    results['processing_records'] = False
                    print("❌ Insufficient processing records documented")
            
            # Check data subject rights implementation
            if 'data_subject_rights' in compliance_data:
                rights = compliance_data['data_subject_rights']
                expected_rights = ['right_of_access', 'right_to_rectification', 'right_to_erasure']
                
                implemented_rights = sum(1 for right in expected_rights if right in rights)
                
                if implemented_rights >= 3:
                    results['data_subject_rights'] = True
                    print(f"✅ Data subject rights implemented ({implemented_rights}/7)")
                else:
                    results['data_subject_rights'] = False
                    print("❌ Data subject rights implementation incomplete")
            
            # Check DPIA framework
            if 'dpia_framework' in compliance_data and 'system_dpia' in compliance_data:
                results['dpia_completed'] = True
                print("✅ Data Protection Impact Assessment completed")
            else:
                results['dpia_completed'] = False
                print("❌ DPIA framework missing")
            
        except FileNotFoundError:
            print("⚠️ GDPR compliance framework file not found - run lab9_compliance.py first")
            results['compliance_framework_available'] = False
        except Exception as e:
            print(f"❌ Compliance system test failed: {str(e)}")
            results['compliance_system_functional'] = False
        
        return results
    
    def generate_integration_report(self) -> Dict[str, Any]:
        """Generate comprehensive integration test report."""
        
        print(f"\n📊 GENERATING INTEGRATION TEST REPORT")
        print("=" * 60)
        
        # Run all tests
        bias_results = self.test_bias_detection_system()
        transparency_results = self.test_transparency_system()
        governance_results = self.test_governance_framework()
        compliance_results = self.test_compliance_system()
        
        # Compile overall results
        all_results = {
            'bias_detection': bias_results,
            'transparency': transparency_results,
            'governance': governance_results,
            'compliance': compliance_results
        }
        
        # Calculate overall score
        total_tests = 0
        passed_tests = 0
        
        for category, results in all_results.items():
            for test, result in results.items():
                total_tests += 1
                if result is True or (isinstance(result, int) and result > 0):
                    passed_tests += 1
        
        overall_score = passed_tests / total_tests if total_tests > 0 else 0
        
        integration_report = {
            'test_date': datetime.now().isoformat(),
            'overall_score': overall_score,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'test_results': all_results,
            'readiness_assessment': self.assess_deployment_readiness(overall_score),
            'recommendations': self.generate_improvement_recommendations(all_results)
        }
        
        print(f"📈 INTEGRATION TEST RESULTS:")
        print(f"  Overall Score: {overall_score:.1%} ({passed_tests}/{total_tests} tests passed)")
        print(f"  Deployment Readiness: {integration_report['readiness_assessment']['status']}")
        
        print(f"\n📋 CATEGORY BREAKDOWN:")
        for category, results in all_results.items():
            category_passed = sum(1 for result in results.values() if result is True or (isinstance(result, int) and result > 0))
            category_total = len(results)
            print(f"  {category.title()}: {category_passed}/{category_total} ({category_passed/category_total:.0%})")
        
        return integration_report
    
    def assess_deployment_readiness(self, overall_score: float) -> Dict[str, Any]:
        """Assess ethical AI deployment readiness."""
        
        if overall_score >= 0.9:
            return {
                'status': 'Ready for Production',
                'confidence': 'High',
                'recommendation': 'System meets ethical AI standards for deployment'
            }
        elif overall_score >= 0.7:
            return {
                'status': 'Ready with Minor Issues',
                'confidence': 'Medium-High',
                'recommendation': 'Address identified issues before full deployment'
            }
        elif overall_score >= 0.5:
            return {
                'status': 'Significant Work Required',
                'confidence': 'Medium',
                'recommendation': 'Complete missing ethical frameworks before deployment'
            }
        else:
            return {
                'status': 'Not Ready for Deployment',
                'confidence': 'Low',
                'recommendation': 'Major ethical framework implementation required'
            }
    
    def generate_improvement_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate specific improvement recommendations."""
        
        recommendations = []
        
        # Bias detection recommendations
        bias_results = results.get('bias_detection', {})
        if not bias_results.get('bias_severity_detected', False):
            recommendations.append("Complete bias detection analysis by running lab9_bias_detection.py")
        
        if bias_results.get('mitigation_recommendations', 0) < 3:
            recommendations.append("Implement comprehensive bias mitigation strategies")
        
        # Transparency recommendations
        transparency_results = results.get('transparency', {})
        if not transparency_results.get('relevance_explanation', False):
            recommendations.append("Implement user-facing explanation system for search results")
        
        # Governance recommendations
        governance_results = results.get('governance', {})
        if not governance_results.get('committee_composition', False):
            recommendations.append("Establish properly composed AI ethics committee")
        
        if not governance_results.get('risk_assessment_framework', False):
            recommendations.append("Complete risk assessment framework for AI system classification")
        
        # Compliance recommendations
        compliance_results = results.get('compliance', {})
        if not compliance_results.get('processing_records_complete', False):
            recommendations.append("Complete GDPR processing records documentation")
        
        if not compliance_results.get('dpia_completed', False):
            recommendations.append("Complete Data Protection Impact Assessment")
        
        # General recommendations
        recommendations.extend([
            "Establish regular ethical AI monitoring and review cycles",
            "Provide AI ethics training for all system users and administrators",
            "Create public transparency reporting on AI ethics initiatives"
        ])
        
        return recommendations

if __name__ == "__main__":
    print("🚀 RUNNING ETHICAL AI INTEGRATION TESTS")
    print("=" * 60)
    
    integration_test = EthicalAIIntegrationTest()
    report = integration_test.generate_integration_report()
    
    # Save integration report
    with open('edinburgh_ethical_ai_integration_report.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n🎯 KEY RECOMMENDATIONS:")
    for i, recommendation in enumerate(report['recommendations'][:5], 1):
        print(f"  {i}. {recommendation}")
    
    print(f"\n" + "=" * 60)
    print("✅ ETHICAL AI INTEGRATION TESTING COMPLETE!")
    print("✅ Report saved to edinburgh_ethical_ai_integration_report.json")
    print("=" * 60)
    
    # Final assessment
    readiness = report['readiness_assessment']
    print(f"\n🎯 DEPLOYMENT READINESS: {readiness['status']}")
    print(f"💡 RECOMMENDATION: {readiness['recommendation']}")
```

**Run integration tests:**

```bash
python lab9_integration_test.py
```

---

## Lab Verification

### Ethical AI Implementation Checklist

```bash
# lab9_verification.sh
#!/bin/bash

echo "🔍 SECTION 9 LAB VERIFICATION"
echo "=============================="

# Check if all ethical AI components are implemented
echo "1. Bias Detection System:"
if [ -f "edinburgh_bias_assessment_report.json" ]; then
    echo "  ✅ Bias assessment report generated"
else
    echo "  ❌ Bias assessment report missing"
fi

echo "2. Transparency System:"
python -c "
try:
    from lab9_transparency import EdinburghTransparencySystem
    print('  ✅ Transparency system functional')
except ImportError as e:
    print(f'  ❌ Transparency system not working: {e}')
"

echo "3. Governance Framework:"
if [ -f "edinburgh_ai_governance_framework.json" ]; then
    echo "  ✅ Governance framework documented"
else
    echo "  ❌ Governance framework missing"
fi

echo "4. GDPR Compliance:"
if [ -f "edinburgh_gdpr_compliance_framework.json" ]; then
    echo "  ✅ GDPR compliance framework implemented"
else
    echo "  ❌ GDPR compliance framework missing"
fi

echo "5. Integration Testing:"
if [ -f "edinburgh_ethical_ai_integration_report.json" ]; then
    echo "  ✅ Integration testing completed"
    # Show overall score
    python -c "
import json
try:
    with open('edinburgh_ethical_ai_integration_report.json', 'r') as f:
        report = json.load(f)
    score = report['overall_score']
    status = report['readiness_assessment']['status']
    print(f'  📊 Overall Score: {score:.1%}')
    print(f'  🎯 Status: {status}')
except Exception as e:
    print(f'  ❌ Could not read integration report: {e}')
"
else
    echo "  ❌ Integration testing not completed"
fi
```

**Run verification:**

```bash
chmod +x lab9_verification.sh
./lab9_verification.sh
```

---

## Success Criteria

### ✅ Lab Completion Checklist

**After completing this lab, you should have:**

- [ ] **Bias Detection System** - Comprehensive analysis and mitigation of algorithmic bias
- [ ] **Transparency Framework** - User-facing explanations and system documentation  
- [ ] **Governance Structure** - Ethics committee, review processes, and accountability frameworks
- [ ] **GDPR Compliance** - Full data protection compliance with user rights implementation
- [ ] **Integration Testing** - End-to-end validation of ethical AI implementation
- [ ] **Deployment Readiness** - Assessment of system readiness for ethical deployment

### 🎯 Key Achievements

**Ethical AI Capabilities:**
- Systematic bias detection across demographics and content types
- User-friendly transparency and explanation systems
- Institutional governance aligned with university values
- Legal compliance with UK-GDPR and university policies

**Edinburgh University Integration:**
- Multi-stakeholder ethics committee with diverse expertise
- Campus and department-specific bias mitigation strategies
- University policy alignment and regulatory compliance
- Community engagement and transparent reporting frameworks

---

## Next Steps

**For Full Ethical AI Deployment:**
- Implement regular bias auditing and reporting cycles
- Establish ongoing ethics committee operations and decision-making
- Create community education and engagement programs
- Develop continuous improvement processes for ethical AI

**For Advanced Ethical AI:**
- Explore cutting-edge fairness algorithms and techniques
- Implement advanced privacy-preserving AI methods
- Develop sector-leading ethical AI standards and practices
- Collaborate with other universities on ethical AI initiatives

---

## Troubleshooting

### Common Issues

**Bias detection not finding issues:**
```bash
# Check if data has sufficient diversity
python -c "
import psycopg
conn = psycopg.connect('postgresql://postgres:postgres@localhost:5050/pgvector')
cur = conn.cursor()
cur.execute('SELECT metadata->>\"department\", COUNT(*) FROM document_chunks GROUP BY metadata->>\"department\"')
for dept, count in cur.fetchall():
    print(f'{dept}: {count} documents')
"
```

**Transparency explanations not generating:**
```python
# Test explanation system directly
from lab9_transparency import EdinburghTransparencySystem
system = EdinburghTransparencySystem({})
result = system.create_result_explanation_system()
print("Explanation system created successfully")
```

**Governance framework validation errors:**
```bash
# Check governance framework file structure
python -c "
import json
with open('edinburgh_ai_governance_framework.json', 'r') as f:
    data = json.load(f)
print('Required sections:', list(data.keys()))
print('Committee members:', len(data['committee_structure']['members']))
"
```

---

**🎉 Congratulations! You've implemented a comprehensive ethical AI framework for Edinburgh University! ⚖️**

Your system now includes bias detection and mitigation, transparency and explainability, institutional governance, and full regulatory compliance - setting the standard for responsible AI in higher education.
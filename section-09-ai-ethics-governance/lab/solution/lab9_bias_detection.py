#!/usr/bin/env python3

import psycopg2
import json
from typing import Dict, List, Any, Tuple
from collections import defaultdict
import statistics

class EdinburghBiasDetector:
    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.conn = None
    
    def connect(self):
        """Connect to PostgreSQL database"""
        self.conn = psycopg2.connect(**self.db_config)
        return self.conn.cursor()
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def analyze_representation_bias(self) -> Dict[str, Any]:
        """
        Analyze bias in document representation across different dimensions.
        Checks for imbalances in department, campus, document type, etc.
        """
        cursor = self.connect()
        
        # Analyze department representation
        cursor.execute("""
            SELECT 
                metadata->>'department' as department,
                COUNT(*) as doc_count,
                AVG(LENGTH(content)) as avg_length,
                COUNT(DISTINCT metadata->>'author') as unique_authors
            FROM docs 
            WHERE metadata->>'department' IS NOT NULL 
            GROUP BY metadata->>'department'
            ORDER BY doc_count DESC;
        """)
        dept_stats = cursor.fetchall()
        
        # Analyze campus representation
        cursor.execute("""
            SELECT 
                metadata->>'campus' as campus,
                COUNT(*) as doc_count,
                AVG(LENGTH(content)) as avg_length
            FROM docs 
            WHERE metadata->>'campus' IS NOT NULL 
            GROUP BY metadata->>'campus'
            ORDER BY doc_count DESC;
        """)
        campus_stats = cursor.fetchall()
        
        # Analyze document type representation
        cursor.execute("""
            SELECT 
                metadata->>'type' as doc_type,
                COUNT(*) as doc_count,
                AVG(LENGTH(content)) as avg_length
            FROM docs 
            WHERE metadata->>'type' IS NOT NULL 
            GROUP BY metadata->>'type'
            ORDER BY doc_count DESC;
        """)
        type_stats = cursor.fetchall()
        
        # Calculate bias metrics
        dept_counts = [stat[1] for stat in dept_stats]
        campus_counts = [stat[1] for stat in campus_stats]
        type_counts = [stat[1] for stat in type_stats]
        
        # Calculate imbalance ratios (max/min)
        dept_imbalance = max(dept_counts) / min(dept_counts) if dept_counts else 1
        campus_imbalance = max(campus_counts) / min(campus_counts) if campus_counts else 1
        type_imbalance = max(type_counts) / min(type_counts) if type_counts else 1
        
        self.close()
        
        return {
            'department_analysis': {
                'stats': dept_stats,
                'imbalance_ratio': dept_imbalance,
                'bias_level': 'HIGH' if dept_imbalance > 3 else 'MEDIUM' if dept_imbalance > 2 else 'LOW'
            },
            'campus_analysis': {
                'stats': campus_stats,
                'imbalance_ratio': campus_imbalance,
                'bias_level': 'HIGH' if campus_imbalance > 3 else 'MEDIUM' if campus_imbalance > 2 else 'LOW'
            },
            'document_type_analysis': {
                'stats': type_stats,
                'imbalance_ratio': type_imbalance,
                'bias_level': 'HIGH' if type_imbalance > 3 else 'MEDIUM' if type_imbalance > 2 else 'LOW'
            },
            'recommendations': self._generate_representation_recommendations(
                dept_imbalance, campus_imbalance, type_imbalance
            )
        }
    
    def analyze_search_result_bias(self, test_queries: List[str]) -> Dict[str, Any]:
        """
        Analyze potential bias in search results by testing with different user profiles.
        Tests how results vary based on user context.
        """
        cursor = self.connect()
        bias_analysis = defaultdict(list)
        
        # Test user profiles representing different Edinburgh contexts
        test_profiles = [
            {'role': 'student', 'campus': 'Kings Buildings', 'department': 'Computer Science'},
            {'role': 'staff', 'campus': 'Central Area', 'department': 'Administration'},
            {'role': 'researcher', 'campus': 'Kings Buildings', 'department': 'Physics'},
            {'role': 'lecturer', 'campus': 'Central Area', 'department': 'Literature'}
        ]
        
        for query in test_queries:
            query_results = {}
            
            for profile in test_profiles:
                # Simulate context-aware search
                cursor.execute("""
                    SELECT 
                        content,
                        metadata,
                        1 - (embedding <=> %s::vector) as similarity,
                        CASE 
                            WHEN metadata->>'department' = %s THEN 0.1
                            WHEN metadata->>'campus' = %s THEN 0.05
                            ELSE 0
                        END as context_boost
                    FROM docs 
                    WHERE 1 - (embedding <=> %s::vector) > 0.7
                    ORDER BY (1 - (embedding <=> %s::vector)) + 
                        CASE 
                            WHEN metadata->>'department' = %s THEN 0.1
                            WHEN metadata->>'campus' = %s THEN 0.05
                            ELSE 0
                        END DESC
                    LIMIT 10;
                """, [
                    self._get_query_embedding(query),
                    profile['department'], profile['campus'],
                    self._get_query_embedding(query),
                    self._get_query_embedding(query),
                    profile['department'], profile['campus']
                ])
                
                results = cursor.fetchall()
                
                # Analyze result diversity
                dept_diversity = len(set(r[1].get('department', 'Unknown') for r in results))
                campus_diversity = len(set(r[1].get('campus', 'Unknown') for r in results))
                type_diversity = len(set(r[1].get('type', 'Unknown') for r in results))
                
                query_results[f"{profile['role']}_{profile['department']}"] = {
                    'result_count': len(results),
                    'dept_diversity': dept_diversity,
                    'campus_diversity': campus_diversity,
                    'type_diversity': type_diversity,
                    'avg_similarity': statistics.mean([r[2] for r in results]) if results else 0
                }
            
            bias_analysis[query] = query_results
        
        self.close()
        
        # Calculate bias metrics across profiles
        bias_scores = self._calculate_result_bias_scores(bias_analysis)
        
        return {
            'query_analysis': dict(bias_analysis),
            'bias_scores': bias_scores,
            'overall_bias_level': self._assess_overall_bias_level(bias_scores),
            'recommendations': self._generate_search_bias_recommendations(bias_scores)
        }
    
    def _get_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for query (simplified - would use actual embedding service)"""
        # In real implementation, this would call Ollama API
        # For demo purposes, return a placeholder vector
        return [0.1] * 1024
    
    def _calculate_result_bias_scores(self, analysis: Dict) -> Dict[str, float]:
        """Calculate bias scores across different metrics"""
        diversity_scores = []
        similarity_variance = []
        
        for query_data in analysis.values():
            dept_diversities = [data['dept_diversity'] for data in query_data.values()]
            campus_diversities = [data['campus_diversity'] for data in query_data.values()]
            similarities = [data['avg_similarity'] for data in query_data.values()]
            
            diversity_scores.append(statistics.stdev(dept_diversities) if len(dept_diversities) > 1 else 0)
            diversity_scores.append(statistics.stdev(campus_diversities) if len(campus_diversities) > 1 else 0)
            similarity_variance.append(statistics.stdev(similarities) if len(similarities) > 1 else 0)
        
        return {
            'diversity_bias_score': statistics.mean(diversity_scores) if diversity_scores else 0,
            'similarity_variance_score': statistics.mean(similarity_variance) if similarity_variance else 0,
            'result_consistency_score': 1 - (statistics.mean(similarity_variance) if similarity_variance else 0)
        }
    
    def _assess_overall_bias_level(self, bias_scores: Dict[str, float]) -> str:
        """Assess overall bias level based on calculated scores"""
        avg_bias = statistics.mean(bias_scores.values())
        
        if avg_bias > 0.3:
            return 'HIGH'
        elif avg_bias > 0.15:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _generate_representation_recommendations(self, dept_imbalance: float, 
                                                campus_imbalance: float, 
                                                type_imbalance: float) -> List[str]:
        """Generate recommendations based on representation analysis"""
        recommendations = []
        
        if dept_imbalance > 3:
            recommendations.append("HIGH PRIORITY: Address severe department representation imbalance")
            recommendations.append("Action: Actively collect documents from underrepresented departments")
        
        if campus_imbalance > 3:
            recommendations.append("MEDIUM PRIORITY: Balance content across Edinburgh campuses")
            recommendations.append("Action: Ensure equal representation from all university campuses")
        
        if type_imbalance > 3:
            recommendations.append("LOW PRIORITY: Diversify document types in collection")
            recommendations.append("Action: Include more varied content types (policies, research, guides)")
        
        recommendations.append("Implement regular bias auditing with these metrics")
        recommendations.append("Set up automated alerts when imbalance ratios exceed thresholds")
        
        return recommendations
    
    def _generate_search_bias_recommendations(self, bias_scores: Dict[str, float]) -> List[str]:
        """Generate recommendations for search result bias"""
        recommendations = []
        
        if bias_scores['diversity_bias_score'] > 0.2:
            recommendations.append("Implement result diversification algorithms")
            recommendations.append("Add explicit diversity metrics to ranking functions")
        
        if bias_scores['similarity_variance_score'] > 0.15:
            recommendations.append("Review context-based boosting mechanisms")
            recommendations.append("Ensure consistent result quality across user profiles")
        
        recommendations.append("Regular A/B testing with different user profiles")
        recommendations.append("Implement fairness constraints in search algorithms")
        recommendations.append("Monitor result diversity metrics in production")
        
        return recommendations
    
    def generate_bias_report(self) -> Dict[str, Any]:
        """Generate comprehensive bias report for Edinburgh University"""
        
        print("🔍 Analyzing representation bias...")
        representation_analysis = self.analyze_representation_bias()
        
        print("🔍 Analyzing search result bias...")
        test_queries = [
            "student accommodation",
            "research funding opportunities",
            "course enrollment procedures",
            "campus facilities booking",
            "library resources access"
        ]
        search_bias_analysis = self.analyze_search_result_bias(test_queries)
        
        # Generate overall assessment
        overall_bias_level = self._assess_combined_bias_level(
            representation_analysis, search_bias_analysis
        )
        
        report = {
            'report_metadata': {
                'generated_for': 'Edinburgh University AI Ethics Committee',
                'report_date': '2024-01-15',
                'analysis_scope': 'Document representation and search result fairness'
            },
            'representation_bias': representation_analysis,
            'search_result_bias': search_bias_analysis,
            'overall_assessment': {
                'bias_level': overall_bias_level,
                'priority_actions': self._generate_priority_actions(
                    representation_analysis, search_bias_analysis
                ),
                'compliance_status': self._assess_compliance_status(overall_bias_level)
            },
            'next_steps': {
                'immediate_actions': [
                    "Present findings to AI Ethics Committee",
                    "Implement high-priority bias mitigation measures",
                    "Set up automated bias monitoring"
                ],
                'ongoing_monitoring': [
                    "Monthly bias assessment reports",
                    "Quarterly review of mitigation effectiveness",
                    "Annual comprehensive bias audit"
                ]
            }
        }
        
        return report
    
    def _assess_combined_bias_level(self, rep_analysis: Dict, search_analysis: Dict) -> str:
        """Assess overall bias level combining both analyses"""
        rep_high = any(
            analysis['bias_level'] == 'HIGH' 
            for analysis in [
                rep_analysis['department_analysis'],
                rep_analysis['campus_analysis'],
                rep_analysis['document_type_analysis']
            ]
        )
        
        search_high = search_analysis['overall_bias_level'] == 'HIGH'
        
        if rep_high or search_high:
            return 'HIGH'
        elif rep_analysis.get('overall_bias_level') == 'MEDIUM' or search_analysis['overall_bias_level'] == 'MEDIUM':
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _generate_priority_actions(self, rep_analysis: Dict, search_analysis: Dict) -> List[str]:
        """Generate priority actions based on combined analysis"""
        actions = []
        
        # High priority representation issues
        for analysis_type, analysis in rep_analysis.items():
            if isinstance(analysis, dict) and analysis.get('bias_level') == 'HIGH':
                actions.append(f"URGENT: Address {analysis_type.replace('_', ' ')} bias")
        
        # High priority search issues
        if search_analysis['overall_bias_level'] == 'HIGH':
            actions.append("URGENT: Implement search result fairness measures")
        
        # Always include these foundational actions
        actions.extend([
            "Establish regular bias monitoring procedures",
            "Train staff on bias detection and mitigation",
            "Create bias incident reporting system"
        ])
        
        return actions
    
    def _assess_compliance_status(self, bias_level: str) -> Dict[str, str]:
        """Assess compliance with various frameworks"""
        return {
            'eu_ai_act': 'COMPLIANT' if bias_level == 'LOW' else 'NEEDS_ATTENTION',
            'gdpr': 'COMPLIANT' if bias_level != 'HIGH' else 'NON_COMPLIANT',
            'edinburgh_policy': 'COMPLIANT' if bias_level == 'LOW' else 'REVIEW_REQUIRED',
            'ethical_guidelines': 'MEETS_STANDARDS' if bias_level != 'HIGH' else 'BELOW_STANDARDS'
        }

if __name__ == "__main__":
    # Example usage
    db_config = {
        'host': 'localhost',
        'port': 5050,
        'database': 'pgvector',
        'user': 'postgres',
        'password': 'postgres'
    }
    
    detector = EdinburghBiasDetector(db_config)
    
    print("🎯 Edinburgh University AI Bias Detection Report")
    print("=" * 50)
    
    bias_report = detector.generate_bias_report()
    
    print(f"\n📊 Overall Bias Level: {bias_report['overall_assessment']['bias_level']}")
    print("\n🚨 Priority Actions:")
    for action in bias_report['overall_assessment']['priority_actions']:
        print(f"  • {action}")
    
    print("\n✅ Compliance Status:")
    for framework, status in bias_report['overall_assessment']['compliance_status'].items():
        print(f"  • {framework.upper()}: {status}")
    
    print("\n📋 Next Steps:")
    print("Immediate:")
    for step in bias_report['next_steps']['immediate_actions']:
        print(f"  • {step}")
    
    print("Ongoing:")
    for step in bias_report['next_steps']['ongoing_monitoring']:
        print(f"  • {step}")
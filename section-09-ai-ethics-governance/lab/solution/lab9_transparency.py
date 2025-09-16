#!/usr/bin/env python3

import psycopg2
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib

class ExplainableSearchResult:
    """Individual search result with explainability features"""
    
    def __init__(self, content: str, metadata: Dict[str, Any], 
                 similarity: float, ranking_factors: Dict[str, float]):
        self.content = content
        self.metadata = metadata
        self.similarity = similarity
        self.ranking_factors = ranking_factors
        self.combined_score = sum(ranking_factors.values())
        self.explanation_id = self._generate_explanation_id()
    
    def _generate_explanation_id(self) -> str:
        """Generate unique ID for this explanation"""
        content_hash = hashlib.md5(self.content.encode()).hexdigest()[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"exp_{timestamp}_{content_hash}"
    
    def explain_relevance(self, user_query: str = "") -> str:
        """Generate user-friendly explanation of why this result is relevant"""
        
        explanations = []
        
        # Vector similarity explanation
        if self.similarity > 0.9:
            explanations.append("🎯 **Highly relevant**: This document closely matches your search terms")
        elif self.similarity > 0.8:
            explanations.append("✅ **Good match**: This document is well-related to your query")
        elif self.similarity > 0.7:
            explanations.append("📋 **Relevant**: This document contains related information")
        else:
            explanations.append("📝 **Potentially useful**: This document may have relevant context")
        
        # Metadata-based explanations
        if self.metadata.get('department'):
            explanations.append(f"📍 From {self.metadata['department']} department")
        
        if self.metadata.get('campus'):
            explanations.append(f"🏛️ Located at {self.metadata['campus']} campus")
        
        if self.metadata.get('type'):
            doc_type = self.metadata['type']
            type_descriptions = {
                'policy': '📜 Official university policy document',
                'guide': '📚 Helpful guidance document',
                'procedure': '⚙️ Step-by-step procedure',
                'faq': '❓ Frequently asked questions',
                'form': '📋 Official university form',
                'research': '🔬 Research publication',
                'news': '📰 University news or announcement'
            }
            explanations.append(type_descriptions.get(doc_type.lower(), f"📄 {doc_type} document"))
        
        if self.metadata.get('last_updated'):
            explanations.append(f"🗓️ Updated: {self.metadata['last_updated']}")
        
        return "\n".join(explanations)
    
    def explain_ranking(self, position: int = None) -> str:
        """Explain how this result's ranking was determined"""
        
        ranking_explanation = []
        
        if position:
            ranking_explanation.append(f"📊 **Ranked #{position}** based on combined relevance score of {self.combined_score:.3f}")
        
        ranking_explanation.append("\n**Ranking factors:**")
        
        # Break down ranking factors
        for factor, score in sorted(self.ranking_factors.items(), key=lambda x: x[1], reverse=True):
            percentage = (score / self.combined_score * 100) if self.combined_score > 0 else 0
            
            factor_explanations = {
                'vector_similarity': f'🎯 Content similarity: {percentage:.1f}% (score: {score:.3f})',
                'department_match': f'🏢 Department relevance: {percentage:.1f}% (score: {score:.3f})',
                'campus_preference': f'📍 Campus preference: {percentage:.1f}% (score: {score:.3f})',
                'document_type_boost': f'📄 Document type boost: {percentage:.1f}% (score: {score:.3f})',
                'recency_boost': f'🗓️ Recency boost: {percentage:.1f}% (score: {score:.3f})',
                'authority_score': f'⭐ Authority score: {percentage:.1f}% (score: {score:.3f})',
                'user_context_match': f'👤 Personal relevance: {percentage:.1f}% (score: {score:.3f})'
            }
            
            ranking_explanation.append(f"  • {factor_explanations.get(factor, f'{factor}: {percentage:.1f}% (score: {score:.3f})')}")
        
        return "\n".join(ranking_explanation)
    
    def get_transparency_data(self) -> Dict[str, Any]:
        """Return structured transparency data for logging/auditing"""
        return {
            'explanation_id': self.explanation_id,
            'timestamp': datetime.now().isoformat(),
            'result_metadata': {
                'similarity_score': self.similarity,
                'combined_score': self.combined_score,
                'ranking_factors': self.ranking_factors,
                'document_metadata': self.metadata
            },
            'transparency_level': self._assess_transparency_level(),
            'explainability_features': {
                'has_similarity_explanation': True,
                'has_ranking_breakdown': True,
                'has_metadata_context': bool(self.metadata),
                'has_factor_weights': len(self.ranking_factors) > 1
            }
        }
    
    def _assess_transparency_level(self) -> str:
        """Assess how transparent this result explanation is"""
        features = 0
        
        if self.similarity > 0:
            features += 1
        if self.ranking_factors:
            features += 1
        if self.metadata:
            features += 1
        if len(self.ranking_factors) > 2:
            features += 1
        
        if features >= 4:
            return 'HIGH'
        elif features >= 2:
            return 'MEDIUM'
        else:
            return 'LOW'

class EdinburghTransparencySystem:
    """System for providing transparency in AI-powered search and recommendations"""
    
    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.conn = None
        self.explanation_log = []
    
    def connect(self):
        """Connect to PostgreSQL database"""
        self.conn = psycopg2.connect(**self.db_config)
        return self.conn.cursor()
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def transparent_search(self, query: str, user_context: Dict[str, Any] = None, 
                          limit: int = 5) -> List[ExplainableSearchResult]:
        """
        Perform search with full transparency and explainability.
        Returns results with detailed explanations of ranking.
        """
        cursor = self.connect()
        
        # Get query embedding (simplified for demo)
        query_embedding = self._get_query_embedding(query)
        
        # Build context-aware query
        context_conditions = []
        context_boosts = []
        
        if user_context:
            if user_context.get('department'):
                context_boosts.append(f"CASE WHEN metadata->>'department' = '{user_context['department']}' THEN 0.1 ELSE 0 END")
            if user_context.get('campus'):
                context_boosts.append(f"CASE WHEN metadata->>'campus' = '{user_context['campus']}' THEN 0.05 ELSE 0 END")
            if user_context.get('role'):
                # Role-based document type preferences
                role_prefs = {
                    'student': ['guide', 'faq', 'procedure'],
                    'staff': ['policy', 'procedure', 'form'],
                    'researcher': ['research', 'policy', 'guide']
                }
                if user_context['role'] in role_prefs:
                    pref_types = "', '".join(role_prefs[user_context['role']])
                    context_boosts.append(f"CASE WHEN metadata->>'type' IN ('{pref_types}') THEN 0.08 ELSE 0 END")
        
        # Calculate recency boost (prefer more recent documents)
        context_boosts.append("""
            CASE 
                WHEN metadata->>'last_updated' IS NOT NULL AND 
                     (metadata->>'last_updated')::date > CURRENT_DATE - INTERVAL '30 days' THEN 0.05
                WHEN metadata->>'last_updated' IS NOT NULL AND 
                     (metadata->>'last_updated')::date > CURRENT_DATE - INTERVAL '90 days' THEN 0.03
                ELSE 0 
            END
        """)
        
        # Authority boost (prefer official documents)
        context_boosts.append("""
            CASE 
                WHEN metadata->>'authority' = 'high' THEN 0.06
                WHEN metadata->>'authority' = 'medium' THEN 0.03
                ELSE 0 
            END
        """)
        
        boost_sql = " + ".join(context_boosts) if context_boosts else "0"
        
        # Execute transparent search query
        cursor.execute(f"""
            SELECT 
                content,
                metadata,
                1 - (embedding <=> %s::vector) as similarity,
                {boost_sql} as context_boost,
                (1 - (embedding <=> %s::vector)) + ({boost_sql}) as total_score
            FROM docs 
            WHERE 1 - (embedding <=> %s::vector) > 0.6
            ORDER BY total_score DESC
            LIMIT %s;
        """, [query_embedding, query_embedding, query_embedding, limit])
        
        results = cursor.fetchall()
        self.close()
        
        # Convert to explainable results
        explainable_results = []
        
        for i, (content, metadata, similarity, context_boost, total_score) in enumerate(results):
            # Calculate detailed ranking factors
            ranking_factors = self._calculate_ranking_factors(
                similarity, context_boost, metadata, user_context or {}
            )
            
            explainable_result = ExplainableSearchResult(
                content=content,
                metadata=metadata,
                similarity=similarity,
                ranking_factors=ranking_factors
            )
            
            # Log transparency data
            transparency_data = explainable_result.get_transparency_data()
            transparency_data['query'] = query
            transparency_data['user_context'] = user_context
            transparency_data['result_position'] = i + 1
            
            self.explanation_log.append(transparency_data)
            explainable_results.append(explainable_result)
        
        return explainable_results
    
    def _calculate_ranking_factors(self, similarity: float, context_boost: float, 
                                   metadata: Dict, user_context: Dict) -> Dict[str, float]:
        """Break down ranking score into interpretable factors"""
        factors = {
            'vector_similarity': similarity
        }
        
        # Break down context boost into specific factors
        if user_context.get('department') and metadata.get('department') == user_context['department']:
            factors['department_match'] = 0.1
        
        if user_context.get('campus') and metadata.get('campus') == user_context['campus']:
            factors['campus_preference'] = 0.05
        
        # Document type boost
        if user_context.get('role'):
            role_prefs = {
                'student': ['guide', 'faq', 'procedure'],
                'staff': ['policy', 'procedure', 'form'],
                'researcher': ['research', 'policy', 'guide']
            }
            if (user_context['role'] in role_prefs and 
                metadata.get('type') in role_prefs[user_context['role']]):
                factors['document_type_boost'] = 0.08
        
        # Recency boost
        if metadata.get('last_updated'):
            # Simplified recency calculation
            factors['recency_boost'] = 0.05 if 'recent' in str(metadata.get('last_updated', '')) else 0.03
        
        # Authority boost
        authority_map = {'high': 0.06, 'medium': 0.03, 'low': 0}
        factors['authority_score'] = authority_map.get(metadata.get('authority', 'low'), 0)
        
        return factors
    
    def _get_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for query (simplified for demo)"""
        # In real implementation, this would call Ollama API
        return [0.1] * 1024
    
    def generate_search_explanation_report(self, query: str, results: List[ExplainableSearchResult]) -> str:
        """Generate comprehensive explanation report for a search"""
        
        report = []
        report.append(f"🔍 **Search Explanation Report**")
        report.append(f"Query: \"{query}\"")
        report.append(f"Results returned: {len(results)}")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        for i, result in enumerate(results, 1):
            report.append(f"## Result #{i}")
            report.append(f"**Content preview**: {result.content[:100]}...")
            report.append("")
            
            # Relevance explanation
            report.append("### Why this result was selected:")
            report.append(result.explain_relevance(query))
            report.append("")
            
            # Ranking explanation
            report.append("### How this result was ranked:")
            report.append(result.explain_ranking(i))
            report.append("")
            
            # Transparency metadata
            transparency = result.get_transparency_data()
            report.append(f"**Transparency Level**: {transparency['transparency_level']}")
            report.append(f"**Explanation ID**: {transparency['explanation_id']}")
            report.append("")
            report.append("---")
            report.append("")
        
        return "\n".join(report)
    
    def create_transparency_dashboard_data(self) -> Dict[str, Any]:
        """Generate data for transparency dashboard"""
        
        if not self.explanation_log:
            return {'message': 'No search data available'}
        
        # Analyze transparency metrics
        transparency_levels = [log['result_metadata']['transparency_level'] for log in self.explanation_log]
        transparency_counts = {level: transparency_levels.count(level) for level in set(transparency_levels)}
        
        # Average scores
        avg_similarity = sum(log['result_metadata']['similarity_score'] for log in self.explanation_log) / len(self.explanation_log)
        avg_combined_score = sum(log['result_metadata']['combined_score'] for log in self.explanation_log) / len(self.explanation_log)
        
        # Factor usage statistics
        factor_usage = {}
        for log in self.explanation_log:
            for factor in log['result_metadata']['ranking_factors']:
                factor_usage[factor] = factor_usage.get(factor, 0) + 1
        
        dashboard_data = {
            'summary_stats': {
                'total_searches_logged': len(set(log['query'] for log in self.explanation_log)),
                'total_results_explained': len(self.explanation_log),
                'average_similarity_score': round(avg_similarity, 3),
                'average_combined_score': round(avg_combined_score, 3)
            },
            'transparency_distribution': transparency_counts,
            'ranking_factor_usage': factor_usage,
            'recent_searches': [
                {
                    'query': log['query'],
                    'timestamp': log['timestamp'],
                    'transparency_level': log['result_metadata']['transparency_level'],
                    'explanation_id': log['explanation_id']
                }
                for log in self.explanation_log[-10:]  # Last 10 searches
            ],
            'compliance_metrics': {
                'explainability_coverage': len([log for log in self.explanation_log if log['transparency_level'] in ['HIGH', 'MEDIUM']]) / len(self.explanation_log) * 100,
                'factor_breakdown_available': len([log for log in self.explanation_log if len(log['result_metadata']['ranking_factors']) > 1]) / len(self.explanation_log) * 100
            }
        }
        
        return dashboard_data
    
    def export_transparency_audit_log(self, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """Export transparency logs for audit purposes"""
        
        audit_log = []
        
        for log_entry in self.explanation_log:
            # Filter by date if specified
            if start_date or end_date:
                entry_date = datetime.fromisoformat(log_entry['timestamp']).date()
                if start_date and entry_date < datetime.fromisoformat(start_date).date():
                    continue
                if end_date and entry_date > datetime.fromisoformat(end_date).date():
                    continue
            
            audit_entry = {
                'audit_id': f"audit_{log_entry['explanation_id']}",
                'timestamp': log_entry['timestamp'],
                'query_hash': hashlib.md5(log_entry['query'].encode()).hexdigest(),  # Anonymized
                'transparency_level': log_entry['result_metadata']['transparency_level'],
                'explainability_features': log_entry['explainability_features'],
                'compliance_check': {
                    'has_similarity_score': log_entry['result_metadata']['similarity_score'] > 0,
                    'has_ranking_breakdown': len(log_entry['result_metadata']['ranking_factors']) > 1,
                    'transparency_adequate': log_entry['result_metadata']['transparency_level'] in ['HIGH', 'MEDIUM']
                }
            }
            
            audit_log.append(audit_entry)
        
        return audit_log

if __name__ == "__main__":
    # Example usage
    db_config = {
        'host': 'localhost',
        'port': 5050,
        'database': 'pgvector',
        'user': 'postgres',
        'password': 'postgres'
    }
    
    transparency_system = EdinburghTransparencySystem(db_config)
    
    print("🔍 Edinburgh University AI Transparency System")
    print("=" * 50)
    
    # Example search with user context
    user_context = {
        'department': 'Computer Science',
        'campus': 'Kings Buildings',
        'role': 'student'
    }
    
    query = "student accommodation booking"
    results = transparency_system.transparent_search(query, user_context, limit=3)
    
    print(f"\n📊 Search Results for: '{query}'")
    print(f"User Context: {user_context}")
    print("-" * 40)
    
    for i, result in enumerate(results, 1):
        print(f"\n**Result #{i}**")
        print(f"Similarity Score: {result.similarity:.3f}")
        print(f"Combined Score: {result.combined_score:.3f}")
        print(f"Transparency Level: {result._assess_transparency_level()}")
        
        print(f"\n{result.explain_relevance(query)}")
        print(f"\n{result.explain_ranking(i)}")
        print("-" * 30)
    
    # Generate explanation report
    print("\n📋 Generating Explanation Report...")
    explanation_report = transparency_system.generate_search_explanation_report(query, results)
    
    # Dashboard data
    print("\n📈 Transparency Dashboard Data:")
    dashboard_data = transparency_system.create_transparency_dashboard_data()
    print(f"Total Results Explained: {dashboard_data['summary_stats']['total_results_explained']}")
    print(f"Explainability Coverage: {dashboard_data['compliance_metrics']['explainability_coverage']:.1f}%")
    
    transparency_system.close()
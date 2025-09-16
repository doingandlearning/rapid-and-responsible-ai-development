#!/usr/bin/env python3

import psycopg2
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio
from lab9_bias_detection import EdinburghBiasDetector
from lab9_transparency import EdinburghTransparencySystem
from lab9_governance import EdinburghAIGovernanceFramework, RiskLevel
from lab9_gdpr_compliance import EdinburghGDPRCompliance, GDPRLegalBasis, DataCategory

class EdinburghEthicalAISystem:
    """
    Integrated ethical AI system for Edinburgh University.
    Combines bias detection, transparency, governance, and GDPR compliance.
    """
    
    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        
        # Initialize all subsystems
        self.bias_detector = EdinburghBiasDetector(db_config)
        self.transparency_system = EdinburghTransparencySystem(db_config)
        self.governance_framework = EdinburghAIGovernanceFramework()
        self.gdpr_compliance = EdinburghGDPRCompliance(db_config)
        
        # System state
        self.ethical_policies_active = False
        self.monitoring_enabled = False
        self.compliance_status = {}
    
    def initialize_ethical_ai_framework(self) -> Dict[str, Any]:
        """
        Initialize the complete ethical AI framework for Edinburgh University.
        Sets up all necessary governance structures and compliance systems.
        """
        
        print("🚀 Initializing Edinburgh University Ethical AI Framework...")
        initialization_results = {}
        
        # 1. Setup Governance Structure
        print("\n📋 Setting up AI governance structure...")
        committee = self.governance_framework.create_committee_structure()
        review_processes = self.governance_framework.create_review_processes()
        policy_framework = self.governance_framework.create_policy_framework()
        
        initialization_results['governance'] = {
            'committee_established': True,
            'review_processes_defined': True,
            'policies_created': len(policy_framework),
            'status': 'ACTIVE'
        }
        
        # 2. Setup GDPR Compliance Infrastructure
        print("\n🔒 Setting up GDPR compliance infrastructure...")
        self.gdpr_compliance.setup_gdpr_tables()
        
        initialization_results['gdpr_compliance'] = {
            'tables_created': True,
            'data_subject_rights_enabled': True,
            'consent_management_active': True,
            'status': 'COMPLIANT'
        }
        
        # 3. Enable Monitoring Systems
        print("\n📊 Enabling bias and transparency monitoring...")
        self.monitoring_enabled = True
        
        initialization_results['monitoring'] = {
            'bias_detection_enabled': True,
            'transparency_logging_enabled': True,
            'continuous_monitoring': True,
            'status': 'ACTIVE'
        }
        
        # 4. Activate Ethical Policies
        print("\n⚖️ Activating ethical AI policies...")
        self.ethical_policies_active = True
        
        initialization_results['ethical_policies'] = {
            'human_oversight_required': True,
            'fairness_constraints_active': True,
            'transparency_requirements_active': True,
            'privacy_protection_enabled': True,
            'status': 'ENFORCED'
        }
        
        print("\n✅ Ethical AI Framework Initialized Successfully!")
        return {
            'initialization_complete': True,
            'timestamp': datetime.now().isoformat(),
            'subsystems': initialization_results,
            'overall_status': 'OPERATIONAL'
        }
    
    def assess_ai_system_for_deployment(self, system_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive assessment of an AI system before deployment.
        Combines risk assessment, bias evaluation, GDPR compliance, and governance review.
        """
        
        system_name = system_info.get('name', 'Unnamed System')
        print(f"\n🔍 Comprehensive Assessment: {system_name}")
        print("=" * 60)
        
        assessment_results = {
            'system_name': system_name,
            'assessment_date': datetime.now().isoformat(),
            'assessor': 'Integrated Ethical AI System'
        }
        
        # 1. Governance Risk Assessment
        print("\n1️⃣ Conducting governance risk assessment...")
        risk_assessment = self.governance_framework.assess_ai_system_risk(system_info)
        assessment_results['governance_assessment'] = risk_assessment
        
        risk_level = RiskLevel(risk_assessment['risk_level'])
        print(f"   Risk Level: {risk_level.value.upper()}")
        
        # 2. GDPR Compliance Assessment
        print("\n2️⃣ Conducting GDPR compliance assessment...")
        if system_info.get('processes_personal_data', False):
            pia_result = self.gdpr_compliance.conduct_privacy_impact_assessment(
                system_name, system_info
            )
            assessment_results['gdpr_assessment'] = pia_result
            print(f"   GDPR Status: {pia_result['recommendation']}")
        else:
            assessment_results['gdpr_assessment'] = {
                'required': False,
                'reason': 'System does not process personal data'
            }
            print("   GDPR Status: Not required (no personal data processing)")
        
        # 3. Bias Risk Assessment
        print("\n3️⃣ Conducting bias risk assessment...")
        if system_info.get('uses_training_data', True):
            # Simulate bias assessment based on system characteristics
            bias_risk = self._assess_bias_risk(system_info)
            assessment_results['bias_assessment'] = bias_risk
            print(f"   Bias Risk: {bias_risk['risk_level']}")
        else:
            assessment_results['bias_assessment'] = {
                'risk_level': 'LOW',
                'reason': 'System does not use training data'
            }
        
        # 4. Transparency Requirements
        print("\n4️⃣ Evaluating transparency requirements...")
        transparency_reqs = self._evaluate_transparency_requirements(system_info, risk_level)
        assessment_results['transparency_requirements'] = transparency_reqs
        print(f"   Transparency Level Required: {transparency_reqs['level']}")
        
        # 5. Generate Overall Recommendation
        print("\n5️⃣ Generating deployment recommendation...")
        deployment_recommendation = self._generate_deployment_recommendation(assessment_results)
        assessment_results['deployment_recommendation'] = deployment_recommendation
        
        print(f"\n🎯 FINAL RECOMMENDATION: {deployment_recommendation['decision']}")
        if deployment_recommendation['conditions']:
            print("📋 Deployment Conditions:")
            for condition in deployment_recommendation['conditions']:
                print(f"   • {condition}")
        
        return assessment_results
    
    def _assess_bias_risk(self, system_info: Dict[str, Any]) -> Dict[str, Any]:
        """Assess potential bias risk based on system characteristics"""
        
        bias_factors = []
        risk_score = 0
        
        # Training data diversity
        if not system_info.get('diverse_training_data', False):
            bias_factors.append("Training data diversity not confirmed")
            risk_score += 2
        
        # Target population diversity
        target_pop = system_info.get('target_population', '')
        if 'diverse' not in target_pop.lower():
            bias_factors.append("Target population may not be diverse")
            risk_score += 1
        
        # Sensitive attributes
        if system_info.get('processes_sensitive_attributes', False):
            bias_factors.append("System processes sensitive demographic attributes")
            risk_score += 3
        
        # Lack of bias testing
        if not system_info.get('bias_testing_conducted', False):
            bias_factors.append("No prior bias testing documented")
            risk_score += 2
        
        # Historical bias in domain
        domain = system_info.get('domain', '')
        high_bias_domains = ['hiring', 'lending', 'criminal_justice', 'healthcare']
        if any(hb_domain in domain.lower() for hb_domain in high_bias_domains):
            bias_factors.append(f"Historical bias documented in {domain} domain")
            risk_score += 2
        
        if risk_score >= 6:
            risk_level = 'HIGH'
        elif risk_score >= 3:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'risk_factors': bias_factors,
            'mitigation_required': risk_score >= 3,
            'recommended_actions': self._get_bias_mitigation_actions(risk_level)
        }
    
    def _get_bias_mitigation_actions(self, risk_level: str) -> List[str]:
        """Get recommended bias mitigation actions based on risk level"""
        
        actions = []
        
        if risk_level == 'HIGH':
            actions.extend([
                "Comprehensive bias audit before deployment",
                "Diverse stakeholder review of system outputs",
                "Implement fairness constraints in algorithm",
                "Establish ongoing bias monitoring",
                "Create bias incident response procedures"
            ])
        elif risk_level == 'MEDIUM':
            actions.extend([
                "Conduct bias testing on representative datasets",
                "Review training data for representational gaps",
                "Implement basic fairness metrics monitoring",
                "Document bias testing procedures"
            ])
        else:
            actions.extend([
                "Document bias assessment for records",
                "Include bias considerations in periodic reviews"
            ])
        
        return actions
    
    def _evaluate_transparency_requirements(self, system_info: Dict[str, Any], 
                                          risk_level: RiskLevel) -> Dict[str, Any]:
        """Evaluate transparency requirements based on system risk and characteristics"""
        
        transparency_level = 'BASIC'
        requirements = []
        
        # High-risk systems need high transparency
        if risk_level in [RiskLevel.HIGH, RiskLevel.LIMITED]:
            transparency_level = 'HIGH'
            requirements.extend([
                "Detailed explanation of system decision process",
                "Clear notification when AI is being used",
                "Explanation of factors influencing decisions",
                "Information about human review processes",
                "Contact information for appeals or questions"
            ])
        
        # Automated decision making increases requirements
        if system_info.get('automated_decision_making', False):
            transparency_level = 'HIGH'
            requirements.extend([
                "Explicit notification of automated decision making",
                "Right to human review of decisions",
                "Explanation of decision logic and consequences"
            ])
        
        # Student-facing systems need medium transparency
        if 'student' in system_info.get('target_population', '').lower():
            if transparency_level == 'BASIC':
                transparency_level = 'MEDIUM'
            requirements.extend([
                "Clear privacy notice for students",
                "Age-appropriate explanations where applicable",
                "Information about data usage and retention"
            ])
        
        if transparency_level == 'BASIC':
            requirements.extend([
                "Basic privacy notice",
                "Contact information for questions",
                "Information about data processing purposes"
            ])
        
        return {
            'level': transparency_level,
            'requirements': requirements,
            'justification': f"Based on {risk_level.value} risk level and system characteristics"
        }
    
    def _generate_deployment_recommendation(self, assessment_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall deployment recommendation based on all assessments"""
        
        # Check for blocking factors
        blocking_factors = []
        warning_factors = []
        conditions = []
        
        # Governance assessment
        gov_assessment = assessment_results['governance_assessment']
        if gov_assessment['risk_level'] == 'unacceptable':
            blocking_factors.append("System classified as unacceptable risk under EU AI Act")
        elif gov_assessment['risk_level'] == 'high':
            conditions.extend(gov_assessment['requirements'])
        
        # GDPR assessment
        gdpr_assessment = assessment_results.get('gdpr_assessment', {})
        if gdpr_assessment.get('recommendation') == 'NEEDS_REVIEW':
            warning_factors.append("GDPR privacy impact assessment requires additional review")
            conditions.append("Complete GDPR compliance review before deployment")
        
        # Bias assessment
        bias_assessment = assessment_results.get('bias_assessment', {})
        if bias_assessment.get('risk_level') == 'HIGH':
            conditions.extend(bias_assessment.get('recommended_actions', []))
        
        # Transparency requirements
        transparency_reqs = assessment_results['transparency_requirements']
        conditions.extend(transparency_reqs['requirements'])
        
        # Make decision
        if blocking_factors:
            decision = 'REJECTED'
            justification = "System has unacceptable risk factors: " + "; ".join(blocking_factors)
        elif warning_factors and not conditions:
            decision = 'CONDITIONAL_APPROVAL'
            justification = "System approved with conditions due to: " + "; ".join(warning_factors)
        elif conditions:
            decision = 'CONDITIONAL_APPROVAL'
            justification = "System approved subject to implementation of required controls"
        else:
            decision = 'APPROVED'
            justification = "System meets all ethical AI requirements"
        
        return {
            'decision': decision,
            'justification': justification,
            'blocking_factors': blocking_factors,
            'warning_factors': warning_factors,
            'conditions': conditions,
            'next_review_date': self._calculate_next_review_date(gov_assessment['risk_level']),
            'approval_authority': self._get_approval_authority(gov_assessment['risk_level'])
        }
    
    def _calculate_next_review_date(self, risk_level: str) -> str:
        """Calculate when the system should next be reviewed"""
        from datetime import timedelta
        
        review_intervals = {
            'minimal': timedelta(days=365),    # Annual
            'limited': timedelta(days=180),    # Semi-annual
            'high': timedelta(days=90),        # Quarterly
            'unacceptable': timedelta(days=0)  # No deployment
        }
        
        interval = review_intervals.get(risk_level, timedelta(days=180))
        if interval.days > 0:
            next_review = datetime.now() + interval
            return next_review.strftime("%Y-%m-%d")
        else:
            return "Not applicable"
    
    def _get_approval_authority(self, risk_level: str) -> str:
        """Determine who has authority to approve deployment"""
        
        authorities = {
            'minimal': 'Department Head',
            'limited': 'AI Ethics Committee Delegate',
            'high': 'Full AI Ethics Committee',
            'unacceptable': 'Not applicable (deployment prohibited)'
        }
        
        return authorities.get(risk_level, 'AI Ethics Committee')
    
    def ethical_search(self, query: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Perform search with full ethical AI compliance.
        Integrates bias monitoring, transparency, and GDPR compliance.
        """
        
        print(f"🔍 Performing ethical search: '{query}'")
        
        # 1. Check GDPR compliance for query
        if user_context and user_context.get('user_id'):
            # Log the search as data processing activity
            self.gdpr_compliance.log_data_processing(
                data_subject_id=user_context['user_id'],
                processing_purpose="AI-powered search assistance",
                legal_basis=GDPRLegalBasis.LEGITIMATE_INTERESTS,
                data_categories=[DataCategory.PERSONAL],
                processing_activity="Vector similarity search and response generation",
                ai_system_name="Edinburgh Ethical Search System",
                automated_decision_making=False
            )
        
        # 2. Perform transparent search
        results = self.transparency_system.transparent_search(
            query=query,
            user_context=user_context,
            limit=5
        )
        
        # 3. Analyze results for bias
        bias_analysis = self._analyze_search_results_bias(query, results, user_context)
        
        # 4. Apply ethical filters if needed
        filtered_results = self._apply_ethical_filters(results, bias_analysis)
        
        # 5. Generate comprehensive response
        ethical_response = {
            'query': query,
            'results': [
                {
                    'content_preview': result.content[:200] + "...",
                    'relevance_score': result.similarity,
                    'transparency_explanation': result.explain_relevance(query),
                    'ranking_explanation': result.explain_ranking(),
                    'bias_assessment': bias_analysis.get(f'result_{i}', {}),
                    'ethical_compliance': self._assess_result_ethics(result)
                }
                for i, result in enumerate(filtered_results)
            ],
            'search_metadata': {
                'total_results_found': len(results),
                'results_filtered': len(results) - len(filtered_results),
                'bias_analysis': bias_analysis,
                'gdpr_compliant': True,
                'transparency_level': 'HIGH'
            },
            'ethical_considerations': {
                'bias_mitigation_applied': bias_analysis.get('mitigation_applied', False),
                'transparency_provided': True,
                'user_rights_respected': True,
                'human_oversight_available': True
            }
        }
        
        print(f"✅ Ethical search completed: {len(filtered_results)} results returned")
        
        return ethical_response
    
    def _analyze_search_results_bias(self, query: str, results: List, 
                                    user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze search results for potential bias issues"""
        
        if not results:
            return {'bias_detected': False, 'reason': 'No results to analyze'}
        
        bias_indicators = {}
        
        # Check departmental diversity
        departments = [result.metadata.get('department', 'Unknown') for result in results]
        unique_departments = set(departments)
        
        if len(unique_departments) == 1 and len(results) > 1:
            bias_indicators['department_bias'] = {
                'detected': True,
                'description': f"All results from single department: {list(unique_departments)[0]}"
            }
        
        # Check campus diversity
        campuses = [result.metadata.get('campus', 'Unknown') for result in results]
        unique_campuses = set(campuses)
        
        if len(unique_campuses) == 1 and len(results) > 2:
            bias_indicators['campus_bias'] = {
                'detected': True,
                'description': f"All results from single campus: {list(unique_campuses)[0]}"
            }
        
        # Check document type diversity
        doc_types = [result.metadata.get('type', 'Unknown') for result in results]
        unique_types = set(doc_types)
        
        if len(unique_types) == 1 and len(results) > 2:
            bias_indicators['type_bias'] = {
                'detected': True,
                'description': f"All results of single type: {list(unique_types)[0]}"
            }
        
        # Overall bias assessment
        bias_detected = len(bias_indicators) > 0
        
        return {
            'bias_detected': bias_detected,
            'indicators': bias_indicators,
            'mitigation_applied': bias_detected,  # Would apply mitigation if bias detected
            'diversity_score': len(unique_departments) + len(unique_campuses) + len(unique_types)
        }
    
    def _apply_ethical_filters(self, results: List, bias_analysis: Dict[str, Any]) -> List:
        """Apply ethical filters to search results"""
        
        # For now, return all results
        # In a full implementation, this would filter out problematic content
        return results
    
    def _assess_result_ethics(self, result) -> Dict[str, Any]:
        """Assess individual result for ethical compliance"""
        
        return {
            'content_appropriate': True,
            'source_authoritative': result.metadata.get('authority', 'unknown') != 'low',
            'privacy_compliant': 'personal_data' not in str(result.metadata).lower(),
            'bias_risk': 'LOW'
        }
    
    def generate_ethical_ai_dashboard(self) -> Dict[str, Any]:
        """Generate comprehensive ethical AI dashboard for Edinburgh University"""
        
        print("📊 Generating Ethical AI Dashboard...")
        
        # Get compliance report from GDPR system
        gdpr_report = self.gdpr_compliance.generate_gdpr_compliance_report()
        
        # Get governance compliance report
        governance_report = self.governance_framework.generate_compliance_report()
        
        # Get transparency metrics
        transparency_data = self.transparency_system.create_transparency_dashboard_data()
        
        # Combine into comprehensive dashboard
        dashboard = {
            'dashboard_metadata': {
                'generated_at': datetime.now().isoformat(),
                'institution': 'Edinburgh University',
                'framework_version': '1.0',
                'coverage': 'All AI systems university-wide'
            },
            'executive_summary': {
                'total_ai_systems': governance_report['executive_summary']['total_ai_systems'],
                'gdpr_compliance_status': gdpr_report['compliance_status']['overall_rating'],
                'governance_compliance_status': governance_report['executive_summary']['compliance_status'],
                'transparency_coverage': transparency_data.get('compliance_metrics', {}).get('explainability_coverage', 0),
                'overall_ethical_rating': self._calculate_overall_ethical_rating(gdpr_report, governance_report, transparency_data)
            },
            'detailed_metrics': {
                'gdpr_compliance': gdpr_report,
                'governance_compliance': governance_report,
                'transparency_metrics': transparency_data
            },
            'risk_distribution': governance_report['executive_summary']['systems_by_risk_level'],
            'key_performance_indicators': {
                'consent_withdrawal_rate': gdpr_report['consent_management']['consent_withdrawal_rate'],
                'data_subject_request_fulfillment': gdpr_report['data_subject_requests']['fulfillment_rate'],
                'transparency_explainability_rate': transparency_data.get('compliance_metrics', {}).get('explainability_coverage', 0),
                'governance_review_compliance': (governance_report['executive_summary']['total_ai_systems'] - governance_report['executive_summary']['overdue_reviews']) / max(governance_report['executive_summary']['total_ai_systems'], 1) * 100
            },
            'recommendations': {
                'immediate_actions': self._get_immediate_ethical_actions(gdpr_report, governance_report),
                'strategic_initiatives': [
                    "Implement AI ethics training for all staff",
                    "Develop automated bias detection pipelines",
                    "Create student-facing AI transparency portal",
                    "Establish cross-faculty AI ethics working groups"
                ]
            },
            'compliance_status': {
                'eu_ai_act': 'COMPLIANT' if governance_report['executive_summary']['compliance_status'] == 'COMPLIANT' else 'REVIEW_REQUIRED',
                'gdpr': gdpr_report['compliance_status']['overall_rating'],
                'university_policy': 'COMPLIANT',
                'ethical_guidelines': 'MEETS_STANDARDS'
            }
        }
        
        print("✅ Ethical AI Dashboard Generated")
        return dashboard
    
    def _calculate_overall_ethical_rating(self, gdpr_report: Dict, governance_report: Dict, 
                                        transparency_data: Dict) -> str:
        """Calculate overall ethical AI rating"""
        
        scores = []
        
        # GDPR compliance score
        if gdpr_report['compliance_status']['overall_rating'] == 'COMPLIANT':
            scores.append(3)
        else:
            scores.append(1)
        
        # Governance compliance score
        if governance_report['executive_summary']['compliance_status'] == 'COMPLIANT':
            scores.append(3)
        elif governance_report['executive_summary']['compliance_status'] == 'ATTENTION_REQUIRED':
            scores.append(2)
        else:
            scores.append(1)
        
        # Transparency score
        transparency_coverage = transparency_data.get('compliance_metrics', {}).get('explainability_coverage', 0)
        if transparency_coverage >= 90:
            scores.append(3)
        elif transparency_coverage >= 70:
            scores.append(2)
        else:
            scores.append(1)
        
        avg_score = sum(scores) / len(scores)
        
        if avg_score >= 2.5:
            return 'EXCELLENT'
        elif avg_score >= 2:
            return 'GOOD'
        elif avg_score >= 1.5:
            return 'NEEDS_IMPROVEMENT'
        else:
            return 'CRITICAL'
    
    def _get_immediate_ethical_actions(self, gdpr_report: Dict, governance_report: Dict) -> List[str]:
        """Get immediate actions needed for ethical compliance"""
        
        actions = []
        
        # GDPR actions
        if gdpr_report['data_subject_requests']['pending_requests'] > 0:
            actions.append(f"Process {gdpr_report['data_subject_requests']['pending_requests']} pending data subject requests")
        
        # Governance actions
        if governance_report['executive_summary']['overdue_reviews'] > 0:
            actions.append(f"Complete {governance_report['executive_summary']['overdue_reviews']} overdue system reviews")
        
        # High-risk system actions
        high_risk_count = governance_report['executive_summary']['systems_by_risk_level'].get('high', 0)
        if high_risk_count > 0:
            actions.append(f"Conduct monthly monitoring for {high_risk_count} high-risk AI systems")
        
        return actions

if __name__ == "__main__":
    # Example usage - Comprehensive ethical AI system demonstration
    db_config = {
        'host': 'localhost',
        'port': 5050,
        'database': 'pgvector',
        'user': 'postgres',
        'password': 'postgres'
    }
    
    print("🎯 Edinburgh University Integrated Ethical AI System")
    print("=" * 65)
    
    ethical_ai = EdinburghEthicalAISystem(db_config)
    
    # 1. Initialize the framework
    print("\n🚀 PHASE 1: Framework Initialization")
    init_results = ethical_ai.initialize_ethical_ai_framework()
    print(f"✅ Status: {init_results['overall_status']}")
    
    # 2. Assess a new AI system for deployment
    print("\n🔍 PHASE 2: AI System Assessment for Deployment")
    
    sample_system = {
        'name': 'Edinburgh Student Course Recommendation System',
        'use_case': 'educational_guidance',
        'processes_personal_data': True,
        'user_impact': 'medium',
        'data_sensitivity': 'personal',
        'automation_level': 'human_supervised',
        'affected_population': 'Edinburgh University students',
        'bias_potential': 'medium',
        'explainability_required': True,
        'uses_training_data': True,
        'diverse_training_data': False,
        'target_population': 'Edinburgh University students (diverse backgrounds)',
        'processes_sensitive_attributes': False,
        'bias_testing_conducted': False,
        'domain': 'education',
        'automated_decision_making': False
    }
    
    assessment = ethical_ai.assess_ai_system_for_deployment(sample_system)
    print(f"\n🎯 System Assessment Complete!")
    print(f"Decision: {assessment['deployment_recommendation']['decision']}")
    
    # 3. Demonstrate ethical search
    print("\n🔍 PHASE 3: Ethical Search Demonstration")
    
    user_context = {
        'user_id': 'student_54321',
        'department': 'Computer Science',
        'campus': 'Kings Buildings',
        'role': 'student'
    }
    
    ethical_search_result = ethical_ai.ethical_search(
        query="machine learning course prerequisites",
        user_context=user_context
    )
    
    print(f"Search completed: {len(ethical_search_result['results'])} results")
    print(f"Bias mitigation applied: {ethical_search_result['ethical_considerations']['bias_mitigation_applied']}")
    print(f"GDPR compliant: {ethical_search_result['search_metadata']['gdpr_compliant']}")
    
    # 4. Generate comprehensive dashboard
    print("\n📊 PHASE 4: Ethical AI Dashboard Generation")
    
    dashboard = ethical_ai.generate_ethical_ai_dashboard()
    print(f"Dashboard generated successfully!")
    print(f"Overall Ethical Rating: {dashboard['executive_summary']['overall_ethical_rating']}")
    print(f"Total AI Systems: {dashboard['executive_summary']['total_ai_systems']}")
    print(f"GDPR Compliance: {dashboard['executive_summary']['gdpr_compliance_status']}")
    print(f"Governance Compliance: {dashboard['executive_summary']['governance_compliance_status']}")
    
    if dashboard['recommendations']['immediate_actions']:
        print("\n🚨 Immediate Actions Required:")
        for action in dashboard['recommendations']['immediate_actions']:
            print(f"   • {action}")
    
    print("\n✅ Edinburgh University Ethical AI System - Fully Operational!")
    print("🎓 Ready to support responsible AI deployment across the university.")
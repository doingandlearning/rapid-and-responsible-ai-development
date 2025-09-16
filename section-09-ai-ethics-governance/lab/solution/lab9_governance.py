#!/usr/bin/env python3

import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import uuid

class RiskLevel(Enum):
    UNACCEPTABLE = "unacceptable"
    HIGH = "high"
    LIMITED = "limited"
    MINIMAL = "minimal"

class AISystemType(Enum):
    SEARCH_SYSTEM = "search_system"
    RECOMMENDATION_ENGINE = "recommendation_engine"
    CHATBOT = "chatbot"
    CLASSIFICATION_SYSTEM = "classification_system"
    DECISION_SUPPORT = "decision_support"

class EdinburghAIGovernanceFramework:
    """
    AI Governance Framework specifically designed for Edinburgh University.
    Implements EU AI Act compliance and university-specific requirements.
    """
    
    def __init__(self):
        self.committee_structure = None
        self.policies = {}
        self.risk_assessments = {}
        self.review_processes = {}
        self.compliance_tracking = {}
        self.audit_log = []
    
    def create_committee_structure(self) -> Dict[str, Any]:
        """
        Create AI Ethics Committee structure for Edinburgh University.
        Ensures diverse representation across faculties and roles.
        """
        
        committee_structure = {
            'ai_ethics_committee': {
                'chair': {
                    'role': 'Vice-Principal for Research and Innovation',
                    'responsibilities': [
                        'Strategic oversight of AI governance',
                        'Final decision authority on high-risk AI systems',
                        'Liaison with university executive'
                    ]
                },
                'members': [
                    {
                        'role': 'Faculty Representative - Science & Engineering',
                        'department': 'Computer Science',
                        'expertise': ['Technical AI systems', 'Machine learning ethics']
                    },
                    {
                        'role': 'Faculty Representative - Humanities & Social Sciences',
                        'department': 'Philosophy',
                        'expertise': ['Ethics', 'Philosophy of technology']
                    },
                    {
                        'role': 'Legal Counsel',
                        'department': 'Legal Services',
                        'expertise': ['GDPR', 'EU AI Act', 'Higher education law']
                    },
                    {
                        'role': 'Data Protection Officer',
                        'department': 'Information Services',
                        'expertise': ['Data protection', 'Privacy compliance']
                    },
                    {
                        'role': 'Student Representative',
                        'department': 'Student Union',
                        'expertise': ['Student advocacy', 'Digital rights']
                    },
                    {
                        'role': 'Professional Services Representative',
                        'department': 'Human Resources',
                        'expertise': ['Staff welfare', 'Employment practices']
                    },
                    {
                        'role': 'External Expert',
                        'department': 'External',
                        'expertise': ['AI ethics', 'Regulatory compliance']
                    }
                ],
                'meeting_schedule': {
                    'frequency': 'Monthly',
                    'additional_meetings': 'As required for urgent reviews',
                    'quorum': 'Minimum 5 members including chair or deputy'
                },
                'reporting': {
                    'reports_to': 'University Executive Committee',
                    'frequency': 'Quarterly',
                    'annual_report': 'Required'
                }
            },
            'technical_review_panel': {
                'purpose': 'Technical assessment of AI systems',
                'members': [
                    {'role': 'Senior AI Researcher', 'expertise': 'Technical evaluation'},
                    {'role': 'IT Security Specialist', 'expertise': 'Security assessment'},
                    {'role': 'Data Analyst', 'expertise': 'Data quality and bias'},
                    {'role': 'Software Architect', 'expertise': 'System integration'}
                ],
                'responsibilities': [
                    'Technical risk assessment',
                    'Code review for AI systems',
                    'Performance and bias testing',
                    'Security and privacy evaluation'
                ]
            },
            'ai_champions_network': {
                'purpose': 'Distributed AI governance support across university',
                'structure': {
                    'school_champions': 'One per school/faculty',
                    'support_service_champions': 'Key professional services',
                    'student_digital_advocates': 'Student-facing services'
                },
                'responsibilities': [
                    'Local AI governance implementation',
                    'Training and awareness',
                    'Issue identification and escalation',
                    'Best practice sharing'
                ]
            }
        }
        
        self.committee_structure = committee_structure
        
        # Log committee creation
        self._log_governance_action(
            action_type='committee_creation',
            description='AI Ethics Committee structure established',
            details=committee_structure
        )
        
        return committee_structure
    
    def create_review_processes(self) -> Dict[str, Any]:
        """
        Create structured review processes for different AI system risk levels.
        Aligned with EU AI Act requirements.
        """
        
        review_processes = {
            'pre_deployment_review': {
                'minimal_risk_systems': {
                    'process': 'Self-assessment',
                    'requirements': [
                        'Complete AI system registration form',
                        'Confirm minimal risk categorization',
                        'Document intended use and limitations'
                    ],
                    'timeline': '5 business days',
                    'approval_authority': 'Department head'
                },
                'limited_risk_systems': {
                    'process': 'Technical review panel assessment',
                    'requirements': [
                        'Detailed system specification',
                        'Risk assessment documentation',
                        'User impact analysis',
                        'Transparency measures implementation',
                        'Data protection impact assessment'
                    ],
                    'timeline': '10 business days',
                    'approval_authority': 'AI Ethics Committee delegate'
                },
                'high_risk_systems': {
                    'process': 'Full AI Ethics Committee review',
                    'requirements': [
                        'Comprehensive risk assessment',
                        'Bias testing and mitigation plan',
                        'Human oversight procedures',
                        'Monitoring and logging systems',
                        'User rights and redress mechanisms',
                        'Legal and regulatory compliance review',
                        'External validation (if required)'
                    ],
                    'timeline': '20 business days',
                    'approval_authority': 'AI Ethics Committee'
                },
                'unacceptable_risk_systems': {
                    'process': 'Prohibited - no deployment allowed',
                    'action': 'Immediate rejection with explanation',
                    'timeline': '2 business days for rejection notification'
                }
            },
            'ongoing_monitoring': {
                'minimal_risk': {
                    'frequency': 'Annual review',
                    'metrics': ['Usage patterns', 'User feedback'],
                    'reporting': 'Annual compliance report'
                },
                'limited_risk': {
                    'frequency': 'Quarterly monitoring',
                    'metrics': [
                        'Performance metrics',
                        'User feedback analysis',
                        'Incident reports',
                        'Compliance status'
                    ],
                    'reporting': 'Quarterly monitoring report'
                },
                'high_risk': {
                    'frequency': 'Monthly monitoring',
                    'metrics': [
                        'Bias testing results',
                        'Human oversight effectiveness',
                        'User complaints and resolutions',
                        'Performance degradation',
                        'Security incidents',
                        'Regulatory compliance status'
                    ],
                    'reporting': 'Monthly detailed report + immediate incident reporting'
                }
            },
            'incident_response': {
                'classification': {
                    'low_severity': 'Minor performance issues or user complaints',
                    'medium_severity': 'System bias detected or privacy concerns',
                    'high_severity': 'Discriminatory outcomes or regulatory violations',
                    'critical_severity': 'Serious harm to individuals or legal violations'
                },
                'response_times': {
                    'low_severity': '5 business days',
                    'medium_severity': '48 hours',
                    'high_severity': '24 hours',
                    'critical_severity': '4 hours'
                },
                'escalation_procedures': {
                    'low_severity': 'Department level resolution',
                    'medium_severity': 'Technical review panel involvement',
                    'high_severity': 'AI Ethics Committee notification',
                    'critical_severity': 'Immediate system suspension + committee emergency session'
                }
            }
        }
        
        self.review_processes = review_processes
        
        # Log process creation
        self._log_governance_action(
            action_type='process_creation',
            description='Review processes established for all risk levels',
            details=review_processes
        )
        
        return review_processes
    
    def assess_ai_system_risk(self, system_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess risk level of an AI system according to EU AI Act categories.
        Returns detailed risk assessment with justification.
        """
        
        system_id = str(uuid.uuid4())
        assessment_date = datetime.now().isoformat()
        
        # Extract key system characteristics
        use_case = system_info.get('use_case', '')
        user_impact = system_info.get('user_impact', 'low')
        data_sensitivity = system_info.get('data_sensitivity', 'public')
        automation_level = system_info.get('automation_level', 'human_supervised')
        affected_population = system_info.get('affected_population', 'internal')
        
        # Risk assessment logic based on EU AI Act
        risk_factors = self._evaluate_risk_factors(system_info)
        risk_level = self._determine_risk_level(risk_factors)
        
        assessment = {
            'assessment_id': system_id,
            'system_name': system_info.get('name', 'Unnamed System'),
            'assessment_date': assessment_date,
            'risk_level': risk_level.value,
            'risk_factors': risk_factors,
            'justification': self._generate_risk_justification(risk_factors, risk_level),
            'requirements': self._get_requirements_for_risk_level(risk_level),
            'next_review_date': self._calculate_next_review_date(risk_level),
            'assessor': system_info.get('assessor', 'System'),
            'compliance_requirements': self._get_compliance_requirements(risk_level)
        }
        
        # Store assessment
        self.risk_assessments[system_id] = assessment
        
        # Log assessment
        self._log_governance_action(
            action_type='risk_assessment',
            description=f'Risk assessment completed for {assessment["system_name"]}',
            details={'assessment_id': system_id, 'risk_level': risk_level.value}
        )
        
        return assessment
    
    def _evaluate_risk_factors(self, system_info: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate individual risk factors for the system"""
        
        risk_factors = {}
        
        # Use case risk evaluation
        high_risk_use_cases = [
            'recruitment', 'hiring', 'employment_decisions',
            'credit_scoring', 'loan_approval',
            'law_enforcement', 'border_control',
            'educational_assessment', 'student_evaluation',
            'healthcare_diagnosis', 'medical_decisions'
        ]
        
        use_case = system_info.get('use_case', '').lower()
        risk_factors['use_case_risk'] = 'high' if any(risk_case in use_case for risk_case in high_risk_use_cases) else 'medium' if 'decision' in use_case else 'low'
        
        # Data sensitivity evaluation
        data_sensitivity = system_info.get('data_sensitivity', 'public')
        sensitivity_map = {
            'public': 'low',
            'internal': 'medium',
            'confidential': 'high',
            'personal': 'high',
            'sensitive_personal': 'very_high'
        }
        risk_factors['data_sensitivity_risk'] = sensitivity_map.get(data_sensitivity, 'medium')
        
        # Automation level evaluation
        automation_level = system_info.get('automation_level', 'human_supervised')
        automation_risk_map = {
            'human_controlled': 'low',
            'human_supervised': 'medium',
            'human_oversight': 'high',
            'fully_automated': 'very_high'
        }
        risk_factors['automation_risk'] = automation_risk_map.get(automation_level, 'medium')
        
        # Population impact evaluation
        affected_population = system_info.get('affected_population', 'internal')
        population_risk_map = {
            'internal_small': 'low',
            'internal': 'medium',
            'students': 'high',
            'public': 'high',
            'vulnerable_groups': 'very_high'
        }
        risk_factors['population_impact_risk'] = population_risk_map.get(affected_population, 'medium')
        
        # Bias potential evaluation
        bias_potential = system_info.get('bias_potential', 'low')
        risk_factors['bias_risk'] = bias_potential
        
        # Transparency requirements
        explainability = system_info.get('explainability_required', True)
        risk_factors['transparency_risk'] = 'low' if explainability else 'high'
        
        return risk_factors
    
    def _determine_risk_level(self, risk_factors: Dict[str, Any]) -> RiskLevel:
        """Determine overall risk level based on individual risk factors"""
        
        # Convert risk levels to numeric scores
        risk_score_map = {'low': 1, 'medium': 2, 'high': 3, 'very_high': 4}
        
        total_score = 0
        max_score = 0
        
        for factor, level in risk_factors.items():
            score = risk_score_map.get(level, 2)
            total_score += score
            max_score = max(max_score, score)
        
        avg_score = total_score / len(risk_factors) if risk_factors else 1
        
        # Risk level determination logic
        if max_score >= 4 or avg_score >= 3.5:
            return RiskLevel.HIGH
        elif max_score >= 3 or avg_score >= 2.5:
            return RiskLevel.LIMITED
        elif avg_score >= 1.5:
            return RiskLevel.MINIMAL
        else:
            return RiskLevel.MINIMAL
    
    def _generate_risk_justification(self, risk_factors: Dict[str, Any], risk_level: RiskLevel) -> str:
        """Generate human-readable justification for risk level"""
        
        high_risk_factors = [factor for factor, level in risk_factors.items() if level in ['high', 'very_high']]
        medium_risk_factors = [factor for factor, level in risk_factors.items() if level == 'medium']
        
        justification = f"System classified as {risk_level.value.upper()} risk based on:\n"
        
        if high_risk_factors:
            justification += f"\nHigh risk factors identified:\n"
            for factor in high_risk_factors:
                justification += f"- {factor.replace('_', ' ').title()}: {risk_factors[factor]}\n"
        
        if medium_risk_factors:
            justification += f"\nMedium risk factors:\n"
            for factor in medium_risk_factors:
                justification += f"- {factor.replace('_', ' ').title()}: {risk_factors[factor]}\n"
        
        # Add specific guidance
        if risk_level == RiskLevel.HIGH:
            justification += "\nThis system requires comprehensive oversight, bias testing, and human supervision."
        elif risk_level == RiskLevel.LIMITED:
            justification += "\nThis system requires transparency measures and regular monitoring."
        else:
            justification += "\nThis system requires basic documentation and annual review."
        
        return justification
    
    def _get_requirements_for_risk_level(self, risk_level: RiskLevel) -> List[str]:
        """Get specific requirements based on risk level"""
        
        requirements = {
            RiskLevel.MINIMAL: [
                'System registration and documentation',
                'Annual compliance review',
                'Basic user feedback collection'
            ],
            RiskLevel.LIMITED: [
                'Transparency notices for users',
                'Clear system limitations documentation',
                'Quarterly performance monitoring',
                'User complaint handling process',
                'Data protection compliance verification'
            ],
            RiskLevel.HIGH: [
                'Comprehensive bias testing before deployment',
                'Human oversight and review mechanisms',
                'Detailed logging and monitoring systems',
                'Regular performance and fairness audits',
                'User rights notification and redress procedures',
                'Data protection impact assessment',
                'Conformity assessment and CE marking (if applicable)',
                'Risk management system implementation'
            ],
            RiskLevel.UNACCEPTABLE: [
                'System deployment prohibited',
                'Alternative approaches required'
            ]
        }
        
        return requirements.get(risk_level, [])
    
    def _calculate_next_review_date(self, risk_level: RiskLevel) -> str:
        """Calculate next review date based on risk level"""
        
        review_intervals = {
            RiskLevel.MINIMAL: timedelta(days=365),  # Annual
            RiskLevel.LIMITED: timedelta(days=90),   # Quarterly
            RiskLevel.HIGH: timedelta(days=30),      # Monthly
            RiskLevel.UNACCEPTABLE: timedelta(days=0) # No review needed
        }
        
        interval = review_intervals.get(risk_level, timedelta(days=90))
        next_review = datetime.now() + interval
        
        return next_review.isoformat()
    
    def _get_compliance_requirements(self, risk_level: RiskLevel) -> List[str]:
        """Get compliance requirements for each risk level"""
        
        compliance = {
            RiskLevel.MINIMAL: ['GDPR', 'University AI Policy'],
            RiskLevel.LIMITED: ['GDPR', 'EU AI Act (Limited Risk)', 'University AI Policy', 'Transparency Requirements'],
            RiskLevel.HIGH: ['GDPR', 'EU AI Act (High Risk)', 'University AI Policy', 'Conformity Assessment', 'Risk Management'],
            RiskLevel.UNACCEPTABLE: ['Prohibited under EU AI Act']
        }
        
        return compliance.get(risk_level, [])
    
    def create_policy_framework(self) -> Dict[str, Any]:
        """
        Create comprehensive AI policy framework for Edinburgh University.
        Covers all aspects of responsible AI use.
        """
        
        policy_framework = {
            'ai_acceptable_use_policy': {
                'scope': 'All university staff, students, and affiliates',
                'principles': [
                    'Human-centric AI: AI systems must augment, not replace human judgment',
                    'Fairness and non-discrimination: AI must not perpetuate or create unfair bias',
                    'Transparency: Users must understand when and how AI is being used',
                    'Privacy and data protection: AI use must respect individual privacy rights',
                    'Accountability: Clear responsibility for AI system decisions and outcomes',
                    'Sustainability: Consider environmental impact of AI systems'
                ],
                'permitted_uses': [
                    'Research and academic activities',
                    'Administrative process improvement',
                    'Student support and guidance',
                    'Educational content creation and delivery',
                    'Accessibility enhancement'
                ],
                'prohibited_uses': [
                    'Surveillance of individuals without consent',
                    'Automated decision-making affecting fundamental rights',
                    'Plagiarism or academic dishonesty',
                    'Discrimination or bias amplification',
                    'Privacy violations'
                ],
                'approval_requirements': {
                    'minimal_risk': 'Department approval',
                    'limited_risk': 'Technical review panel',
                    'high_risk': 'AI Ethics Committee',
                    'unacceptable_risk': 'Prohibited'
                }
            },
            'data_governance_for_ai': {
                'data_collection': [
                    'Explicit consent required for personal data',
                    'Data minimization principle applies',
                    'Purpose limitation must be specified',
                    'Regular data quality assessments'
                ],
                'data_processing': [
                    'Lawful basis under GDPR required',
                    'Bias detection and mitigation measures',
                    'Data anonymization where possible',
                    'Retention period limits enforced'
                ],
                'data_sharing': [
                    'Internal sharing requires data sharing agreement',
                    'External sharing requires ethics committee approval',
                    'Cross-border transfers must comply with adequacy decisions',
                    'Commercial data sharing prohibited without explicit consent'
                ]
            },
            'human_oversight_requirements': {
                'high_risk_systems': [
                    'Qualified human operator must supervise system',
                    'Human can override system decisions',
                    'Meaningful human review of system outputs',
                    'Clear escalation procedures for human intervention'
                ],
                'limited_risk_systems': [
                    'Human review of system performance',
                    'Regular human validation of outputs',
                    'Clear process for human override'
                ],
                'training_requirements': [
                    'AI system operators must receive appropriate training',
                    'Regular competency assessments',
                    'Understanding of system limitations and biases'
                ]
            },
            'procurement_guidelines': {
                'vendor_assessment': [
                    'AI ethics and governance practices',
                    'Bias testing and mitigation capabilities',
                    'Data protection and privacy measures',
                    'Transparency and explainability features',
                    'Environmental sustainability practices'
                ],
                'contractual_requirements': [
                    'Right to audit AI system performance',
                    'Bias testing reports and remediation',
                    'Data processing agreements compliant with GDPR',
                    'Liability and indemnification clauses',
                    'Service level agreements for fairness metrics'
                ]
            }
        }
        
        self.policies = policy_framework
        
        # Log policy creation
        self._log_governance_action(
            action_type='policy_creation',
            description='Comprehensive AI policy framework established',
            details={'policies_created': len(policy_framework)}
        )
        
        return policy_framework
    
    def _log_governance_action(self, action_type: str, description: str, details: Dict[str, Any]):
        """Log governance actions for audit trail"""
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action_type': action_type,
            'description': description,
            'details': details,
            'log_id': str(uuid.uuid4())
        }
        
        self.audit_log.append(log_entry)
    
    def generate_compliance_report(self) -> Dict[str, Any]:
        """Generate comprehensive compliance report for regulators and management"""
        
        report_date = datetime.now().isoformat()
        
        # Analyze current systems and compliance status
        total_systems = len(self.risk_assessments)
        risk_distribution = {}
        overdue_reviews = []
        
        for assessment in self.risk_assessments.values():
            risk_level = assessment['risk_level']
            risk_distribution[risk_level] = risk_distribution.get(risk_level, 0) + 1
            
            # Check for overdue reviews
            next_review = datetime.fromisoformat(assessment['next_review_date'])
            if next_review < datetime.now():
                overdue_reviews.append(assessment)
        
        compliance_report = {
            'report_metadata': {
                'report_date': report_date,
                'reporting_period': 'Current status as of report date',
                'prepared_by': 'Edinburgh University AI Governance Framework',
                'report_type': 'Compliance Status Report'
            },
            'executive_summary': {
                'total_ai_systems': total_systems,
                'systems_by_risk_level': risk_distribution,
                'overdue_reviews': len(overdue_reviews),
                'compliance_status': 'COMPLIANT' if len(overdue_reviews) == 0 else 'ATTENTION_REQUIRED'
            },
            'governance_structure': {
                'committee_established': self.committee_structure is not None,
                'policies_in_place': len(self.policies),
                'review_processes_defined': len(self.review_processes)
            },
            'risk_management': {
                'systems_assessed': total_systems,
                'high_risk_systems': risk_distribution.get('high', 0),
                'limited_risk_systems': risk_distribution.get('limited', 0),
                'minimal_risk_systems': risk_distribution.get('minimal', 0)
            },
            'compliance_issues': {
                'overdue_reviews': [
                    {
                        'system_name': assessment['system_name'],
                        'risk_level': assessment['risk_level'],
                        'days_overdue': (datetime.now() - datetime.fromisoformat(assessment['next_review_date'])).days
                    }
                    for assessment in overdue_reviews
                ],
                'remediation_required': len(overdue_reviews) > 0
            },
            'recommendations': self._generate_compliance_recommendations(risk_distribution, overdue_reviews),
            'audit_trail': {
                'total_logged_actions': len(self.audit_log),
                'recent_actions': self.audit_log[-10:] if len(self.audit_log) >= 10 else self.audit_log
            }
        }
        
        return compliance_report
    
    def _generate_compliance_recommendations(self, risk_distribution: Dict, overdue_reviews: List) -> List[str]:
        """Generate recommendations based on current compliance status"""
        
        recommendations = []
        
        if overdue_reviews:
            recommendations.append(f"URGENT: Complete {len(overdue_reviews)} overdue system reviews")
        
        high_risk_count = risk_distribution.get('high', 0)
        if high_risk_count > 0:
            recommendations.append(f"Monitor {high_risk_count} high-risk systems monthly")
        
        total_systems = sum(risk_distribution.values())
        if total_systems == 0:
            recommendations.append("Begin AI system inventory and risk assessments")
        
        recommendations.extend([
            "Conduct quarterly compliance review meetings",
            "Update staff training on AI governance requirements",
            "Review and update policies based on regulatory changes",
            "Implement automated compliance monitoring where possible"
        ])
        
        return recommendations

if __name__ == "__main__":
    # Example usage
    print("🏛️ Edinburgh University AI Governance Framework")
    print("=" * 55)
    
    governance = EdinburghAIGovernanceFramework()
    
    # 1. Create committee structure
    print("\n📋 1. Creating AI Ethics Committee Structure...")
    committee = governance.create_committee_structure()
    print(f"✅ Committee established with {len(committee['ai_ethics_committee']['members'])} members")
    
    # 2. Create review processes
    print("\n⚙️ 2. Establishing Review Processes...")
    processes = governance.create_review_processes()
    print("✅ Review processes defined for all risk levels")
    
    # 3. Assess a sample AI system
    print("\n🔍 3. Assessing Sample AI System...")
    sample_system = {
        'name': 'Student Support Chatbot',
        'use_case': 'student_support_decision_assistance',
        'user_impact': 'high',
        'data_sensitivity': 'personal',
        'automation_level': 'human_supervised',
        'affected_population': 'students',
        'bias_potential': 'medium',
        'explainability_required': True,
        'assessor': 'Technical Review Panel'
    }
    
    assessment = governance.assess_ai_system_risk(sample_system)
    print(f"✅ Risk Assessment Complete:")
    print(f"   System: {assessment['system_name']}")
    print(f"   Risk Level: {assessment['risk_level'].upper()}")
    print(f"   Next Review: {assessment['next_review_date'][:10]}")
    
    # 4. Create policy framework
    print("\n📜 4. Creating Policy Framework...")
    policies = governance.create_policy_framework()
    print(f"✅ Policy framework created with {len(policies)} policy areas")
    
    # 5. Generate compliance report
    print("\n📊 5. Generating Compliance Report...")
    compliance_report = governance.generate_compliance_report()
    print("✅ Compliance Report Generated:")
    print(f"   Total AI Systems: {compliance_report['executive_summary']['total_ai_systems']}")
    print(f"   Compliance Status: {compliance_report['executive_summary']['compliance_status']}")
    print(f"   Overdue Reviews: {compliance_report['executive_summary']['overdue_reviews']}")
    
    print("\n🎯 Governance Framework Implementation Complete!")
    print("Ready for Edinburgh University AI Ethics Committee review.")
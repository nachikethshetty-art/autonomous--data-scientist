"""
Module 18: API Integration & Orchestration
Integrate all modules into unified API endpoints.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class APIResponse:
    """Standard API response."""
    status: str
    data: Dict[str, Any]
    timestamp: str
    message: str = ""


class APIIntegration:
    """
    Unified API integration.
    
    Integrates:
    - Alerting system
    - Model registry
    - A/B testing
    - Deployment manager
    - Monitoring
    
    Provides REST endpoints for all functionality.
    """
    
    def __init__(self, alerting_manager=None, model_registry=None,
                 ab_framework=None, deployment_manager=None):
        """
        Initialize API integration.
        
        Args:
            alerting_manager: AlertManager instance
            model_registry: ModelRegistry instance
            ab_framework: ABTestFramework instance
            deployment_manager: ProductionDeploymentManager instance
        """
        self.alerting_manager = alerting_manager
        self.model_registry = model_registry
        self.ab_framework = ab_framework
        self.deployment_manager = deployment_manager
    
    # ==================== Alerting Endpoints ====================
    
    def send_alert(self, alert_type: str, severity: str, message: str,
                   channels: Optional[List[str]] = None) -> APIResponse:
        """Send alert through configured channels."""
        try:
            if not self.alerting_manager:
                return APIResponse(
                    status='error',
                    data={},
                    timestamp=datetime.now().isoformat(),
                    message='Alerting service not configured'
                )
            
            self.alerting_manager.send_alert(
                alert_type=alert_type,
                severity=severity,
                message=message,
                channels=channels
            )
            
            return APIResponse(
                status='success',
                data={
                    'alert_type': alert_type,
                    'severity': severity,
                    'channels': channels or []
                },
                timestamp=datetime.now().isoformat(),
                message=f"Alert sent: {alert_type}"
            )
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
            return APIResponse(
                status='error',
                data={},
                timestamp=datetime.now().isoformat(),
                message=str(e)
            )
    
    def get_alert_history(self, limit: int = 100) -> APIResponse:
        """Get alert history."""
        try:
            if not self.alerting_manager:
                return APIResponse(
                    status='error',
                    data={},
                    timestamp=datetime.now().isoformat(),
                    message='Alerting service not configured'
                )
            
            history = self.alerting_manager.get_alert_history(limit=limit)
            
            return APIResponse(
                status='success',
                data={'alerts': history},
                timestamp=datetime.now().isoformat(),
                message=f"Retrieved {len(history)} alerts"
            )
        except Exception as e:
            logger.error(f"Failed to get alert history: {e}")
            return APIResponse(
                status='error',
                data={},
                timestamp=datetime.now().isoformat(),
                message=str(e)
            )
    
    # ==================== Model Registry Endpoints ====================
    
    def register_model(self, model_id: str, model_framework: str,
                      model_data: Dict, performance_metrics: Dict,
                      hyperparameters: Optional[Dict] = None,
                      tags: Optional[List[str]] = None) -> APIResponse:
        """Register model in registry."""
        try:
            if not self.model_registry:
                return APIResponse(
                    status='error',
                    data={},
                    timestamp=datetime.now().isoformat(),
                    message='Model registry not configured'
                )
            
            version = self.model_registry.register_model(
                model_id=model_id,
                model_framework=model_framework,
                model_data=model_data,
                performance_metrics=performance_metrics,
                hyperparameters=hyperparameters,
                tags=tags
            )
            
            return APIResponse(
                status='success',
                data={
                    'model_id': model_id,
                    'version': version,
                    'framework': model_framework
                },
                timestamp=datetime.now().isoformat(),
                message=f"Model registered: {model_id}@{version}"
            )
        except Exception as e:
            logger.error(f"Failed to register model: {e}")
            return APIResponse(
                status='error',
                data={},
                timestamp=datetime.now().isoformat(),
                message=str(e)
            )
    
    def get_model(self, model_id: str, version: Optional[str] = None) -> APIResponse:
        """Get model from registry."""
        try:
            if not self.model_registry:
                return APIResponse(
                    status='error',
                    data={},
                    timestamp=datetime.now().isoformat(),
                    message='Model registry not configured'
                )
            
            model_info = self.model_registry.get_model(model_id=model_id, version=version)
            
            if not model_info:
                return APIResponse(
                    status='error',
                    data={},
                    timestamp=datetime.now().isoformat(),
                    message=f"Model not found: {model_id}"
                )
            
            return APIResponse(
                status='success',
                data=model_info,
                timestamp=datetime.now().isoformat(),
                message=f"Retrieved model: {model_id}"
            )
        except Exception as e:
            logger.error(f"Failed to get model: {e}")
            return APIResponse(
                status='error',
                data={},
                timestamp=datetime.now().isoformat(),
                message=str(e)
            )
    
    def list_models(self, stage: Optional[str] = None) -> APIResponse:
        """List models in registry."""
        try:
            if not self.model_registry:
                return APIResponse(
                    status='error',
                    data={},
                    timestamp=datetime.now().isoformat(),
                    message='Model registry not configured'
                )
            
            models = self.model_registry.list_models(stage=stage)
            
            return APIResponse(
                status='success',
                data={'models': models},
                timestamp=datetime.now().isoformat(),
                message=f"Retrieved {len(models)} models"
            )
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return APIResponse(
                status='error',
                data={},
                timestamp=datetime.now().isoformat(),
                message=str(e)
            )
    
    def transition_model_stage(self, model_id: str, from_stage: str,
                              to_stage: str, reason: str = "") -> APIResponse:
        """Transition model to new stage."""
        try:
            if not self.model_registry:
                return APIResponse(
                    status='error',
                    data={},
                    timestamp=datetime.now().isoformat(),
                    message='Model registry not configured'
                )
            
            self.model_registry.transition_stage(
                model_id=model_id,
                from_stage=from_stage,
                to_stage=to_stage,
                reason=reason
            )
            
            return APIResponse(
                status='success',
                data={
                    'model_id': model_id,
                    'from_stage': from_stage,
                    'to_stage': to_stage
                },
                timestamp=datetime.now().isoformat(),
                message=f"Model transitioned: {from_stage} → {to_stage}"
            )
        except Exception as e:
            logger.error(f"Failed to transition model: {e}")
            return APIResponse(
                status='error',
                data={},
                timestamp=datetime.now().isoformat(),
                message=str(e)
            )
    
    # ==================== A/B Testing Endpoints ====================
    
    def create_ab_test(self, test_id: str, model_control: str,
                       model_treatment: str, target_metric: str,
                       sample_size: int = 1000,
                       significance_level: float = 0.05) -> APIResponse:
        """Create A/B test."""
        try:
            if not self.ab_framework:
                return APIResponse(
                    status='error',
                    data={},
                    timestamp=datetime.now().isoformat(),
                    message='A/B testing service not configured'
                )
            
            self.ab_framework.create_test(
                test_id=test_id,
                model_control=model_control,
                model_treatment=model_treatment,
                target_metric=target_metric,
                sample_size=sample_size,
                significance_level=significance_level
            )
            
            return APIResponse(
                status='success',
                data={
                    'test_id': test_id,
                    'control': model_control,
                    'treatment': model_treatment
                },
                timestamp=datetime.now().isoformat(),
                message=f"A/B test created: {test_id}"
            )
        except Exception as e:
            logger.error(f"Failed to create A/B test: {e}")
            return APIResponse(
                status='error',
                data={},
                timestamp=datetime.now().isoformat(),
                message=str(e)
            )
    
    def add_test_observation(self, test_id: str, group: str,
                            prediction: float, actual: float) -> APIResponse:
        """Add observation to A/B test."""
        try:
            if not self.ab_framework:
                return APIResponse(
                    status='error',
                    data={},
                    timestamp=datetime.now().isoformat(),
                    message='A/B testing service not configured'
                )
            
            self.ab_framework.add_observation(
                test_id=test_id,
                group=group,
                prediction=prediction,
                actual=actual
            )
            
            return APIResponse(
                status='success',
                data={'test_id': test_id, 'group': group},
                timestamp=datetime.now().isoformat(),
                message=f"Observation added to test: {test_id}"
            )
        except Exception as e:
            logger.error(f"Failed to add test observation: {e}")
            return APIResponse(
                status='error',
                data={},
                timestamp=datetime.now().isoformat(),
                message=str(e)
            )
    
    def get_ab_test_results(self, test_id: str) -> APIResponse:
        """Get A/B test results."""
        try:
            if not self.ab_framework:
                return APIResponse(
                    status='error',
                    data={},
                    timestamp=datetime.now().isoformat(),
                    message='A/B testing service not configured'
                )
            
            results = self.ab_framework.get_test_results(test_id=test_id)
            
            if not results:
                return APIResponse(
                    status='error',
                    data={},
                    timestamp=datetime.now().isoformat(),
                    message=f"Test not found: {test_id}"
                )
            
            return APIResponse(
                status='success',
                data=results,
                timestamp=datetime.now().isoformat(),
                message=f"Retrieved results for test: {test_id}"
            )
        except Exception as e:
            logger.error(f"Failed to get test results: {e}")
            return APIResponse(
                status='error',
                data={},
                timestamp=datetime.now().isoformat(),
                message=str(e)
            )
    
    # ==================== Deployment Endpoints ====================
    
    def plan_deployment(self, deployment_id: str, environment: str,
                       model_id: str, model_version: str,
                       replicas: int = 3) -> APIResponse:
        """Plan deployment."""
        try:
            if not self.deployment_manager:
                return APIResponse(
                    status='error',
                    data={},
                    timestamp=datetime.now().isoformat(),
                    message='Deployment manager not configured'
                )
            
            from src.deployment.manager import DeploymentEnvironment
            
            plan = self.deployment_manager.plan_deployment(
                deployment_id=deployment_id,
                environment=DeploymentEnvironment(environment),
                model_id=model_id,
                model_version=model_version,
                replicas=replicas
            )
            
            return APIResponse(
                status='success',
                data=plan,
                timestamp=datetime.now().isoformat(),
                message=f"Deployment plan created: {deployment_id}"
            )
        except Exception as e:
            logger.error(f"Failed to plan deployment: {e}")
            return APIResponse(
                status='error',
                data={},
                timestamp=datetime.now().isoformat(),
                message=str(e)
            )
    
    def execute_deployment(self, deployment_id: str) -> APIResponse:
        """Execute deployment."""
        try:
            if not self.deployment_manager:
                return APIResponse(
                    status='error',
                    data={},
                    timestamp=datetime.now().isoformat(),
                    message='Deployment manager not configured'
                )
            
            results = self.deployment_manager.execute_deployment(
                deployment_id=deployment_id
            )
            
            return APIResponse(
                status='success' if 'error' not in results else 'error',
                data=results,
                timestamp=datetime.now().isoformat(),
                message=f"Deployment executed: {deployment_id}"
            )
        except Exception as e:
            logger.error(f"Failed to execute deployment: {e}")
            return APIResponse(
                status='error',
                data={},
                timestamp=datetime.now().isoformat(),
                message=str(e)
            )
    
    def get_deployment_status(self, deployment_id: str) -> APIResponse:
        """Get deployment status."""
        try:
            if not self.deployment_manager:
                return APIResponse(
                    status='error',
                    data={},
                    timestamp=datetime.now().isoformat(),
                    message='Deployment manager not configured'
                )
            
            status = self.deployment_manager.get_deployment_status(
                deployment_id=deployment_id
            )
            
            return APIResponse(
                status='success' if 'error' not in status else 'error',
                data=status,
                timestamp=datetime.now().isoformat(),
                message=f"Retrieved deployment status: {deployment_id}"
            )
        except Exception as e:
            logger.error(f"Failed to get deployment status: {e}")
            return APIResponse(
                status='error',
                data={},
                timestamp=datetime.now().isoformat(),
                message=str(e)
            )
    
    # ==================== Health & Status ====================
    
    def health_check(self) -> APIResponse:
        """System health check."""
        health = {
            'alerting': bool(self.alerting_manager),
            'registry': bool(self.model_registry),
            'ab_testing': bool(self.ab_framework),
            'deployment': bool(self.deployment_manager)
        }
        
        return APIResponse(
            status='healthy' if all(health.values()) else 'degraded',
            data=health,
            timestamp=datetime.now().isoformat(),
            message='Health check completed'
        )
    
    def get_system_status(self) -> APIResponse:
        """Get comprehensive system status."""
        status = {
            'timestamp': datetime.now().isoformat(),
            'health': self.health_check().data,
            'components': {
                'alerting': 'ready' if self.alerting_manager else 'unavailable',
                'registry': 'ready' if self.model_registry else 'unavailable',
                'ab_testing': 'ready' if self.ab_framework else 'unavailable',
                'deployment': 'ready' if self.deployment_manager else 'unavailable'
            }
        }
        
        return APIResponse(
            status='operational',
            data=status,
            timestamp=datetime.now().isoformat(),
            message='System status retrieved'
        )

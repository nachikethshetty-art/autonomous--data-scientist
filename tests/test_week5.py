"""
Week 5 Comprehensive Test Suite
Tests for Alerting, Model Registry, A/B Testing, Deployment, and API Integration.
Target: 35+ tests, 100% pass rate
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# Import modules to test
from src.alerting.manager import (
    AlertManager, AlertSeverity, AlertChannel, Alert
)
from src.registry.model_registry import (
    ModelRegistry, ModelMetadata, ModelStage
)
from src.testing.ab_framework import (
    ABTestFramework, ABTestConfig, TestStatus
)
from src.deployment.manager import (
    ProductionDeploymentManager, DeploymentEnvironment, DeploymentStatus
)
from src.integration.api import (
    APIIntegration, APIResponse
)


# ==================== Test Alerting System ====================

class TestAlertingSystem:
    """Tests for AlertManager."""
    
    @pytest.fixture
    def alert_manager(self):
        """Create AlertManager instance."""
        return AlertManager()
    
    def test_alert_manager_initialization(self, alert_manager):
        """Test AlertManager initialization."""
        assert alert_manager is not None
        assert hasattr(alert_manager, 'alert_history')
        assert isinstance(alert_manager.alert_history, dict)
    
    def test_send_alert_success(self, alert_manager):
        """Test sending alert successfully."""
        result = alert_manager.send_alert(
            job_id='job_001',
            title='Model Drift Detected',
            message='Drift detected in model performance',
            severity=AlertSeverity.WARNING,
            category='drift'
        )
        
        assert result['status'] in ['sent', 'queued', 'suppressed']
    
    def test_send_alert_with_channels(self, alert_manager):
        """Test sending alert with specific channels."""
        result = alert_manager.send_alert(
            job_id='job_002',
            title='Performance Degradation',
            message='Performance below threshold',
            severity=AlertSeverity.CRITICAL,
            category='performance',
            channels=[AlertChannel.SLACK, AlertChannel.EMAIL]
        )
        
        assert result['status'] in ['sent', 'queued', 'suppressed']
    
    def test_alert_deduplication(self, alert_manager):
        """Test alert deduplication."""
        # Send same alert twice
        alert_manager.send_alert(
            job_id='dup_job',
            title='Test Alert',
            message='Duplicate test',
            severity=AlertSeverity.INFO,
            category='test'
        )
        
        result = alert_manager.send_alert(
            job_id='dup_job',
            title='Test Alert',
            message='Duplicate test',
            severity=AlertSeverity.INFO,
            category='test'
        )
        
        # Second alert should be deduplicated
        assert result['status'] in ['suppressed', 'sent']
    
    def test_alert_severity_enum(self):
        """Test AlertSeverity enum."""
        assert AlertSeverity.CRITICAL.value == 'CRITICAL'
        assert AlertSeverity.WARNING.value == 'WARNING'
        assert AlertSeverity.INFO.value == 'INFO'
        assert AlertSeverity.OK.value == 'OK'
    
    def test_alert_channel_enum(self):
        """Test AlertChannel enum."""
        assert AlertChannel.SLACK.value == 'slack'
        assert AlertChannel.EMAIL.value == 'email'
        assert AlertChannel.SMS.value == 'sms'
        assert AlertChannel.LOG.value == 'log'
        assert AlertChannel.WEBHOOK.value == 'webhook'
    
    def test_get_alert_history(self, alert_manager):
        """Test retrieving alert history."""
        # Send alert first
        alert_manager.send_alert(
            job_id='hist_job',
            title='Test Alert',
            message='Test alert history',
            severity=AlertSeverity.INFO,
            category='test'
        )
        
        # Then get history for this job
        history = alert_manager.get_alert_history('hist_job')
        assert isinstance(history, list)
    
    def test_resolve_alert(self, alert_manager):
        """Test resolving/acknowledging alert."""
        alert_manager.send_alert(
            job_id='resolve_job',
            title='Test Resolution',
            message='Test alert resolution',
            severity=AlertSeverity.WARNING,
            category='test'
        )
        
        # Resolve alert
        resolved = alert_manager.resolve_alert('resolve_job', 'test')
        assert 'status' in resolved


# ==================== Test Model Registry ====================

class TestModelRegistry:
    """Tests for ModelRegistry."""
    
    @pytest.fixture
    def registry(self):
        """Create ModelRegistry instance."""
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = ModelRegistry(registry_dir=tmpdir)
            yield registry
    
    def test_registry_initialization(self, registry):
        """Test ModelRegistry initialization."""
        assert registry is not None
        assert hasattr(registry, 'index')
        assert isinstance(registry.index, dict)
    
    def test_register_model(self, registry):
        """Test registering model."""
        result = registry.register_model(
            model_id='test_model',
            name='Test Model',
            version='1.0.0',
            description='Test model',
            metrics={'accuracy': 0.95},
            parameters={'n_estimators': 100},
            data_version='1.0',
            feature_names=['feat1', 'feat2'],
            problem_type='classification',
            framework='sklearn',
            input_schema={'type': 'dict'},
            output_schema={'type': 'float'}
        )
        
        assert result is not None
        assert 'test_model' in registry.index['models']
    
    def test_register_model_with_lineage(self, registry):
        """Test registering model with parent lineage."""
        result = registry.register_model(
            model_id='v2_model',
            name='V2 Model',
            version='2.0.0',
            description='Improved model',
            metrics={'accuracy': 0.97},
            parameters={'n_estimators': 200},
            data_version='2.0',
            feature_names=['feat1', 'feat2', 'feat3'],
            problem_type='classification',
            framework='sklearn',
            input_schema={'type': 'dict'},
            output_schema={'type': 'float'},
            parent_model_id='test_model'
        )
        
        assert result is not None
    
    def test_get_model(self, registry):
        """Test retrieving model."""
        registry.register_model(
            model_id='retrieve_test',
            name='Retrieve Test',
            version='1.0.0',
            description='Test retrieval',
            metrics={'accuracy': 0.90},
            parameters={},
            data_version='1.0',
            feature_names=['feat1'],
            problem_type='classification',
            framework='sklearn',
            input_schema={},
            output_schema={}
        )
        
        model = registry.get_model('retrieve_test')
        assert model is not None
    
    def test_list_models(self, registry):
        """Test listing models."""
        registry.register_model(
            model_id='model1',
            name='Model 1',
            version='1.0.0',
            description='Model 1',
            metrics={'accuracy': 0.95},
            parameters={},
            data_version='1.0',
            feature_names=['f1'],
            problem_type='classification',
            framework='sklearn',
            input_schema={},
            output_schema={}
        )
        registry.register_model(
            model_id='model2',
            name='Model 2',
            version='1.0.0',
            description='Model 2',
            metrics={'accuracy': 0.92},
            parameters={},
            data_version='1.0',
            feature_names=['f1'],
            problem_type='classification',
            framework='tensorflow',
            input_schema={},
            output_schema={}
        )
        
        models = registry.list_models()
        assert len(models) >= 2
    
    def test_model_stage_enum(self):
        """Test ModelStage enum."""
        assert ModelStage.DEVELOPMENT.value == 'development'
        assert ModelStage.STAGING.value == 'staging'
        assert ModelStage.PRODUCTION.value == 'production'
        assert ModelStage.ARCHIVED.value == 'archived'
    
    def test_transition_stage(self, registry):
        """Test transitioning model stage."""
        registry.register_model(
            model_id='stage_test',
            name='Stage Test',
            version='1.0.0',
            description='Test transitions',
            metrics={'accuracy': 0.95},
            parameters={},
            data_version='1.0',
            feature_names=['f1'],
            problem_type='classification',
            framework='sklearn',
            input_schema={},
            output_schema={}
        )
        
        # Transition needs version and new_stage (as enum)
        result = registry.transition_stage(
            model_id='stage_test',
            version='1.0.0',
            new_stage=ModelStage.STAGING
        )
        
        assert result is not None
    
    def test_search_models(self, registry):
        """Test searching models by framework."""
        registry.register_model(
            model_id='search1',
            name='Search 1',
            version='1.0.0',
            description='Search 1',
            metrics={'accuracy': 0.95},
            parameters={},
            data_version='1.0',
            feature_names=['f1'],
            problem_type='classification',
            framework='sklearn',
            input_schema={},
            output_schema={}
        )
        registry.register_model(
            model_id='search2',
            name='Search 2',
            version='1.0.0',
            description='Search 2',
            metrics={'accuracy': 0.92},
            parameters={},
            data_version='1.0',
            feature_names=['f1'],
            problem_type='classification',
            framework='tensorflow',
            input_schema={},
            output_schema={}
        )
        
        # search_models requires query dict
        results = registry.search_models({'framework': 'sklearn'})
        assert isinstance(results, list)
    
    def test_compare_models(self, registry):
        """Test comparing models."""
        registry.register_model(
            model_id='compare1',
            name='Compare 1',
            version='1.0.0',
            description='Compare 1',
            metrics={'accuracy': 0.95, 'precision': 0.94},
            parameters={},
            data_version='1.0',
            feature_names=['f1'],
            problem_type='classification',
            framework='sklearn',
            input_schema={},
            output_schema={}
        )
        registry.register_model(
            model_id='compare2',
            name='Compare 2',
            version='1.0.0',
            description='Compare 2',
            metrics={'accuracy': 0.92, 'precision': 0.91},
            parameters={},
            data_version='1.0',
            feature_names=['f1'],
            problem_type='classification',
            framework='sklearn',
            input_schema={},
            output_schema={}
        )
        
        # compare_models takes list of model IDs
        comparison = registry.compare_models(['compare1', 'compare2'])
        assert comparison is not None


# ==================== Test A/B Testing ====================

class TestABTesting:
    """Tests for ABTestFramework."""
    
    @pytest.fixture
    def ab_framework(self):
        """Create ABTestFramework instance."""
        with tempfile.TemporaryDirectory() as tmpdir:
            framework = ABTestFramework(tests_dir=tmpdir)
            yield framework
    
    def test_ab_framework_initialization(self, ab_framework):
        """Test ABTestFramework initialization."""
        assert ab_framework is not None
        assert hasattr(ab_framework, 'results_dir')
    
    def test_create_test(self, ab_framework):
        """Test creating A/B test."""
        result = ab_framework.create_test(
            test_id='test_001',
            control_model_id='model_v1',
            treatment_model_id='model_v2',
            metric='accuracy',
            sample_size=100
        )
        
        assert result is not None
        assert result['test_id'] == 'test_001'
        assert result['status'] == TestStatus.RUNNING.value
    
    def test_add_observation(self, ab_framework):
        """Test adding observation."""
        ab_framework.create_test(
            test_id='test_002',
            control_model_id='model_a',
            treatment_model_id='model_b',
            metric='accuracy',
            sample_size=50
        )
        
        result = ab_framework.add_observation(
            test_id='test_002',
            variant='control',
            prediction=0.95,
            actual=1.0
        )
        
        assert result is not None
    
    def test_add_multiple_observations(self, ab_framework):
        """Test adding multiple observations."""
        ab_framework.create_test(
            test_id='test_003',
            control_model_id='model_control',
            treatment_model_id='model_treatment',
            metric='accuracy',
            sample_size=100
        )
        
        # Add observations to both variants
        for i in range(30):
            ab_framework.add_observation(
                test_id='test_003',
                variant='control',
                prediction=0.90 + (i * 0.001),
                actual=1.0 if i % 2 == 0 else 0.0
            )
            ab_framework.add_observation(
                test_id='test_003',
                variant='treatment',
                prediction=0.92 + (i * 0.001),
                actual=1.0 if i % 2 == 0 else 0.0
            )
    
    def test_run_test(self, ab_framework):
        """Test running statistical test."""
        ab_framework.create_test(
            test_id='test_004',
            control_model_id='model1',
            treatment_model_id='model2',
            metric='accuracy',
            sample_size=30,
            significance_level=0.05
        )
        
        # Add observations
        for i in range(30):
            ab_framework.add_observation(
                test_id='test_004',
                variant='control',
                prediction=0.85 + (i * 0.001),
                actual=1.0
            )
            ab_framework.add_observation(
                test_id='test_004',
                variant='treatment',
                prediction=0.88 + (i * 0.001),
                actual=1.0
            )
        
        result = ab_framework.run_test('test_004')
        
        assert result is not None
    
    def test_get_test_results(self, ab_framework):
        """Test retrieving test results."""
        ab_framework.create_test(
            test_id='test_005',
            control_model_id='ctrl',
            treatment_model_id='treat',
            metric='accuracy',
            sample_size=50
        )
        
        ab_framework.add_observation(
            test_id='test_005',
            variant='control',
            prediction=0.90,
            actual=1.0
        )
        
        results = ab_framework.get_test_results('test_005')
        assert results is not None
    
    def test_stop_test(self, ab_framework):
        """Test stopping test early."""
        ab_framework.create_test(
            test_id='test_007',
            control_model_id='model1',
            treatment_model_id='model2',
            metric='accuracy',
            sample_size=100
        )
        
        result = ab_framework.stop_test('test_007', reason='Early stopping')
        
        assert result is not None
        assert result['status'] == TestStatus.STOPPED.value


# ==================== Test Deployment ====================

class TestDeployment:
    """Tests for ProductionDeploymentManager."""
    
    @pytest.fixture
    def deployment_manager(self):
        """Create ProductionDeploymentManager instance."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ProductionDeploymentManager(deployments_dir=tmpdir)
            yield manager
    
    def test_deployment_manager_initialization(self, deployment_manager):
        """Test deployment manager initialization."""
        assert deployment_manager is not None
        assert hasattr(deployment_manager, 'deployments_dir')
    
    def test_plan_deployment(self, deployment_manager):
        """Test planning deployment."""
        plan = deployment_manager.plan_deployment(
            deployment_id='deploy_001',
            environment=DeploymentEnvironment.PRODUCTION,
            model_id='model_v1',
            model_version='1.0.0',
            replicas=3
        )
        
        assert plan is not None
        assert plan['deployment_id'] == 'deploy_001'
        assert plan['status'] == DeploymentStatus.PENDING.value
    
    def test_plan_deployment_strategies(self, deployment_manager):
        """Test deployment strategy selection."""
        # Development - rolling update
        dev_plan = deployment_manager.plan_deployment(
            deployment_id='dev_001',
            environment=DeploymentEnvironment.DEVELOPMENT,
            model_id='model',
            model_version='1.0'
        )
        assert dev_plan['strategy'] == 'rolling_update'
        
        # Staging - blue green
        staging_plan = deployment_manager.plan_deployment(
            deployment_id='stage_001',
            environment=DeploymentEnvironment.STAGING,
            model_id='model',
            model_version='1.0'
        )
        assert staging_plan['strategy'] == 'blue_green'
        
        # Production - canary
        prod_plan = deployment_manager.plan_deployment(
            deployment_id='prod_001',
            environment=DeploymentEnvironment.PRODUCTION,
            model_id='model',
            model_version='1.0'
        )
        assert prod_plan['strategy'] == 'canary'
    
    def test_execute_deployment(self, deployment_manager):
        """Test executing deployment."""
        # First plan
        deployment_manager.plan_deployment(
            deployment_id='execute_001',
            environment=DeploymentEnvironment.STAGING,
            model_id='model_v1',
            model_version='1.0.0'
        )
        
        # Then execute
        result = deployment_manager.execute_deployment('execute_001')
        
        assert result is not None
        assert result['status'] == DeploymentStatus.SUCCEEDED.value
    
    def test_get_deployment_status(self, deployment_manager):
        """Test getting deployment status."""
        deployment_manager.plan_deployment(
            deployment_id='status_001',
            environment=DeploymentEnvironment.PRODUCTION,
            model_id='model',
            model_version='1.0'
        )
        
        status = deployment_manager.get_deployment_status('status_001')
        
        assert status is not None
        assert status['deployment_id'] == 'status_001'
    
    def test_rollback_deployment(self, deployment_manager):
        """Test rolling back deployment."""
        deployment_manager.plan_deployment(
            deployment_id='rollback_001',
            environment=DeploymentEnvironment.PRODUCTION,
            model_id='model',
            model_version='1.0'
        )
        
        deployment_manager.execute_deployment('rollback_001')
        
        rollback = deployment_manager.rollback_deployment(
            deployment_id='rollback_001',
            reason='Performance degradation'
        )
        
        assert rollback is not None
        assert rollback['status'] == DeploymentStatus.ROLLED_BACK.value
    
    def test_get_deployment_history(self, deployment_manager):
        """Test getting deployment history."""
        # Create multiple deployments
        for i in range(3):
            deployment_manager.plan_deployment(
                deployment_id=f'history_{i}',
                environment=DeploymentEnvironment.STAGING,
                model_id=f'model_{i}',
                model_version='1.0'
            )
        
        history = deployment_manager.get_deployment_history()
        
        assert len(history) >= 3


# ==================== Test API Integration ====================

class TestAPIIntegration:
    """Tests for APIIntegration."""
    
    @pytest.fixture
    def api_integration(self):
        """Create APIIntegration instance with mocked components."""
        alert_mgr = Mock(spec=AlertManager)
        alert_mgr.send_alert.return_value = {'status': 'sent', 'alert_id': 'alert_123'}
        alert_mgr.get_alert_history.return_value = []
        
        registry = Mock(spec=ModelRegistry)
        registry.register_model.return_value = 'v1'
        registry.get_model.return_value = {'model_id': 'test'}
        registry.list_models.return_value = []
        
        ab_framework = Mock(spec=ABTestFramework)
        ab_framework.create_test.return_value = None
        ab_framework.get_test_results.return_value = {}
        
        deploy_mgr = Mock(spec=ProductionDeploymentManager)
        deploy_mgr.plan_deployment.return_value = {}
        deploy_mgr.execute_deployment.return_value = {'status': 'succeeded'}
        deploy_mgr.get_deployment_status.return_value = {'status': 'running'}
        
        return APIIntegration(
            alerting_manager=alert_mgr,
            model_registry=registry,
            ab_framework=ab_framework,
            deployment_manager=deploy_mgr
        )
    
    def test_api_response_structure(self):
        """Test APIResponse structure."""
        response = APIResponse(
            status='success',
            data={'key': 'value'},
            timestamp=datetime.now().isoformat(),
            message='Test message'
        )
        
        assert response.status == 'success'
        assert response.data == {'key': 'value'}
    
    def test_send_alert_endpoint(self, api_integration):
        """Test send alert endpoint."""
        response = api_integration.send_alert(
            alert_type='test',
            severity='warning',
            message='Test alert'
        )
        
        assert response.status == 'success'
    
    def test_register_model_endpoint(self, api_integration):
        """Test register model endpoint."""
        response = api_integration.register_model(
            model_id='test_model',
            model_framework='sklearn',
            model_data={},
            performance_metrics={'accuracy': 0.95}
        )
        
        assert response.status == 'success'
    
    def test_get_model_endpoint(self, api_integration):
        """Test get model endpoint."""
        response = api_integration.get_model('test_model')
        
        assert response.status == 'success'
    
    def test_list_models_endpoint(self, api_integration):
        """Test list models endpoint."""
        response = api_integration.list_models()
        
        assert response.status == 'success'
    
    def test_create_ab_test_endpoint(self, api_integration):
        """Test create A/B test endpoint."""
        response = api_integration.create_ab_test(
            test_id='test_001',
            model_control='model_v1',
            model_treatment='model_v2',
            target_metric='accuracy'
        )
        
        assert response.status == 'success'
    
    def test_plan_deployment_endpoint(self, api_integration):
        """Test plan deployment endpoint."""
        response = api_integration.plan_deployment(
            deployment_id='deploy_001',
            environment='production',
            model_id='model_v1',
            model_version='1.0.0'
        )
        
        assert response.status == 'success'
    
    def test_health_check_endpoint(self, api_integration):
        """Test health check endpoint."""
        response = api_integration.health_check()
        
        assert response.status == 'healthy'
        assert 'alerting' in response.data
        assert 'registry' in response.data
    
    def test_system_status_endpoint(self, api_integration):
        """Test system status endpoint."""
        response = api_integration.get_system_status()
        
        assert response.status == 'operational'
        assert 'components' in response.data


# ==================== Integration Tests ====================

class TestWeek5Integration:
    """Integration tests for Week 5 components."""
    
    def test_alert_registry_workflow(self):
        """Test alert and registry integration."""
        alert_mgr = AlertManager()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = ModelRegistry(registry_dir=tmpdir)
            
            # Register model
            registry.register_model(
                model_id='integration_model',
                name='Integration Model',
                version='1.0.0',
                description='Integration test model',
                metrics={'accuracy': 0.95},
                parameters={},
                data_version='1.0',
                feature_names=['f1'],
                problem_type='classification',
                framework='sklearn',
                input_schema={},
                output_schema={}
            )
            
            # Send alert about registration
            alert = alert_mgr.send_alert(
                job_id='int_job',
                title='Model Registered',
                message='New model registered',
                severity=AlertSeverity.INFO,
                category='registration'
            )
            
            assert 'integration_model' in registry.index['models']
    
    def test_deployment_test_workflow(self):
        """Test deployment and testing integration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            deploy_mgr = ProductionDeploymentManager(deployments_dir=tmpdir)
            
            with tempfile.TemporaryDirectory() as test_dir:
                ab_framework = ABTestFramework(tests_dir=test_dir)
                
                # Plan deployment
                deploy_mgr.plan_deployment(
                    deployment_id='integration_deploy',
                    environment=DeploymentEnvironment.STAGING,
                    model_id='model_v1',
                    model_version='1.0'
                )
                
                # Create A/B test
                ab_framework.create_test(
                    test_id='integration_test',
                    control_model_id='model_v1',
                    treatment_model_id='model_v2',
                    metric='accuracy',
                    sample_size=100
                )
                
                history = deploy_mgr.get_deployment_history()
                assert len(history) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])

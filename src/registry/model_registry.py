"""
Module 15: Model Registry and Versioning
Centralized model management with metadata, lineage, and versioning.
"""

import json
import logging
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelStage(Enum):
    """Model lifecycle stages."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    ARCHIVED = "archived"


@dataclass
class ModelMetadata:
    """Model metadata for registry."""
    model_id: str
    name: str
    version: str
    stage: ModelStage
    created_at: str
    created_by: str
    description: str
    metrics: Dict[str, float]
    parameters: Dict[str, Any]
    data_version: str
    feature_names: List[str]
    problem_type: str
    framework: str
    input_schema: Dict
    output_schema: Dict
    tags: Dict[str, str]
    parent_model_id: Optional[str] = None


class ModelRegistry:
    """
    Centralized model registry.
    
    Features:
    - Model versioning and lifecycle management
    - Metadata tracking
    - Model lineage
    - Stage transitions
    - Model comparison
    - Search and filtering
    """
    
    def __init__(self, registry_dir: str = "data/model_registry"):
        """
        Initialize model registry.
        
        Args:
            registry_dir: Directory for model registry
        """
        self.registry_dir = Path(registry_dir)
        self.registry_dir.mkdir(parents=True, exist_ok=True)
        
        self.models_dir = self.registry_dir / "models"
        self.metadata_dir = self.registry_dir / "metadata"
        self.models_dir.mkdir(exist_ok=True)
        self.metadata_dir.mkdir(exist_ok=True)
        
        self.index_file = self.registry_dir / "index.json"
        self._load_index()
    
    def _load_index(self):
        """Load registry index."""
        if self.index_file.exists():
            with open(self.index_file, 'r') as f:
                self.index = json.load(f)
        else:
            self.index = {'models': {}, 'latest_versions': {}}
    
    def _save_index(self):
        """Save registry index."""
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2)
    
    def register_model(self, model_id: str, name: str, version: str,
                      description: str, metrics: Dict[str, float],
                      parameters: Dict[str, Any], data_version: str,
                      feature_names: List[str], problem_type: str,
                      framework: str, input_schema: Dict,
                      output_schema: Dict, tags: Optional[Dict] = None,
                      parent_model_id: Optional[str] = None) -> Dict:
        """
        Register a new model.
        
        Args:
            model_id: Unique model identifier
            name: Model name
            version: Model version
            description: Model description
            metrics: Performance metrics
            parameters: Model parameters
            data_version: Training data version
            feature_names: List of feature names
            problem_type: classification/regression
            framework: ML framework (sklearn, torch, etc.)
            input_schema: Input data schema
            output_schema: Output data schema
            tags: Custom tags
            parent_model_id: Parent model for lineage
        
        Returns:
            Registration details
        """
        metadata = ModelMetadata(
            model_id=model_id,
            name=name,
            version=version,
            stage=ModelStage.DEVELOPMENT,
            created_at=datetime.now().isoformat(),
            created_by="system",
            description=description,
            metrics=metrics,
            parameters=parameters,
            data_version=data_version,
            feature_names=feature_names,
            problem_type=problem_type,
            framework=framework,
            input_schema=input_schema,
            output_schema=output_schema,
            tags=tags or {},
            parent_model_id=parent_model_id
        )
        
        # Save metadata
        metadata_file = self.metadata_dir / f"{model_id}_{version}.json"
        with open(metadata_file, 'w') as f:
            json.dump(asdict(metadata), f, indent=2, default=str)
        
        # Update index
        if model_id not in self.index['models']:
            self.index['models'][model_id] = []
        
        self.index['models'][model_id].append({
            'version': version,
            'stage': metadata.stage.value,
            'created_at': metadata.created_at,
            'metrics': metrics
        })
        
        self.index['latest_versions'][name] = {
            'model_id': model_id,
            'version': version,
            'stage': metadata.stage.value
        }
        
        self._save_index()
        
        logger.info(f"Registered model {model_id} v{version}")
        
        return {
            'model_id': model_id,
            'name': name,
            'version': version,
            'stage': metadata.stage.value,
            'created_at': metadata.created_at
        }
    
    def transition_stage(self, model_id: str, version: str,
                        new_stage: ModelStage) -> Dict:
        """
        Transition model to new stage.
        
        Args:
            model_id: Model identifier
            version: Model version
            new_stage: Target stage
        
        Returns:
            Transition details
        """
        metadata_file = self.metadata_dir / f"{model_id}_{version}.json"
        
        if not metadata_file.exists():
            return {'error': 'Model not found'}
        
        # Load, update, and save metadata
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        old_stage = metadata['stage']
        metadata['stage'] = new_stage.value
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        # Update index
        for idx, model_ver in enumerate(self.index['models'].get(model_id, [])):
            if model_ver['version'] == version:
                model_ver['stage'] = new_stage.value
        
        self._save_index()
        
        logger.info(f"Transitioned {model_id} v{version} from {old_stage} to {new_stage.value}")
        
        return {
            'model_id': model_id,
            'version': version,
            'old_stage': old_stage,
            'new_stage': new_stage.value,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_model(self, model_id: str, version: Optional[str] = None) -> Dict:
        """
        Get model metadata.
        
        Args:
            model_id: Model identifier
            version: Specific version (latest if None)
        
        Returns:
            Model metadata
        """
        if version is None:
            # Get latest version
            versions = self.index['models'].get(model_id, [])
            if not versions:
                return {'error': 'Model not found'}
            version = versions[-1]['version']
        
        metadata_file = self.metadata_dir / f"{model_id}_{version}.json"
        
        if not metadata_file.exists():
            return {'error': 'Model version not found'}
        
        with open(metadata_file, 'r') as f:
            return json.load(f)
    
    def list_models(self, stage: Optional[ModelStage] = None) -> List[Dict]:
        """
        List models in registry.
        
        Args:
            stage: Filter by stage (all if None)
        
        Returns:
            List of models
        """
        models = []
        
        for model_id, versions in self.index['models'].items():
            for version_info in versions:
                if stage is None or version_info['stage'] == stage.value:
                    metadata = self.get_model(model_id, version_info['version'])
                    models.append(metadata)
        
        return models
    
    def search_models(self, query: Dict) -> List[Dict]:
        """
        Search models by criteria.
        
        Args:
            query: Search criteria (framework, problem_type, etc.)
        
        Returns:
            Matching models
        """
        results = []
        
        for model_id, versions in self.index['models'].items():
            for version_info in versions:
                metadata = self.get_model(model_id, version_info['version'])
                
                # Check all query criteria
                match = True
                for key, value in query.items():
                    if metadata.get(key) != value:
                        match = False
                        break
                
                if match:
                    results.append(metadata)
        
        return results
    
    def compare_models(self, model_ids: List[str]) -> Dict:
        """
        Compare multiple models.
        
        Args:
            model_ids: List of model IDs to compare
        
        Returns:
            Comparison report
        """
        comparison = {
            'models': [],
            'metrics_comparison': {},
            'parameters_comparison': {}
        }
        
        for model_id in model_ids:
            metadata = self.get_model(model_id)
            if 'error' not in metadata:
                comparison['models'].append({
                    'model_id': model_id,
                    'version': metadata['version'],
                    'stage': metadata['stage']
                })
                
                # Add metrics
                for metric, value in metadata.get('metrics', {}).items():
                    if metric not in comparison['metrics_comparison']:
                        comparison['metrics_comparison'][metric] = {}
                    comparison['metrics_comparison'][metric][model_id] = value
        
        return comparison
    
    def get_production_model(self, name: str) -> Dict:
        """
        Get production model by name.
        
        Args:
            name: Model name
        
        Returns:
            Production model metadata
        """
        models = self.list_models(stage=ModelStage.PRODUCTION)
        
        for model in models:
            if model.get('name') == name:
                return model
        
        return {'error': f'No production model found: {name}'}
    
    def get_lineage(self, model_id: str, version: str) -> Dict:
        """
        Get model lineage (parent models).
        
        Args:
            model_id: Model identifier
            version: Model version
        
        Returns:
            Lineage information
        """
        metadata = self.get_model(model_id, version)
        
        if 'error' in metadata:
            return metadata
        
        lineage = {
            'current': {
                'model_id': model_id,
                'version': version,
                'name': metadata.get('name')
            },
            'parents': [],
            'depth': 0
        }
        
        # Trace parents
        parent_id = metadata.get('parent_model_id')
        depth = 0
        while parent_id and depth < 10:  # Prevent infinite loops
            parent = self.get_model(parent_id)
            if 'error' not in parent:
                lineage['parents'].append({
                    'model_id': parent_id,
                    'version': parent.get('version'),
                    'name': parent.get('name')
                })
                parent_id = parent.get('parent_model_id')
                depth += 1
            else:
                break
        
        lineage['depth'] = depth
        
        return lineage

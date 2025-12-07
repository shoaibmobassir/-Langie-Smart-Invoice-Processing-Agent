"""Load and parse workflow.json configuration."""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from src.state.models import WorkflowConfig


class WorkflowConfigLoader:
    """Load and parse workflow configuration from JSON."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize loader with config path."""
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "workflow.json"
        self.config_path = Path(config_path)
    
    def load(self) -> Dict[str, Any]:
        """Load workflow configuration from JSON file."""
        with open(self.config_path, "r") as f:
            return json.load(f)
    
    def get_config(self) -> WorkflowConfig:
        """Get workflow config section."""
        workflow = self.load()
        return workflow.get("config", {})
    
    def get_stage(self, stage_id: str) -> Optional[Dict[str, Any]]:
        """Get stage configuration by ID."""
        workflow = self.load()
        stages = workflow.get("stages", [])
        for stage in stages:
            if stage.get("id") == stage_id:
                return stage
        return None
    
    def get_all_stages(self) -> list[Dict[str, Any]]:
        """Get all stage configurations."""
        workflow = self.load()
        return workflow.get("stages", [])
    
    def get_hitl_contract(self) -> Dict[str, Any]:
        """Get HITL API contract."""
        workflow = self.load()
        return workflow.get("human_review_api_contract", {})


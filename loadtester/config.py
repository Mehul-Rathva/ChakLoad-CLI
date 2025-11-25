"""Configuration management for load testing."""
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import asdict

from loadtester.frameworks.base import TestConfig
from loadtester.utils.logger import logger


class Config:
    """Configuration manager for load testing."""
    
    def __init__(self):
        self.framework: Optional[str] = None
        self.test_type: str = "web-site"
        self.target_url: str = ""
        self.users: int = 100
        self.duration: int = 60
        self.rampup: int = 10
        self.custom_params: Dict[str, Any] = {}
        self.config_dir = Path("configs")
        self.config_dir.mkdir(exist_ok=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "framework": self.framework,
            "test_type": self.test_type,
            "target_url": self.target_url,
            "users": self.users,
            "duration": self.duration,
            "rampup": self.rampup,
            "custom_params": self.custom_params
        }
    
    def from_dict(self, data: Dict[str, Any]) -> 'Config':
        """Load configuration from dictionary."""
        self.framework = data.get("framework")
        self.test_type = data.get("test_type", "web-site")
        self.target_url = data.get("target_url", "")
        self.users = data.get("users", 100)
        self.duration = data.get("duration", 60)
        self.rampup = data.get("rampup", 10)
        self.custom_params = data.get("custom_params", {})
        
        return self
    
    def save_config(self, name: str) -> str:
        """Save current configuration to a named file."""
        config_path = self.config_dir / f"{name}.yaml"
        
        with open(config_path, 'w') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False)
        
        return str(config_path)
    
    def load_config(self, name: str) -> 'Config':
        """Load configuration from a named file."""
        config_path = self.config_dir / f"{name}.yaml"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file {config_path} does not exist")
        
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
        
        return self.from_dict(data)
    
    def list_configs(self) -> list:
        """List all saved configurations."""
        configs = []
        for config_file in self.config_dir.glob("*.yaml"):
            configs.append(config_file.stem)
        return configs
    
    def to_test_config(self) -> TestConfig:
        """Convert to TestConfig dataclass."""
        return TestConfig(
            target_url=self.target_url,
            users=self.users,
            duration=self.duration,
            rampup=self.rampup,
            test_type=self.test_type,
            framework=self.framework or "locust",  # Default to locust
            custom_params=self.custom_params
        )


def load_default_config() -> Config:
    """Load the default configuration."""
    config = Config()
    # Try to load default config if it exists
    default_path = Path("configs") / "default.yaml"
    if default_path.exists():
        try:
            config.load_config("default")
        except Exception as e:
            logger.warning(f"Could not load default config: {e}")
    
    return config
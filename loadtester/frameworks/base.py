"""Base framework classes for load testing frameworks."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional
import subprocess
import tempfile
import os


@dataclass
class TestConfig:
    """Configuration for a load test."""
    target_url: str = ""
    users: int = 100
    duration: int = 60
    rampup: int = 10
    test_type: str = "web-site"
    framework: str = "locust"
    custom_params: Optional[Dict[str, Any]] = None


@dataclass
class TestResults:
    """Results of a load test."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    requests_per_second: float = 0.0
    avg_response_time: float = 0.0
    median_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    min_response_time: float = 0.0
    max_response_time: float = 0.0
    error_rate: float = 0.0
    errors: Optional[Dict[str, int]] = None
    data_sent_mb: float = 0.0
    data_received_mb: float = 0.0
    duration: int = 0


class BaseFramework(ABC):
    """Base class for load testing frameworks."""
    
    @abstractmethod
    def prepare_test(self, config: TestConfig) -> str:
        """Prepare the test script from a template."""
        pass
    
    @abstractmethod
    def run_test(self, script_path: str, config: TestConfig) -> TestResults:
        """Run the load test."""
        pass
    
    @abstractmethod
    def parse_results(self, output: str) -> TestResults:
        """Parse the results of the test."""
        pass
    
    @abstractmethod
    def stop_test(self):
        """Stop a running test."""
        pass
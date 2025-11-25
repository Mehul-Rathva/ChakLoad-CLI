"""Framework availability checker."""
import subprocess
import shutil
from typing import Dict, List


def check_framework_availability() -> Dict[str, bool]:
    """Check which frameworks are available on the system."""
    available = {}

    # Check for K6
    available['k6'] = bool(shutil.which('k6'))

    # Check for Locust (import-based check since it's a Python package)
    try:
        import locust
        available['locust'] = True
    except ImportError:
        available['locust'] = False

    # Check for JMeter
    available['jmeter'] = bool(shutil.which('jmeter'))

    # Check for Artillery
    available['artillery'] = bool(shutil.which('artillery'))

    return available


def get_available_frameworks() -> List[str]:
    """Get list of currently available frameworks."""
    availability = check_framework_availability()
    available_list = ['simple', 'http', 'advanced', 'builtin']  # Built-in frameworks

    for framework, is_available in availability.items():
        if is_available:
            available_list.append(framework)

    return available_list
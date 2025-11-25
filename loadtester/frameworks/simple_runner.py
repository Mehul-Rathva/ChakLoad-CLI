"""Simple HTTP-based load testing framework using requests."""
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from loadtester.frameworks.base import BaseFramework, TestConfig, TestResults
from loadtester.utils.logger import logger


class SimpleHttpRunner(BaseFramework):
    """Simple HTTP load testing framework using requests library."""
    
    def __init__(self):
        self.active = False
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def prepare_test(self, config: TestConfig) -> str:
        """Prepare test configuration - no script needed for this simple runner."""
        # For this simple runner, we don't need to generate a script
        # Instead, we'll use the configuration directly
        return f"config_{config.target_url.replace('https://', '').replace('http://', '').replace('/', '_')}"
    
    def run_test(self, script_path: str, config: TestConfig) -> TestResults:
        """Run the load test using threads."""
        logger.info(f"Starting load test with {config.users} users for {config.duration} seconds")
        
        self.active = True
        start_time = time.time()
        results = TestResults()
        results.duration = config.duration
        
        # Store responses for later analysis
        responses = []
        
        # Calculate ramp-up time
        rampup_time = config.rampup
        total_test_time = config.duration
        
        def make_request(user_id: int):
            """Function to make individual requests."""
            if not self.active:
                return None
                
            try:
                start_req_time = time.time()
                response = self.session.get(config.target_url)
                end_req_time = time.time()
                
                req_time_ms = (end_req_time - start_req_time) * 1000
                
                return {
                    'status_code': response.status_code,
                    'response_time': req_time_ms,
                    'size': len(response.content),
                    'user_id': user_id
                }
            except Exception as e:
                logger.debug(f"Request error: {str(e)}")
                return {
                    'status_code': 0,
                    'response_time': 0,
                    'size': 0,
                    'error': str(e),
                    'user_id': user_id
                }
        
        # Calculate how long to run
        end_time = start_time + total_test_time
        
        # Use ThreadPoolExecutor to manage the users
        with ThreadPoolExecutor(max_workers=config.users) as executor:
            # Submit initial batch of requests
            future_to_user = {executor.submit(make_request, i): i for i in range(config.users)}
            
            # Continue making requests for the duration
            while time.time() < end_time and self.active:
                # Process completed requests
                for future in as_completed(future_to_user):
                    response_data = future.result()
                    if response_data:
                        responses.append(response_data)
                    
                    # Submit a new request to replace the completed one
                    if time.time() < end_time and self.active:
                        new_future = executor.submit(make_request, future_to_user[future])
                        future_to_user[new_future] = future_to_user[future]
                    
                    # Remove completed future from tracking
                    del future_to_user[future]
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.01)
        
        # Process all responses to calculate metrics
        if responses:
            results.total_requests = len(responses)
            successful_responses = [r for r in responses if r.get('status_code', 0) and r['status_code'] < 400]
            failed_responses = [r for r in responses if r.get('status_code', 0) and r['status_code'] >= 400]
            error_responses = [r for r in responses if 'error' in r]
            
            results.successful_requests = len(successful_responses)
            results.failed_requests = len(failed_responses)
            
            if results.total_requests > 0:
                results.error_rate = (len(failed_responses) + len(error_responses)) / results.total_requests * 100
            
            # Calculate response times
            response_times = [r['response_time'] for r in responses if r.get('response_time', 0) > 0]
            if response_times:
                response_times.sort()
                results.avg_response_time = sum(response_times) / len(response_times)
                results.median_response_time = response_times[len(response_times) // 2] 
                results.min_response_time = min(response_times)
                results.max_response_time = max(response_times)
                
                if len(response_times) > 0:
                    # Calculate percentiles
                    p95_idx = int(0.95 * len(response_times))
                    p99_idx = int(0.99 * len(response_times))
                    
                    if p95_idx < len(response_times):
                        results.p95_response_time = response_times[p95_idx]
                    if p99_idx < len(response_times):
                        results.p99_response_time = response_times[p99_idx]
                
                # Calculate requests per second
                actual_duration = time.time() - start_time
                if actual_duration > 0:
                    results.requests_per_second = results.total_requests / actual_duration
            
            # Calculate data transfer
            total_data = sum([r.get('size', 0) for r in responses])
            results.data_sent_mb = 0  # This is a simple client, no data sent
            results.data_received_mb = total_data / (1024 * 1024)
            
            # Count error types
            error_counts = {}
            for r in responses:
                if 'error' in r:
                    error_type = type(r['error']).__name__ if hasattr(r['error'], '__class__') else str(r['error'])
                    error_counts[error_type] = error_counts.get(error_type, 0) + 1
                elif r.get('status_code', 0) >= 400:
                    status_code = str(r['status_code'])
                    error_counts[status_code] = error_counts.get(status_code, 0) + 1
            
            results.errors = error_counts
        
        self.active = False
        return results
    
    def parse_results(self, output: str) -> TestResults:
        """Parse results from output (not used in this implementation)."""
        # This method is not needed for this implementation since we calculate results directly
        return TestResults()
    
    def stop_test(self):
        """Stop the running test."""
        self.active = False
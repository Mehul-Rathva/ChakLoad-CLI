"""Enhanced HTTP-based load testing framework using requests library."""
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from datetime import datetime
import statistics

from loadtester.frameworks.base import BaseFramework, TestConfig, TestResults
from loadtester.utils.logger import logger


class EnhancedHttpRunner(BaseFramework):
    """Enhanced HTTP load testing framework using requests library with advanced features."""
    
    def __init__(self):
        self.active = False
        self.sessions: List[requests.Session] = []
        self.user_threads = []  # Track active threads
    
    def prepare_test(self, config: TestConfig) -> str:
        """Prepare test configuration - no script needed for this runner."""
        return f"config_{config.target_url.replace('https://', '').replace('http://', '').replace('/', '_')}"
    
    def run_test(self, script_path: str, config: TestConfig) -> TestResults:
        """Run the load test using threads with advanced metrics."""
        logger.info(f"Starting enhanced load test with {config.users} users for {config.duration} seconds")

        self.active = True
        start_time = time.time()
        results = TestResults()
        results.duration = config.duration

        # Store all response data for detailed analysis
        all_responses = []
        response_lock = threading.Lock()  # Protect shared data

        # Create session pool
        for _ in range(config.users):
            session = requests.Session()

            # Configure retry strategy
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("http://", adapter)
            session.mount("https://", adapter)

            self.sessions.append(session)

        def make_requests_for_user(session_idx: int):
            """Function to make multiple requests for a single user."""
            session = self.sessions[session_idx]
            user_responses = []

            # Determine request pattern based on test type
            if config.test_type == "telegram-webhook":
                request_func = self._make_webhook_request
            elif config.test_type == "api-endpoint":
                request_func = self._make_api_request
            else:  # web-site
                request_func = self._make_web_request

            # For telegram webhook, we might want to simulate realistic request patterns
            # Telegram sends webhook requests sequentially, so in a real scenario,
            # you'd have different "virtual" users sending messages, not concurrent requests
            if config.test_type == "telegram-webhook":
                # Simulate realistic delays for Telegram webhook testing
                message_interval = max(0.01, 1.0 / (config.users or 10))  # Reduce to 0.01 for faster testing
            else:
                message_interval = 0.1  # Default interval for other test types

            user_start_time = time.time()

            # Calculate when this thread should stop
            thread_end_time = start_time + config.duration
            while self.active and time.time() < thread_end_time:
                try:
                    start_req_time = time.time()
                    response_data = request_func(config, session)
                    end_req_time = time.time()

                    req_time_ms = (end_req_time - start_req_time) * 1000

                    # Record response data
                    response_record = {
                        'timestamp': datetime.now(),
                        'response_time': req_time_ms,
                        'status_code': response_data.get('status_code', 0),
                        'size': response_data.get('size', 0),
                        'error': response_data.get('error'),
                        'session_idx': session_idx
                    }

                    user_responses.append(response_record)

                    # Add to global responses list with thread safety
                    with response_lock:
                        all_responses.append(response_record)

                except Exception as e:
                    error_record = {
                        'timestamp': datetime.now(),
                        'response_time': 0,
                        'status_code': 0,
                        'size': 0,
                        'error': str(e),
                        'session_idx': session_idx
                    }
                    with response_lock:
                        all_responses.append(error_record)

                # Add delay based on test type, but make sure we don't exceed test duration
                remaining_time = thread_end_time - time.time()
                if remaining_time <= 0:
                    break  # Stop if no time left

                # Sleep for interval but don't exceed remaining time
                sleep_time = min(message_interval, max(0, remaining_time))
                time.sleep(sleep_time)

            # Add all user responses to global list
            return user_responses

        # Ramp-up logic: gradually start users over rampup time
        with ThreadPoolExecutor(max_workers=min(config.users, 50)) as executor:  # Limit max concurrent workers
            futures = []

            # Submit initial batch of users with ramp-up
            for i in range(config.users):
                if config.rampup > 0 and i > 0:
                    # Add delay for gradual ramp-up
                    delay = min((config.rampup / config.users) * i, 1.0)  # Max 1s delay per user
                    time.sleep(delay)

                if self.active:
                    future = executor.submit(make_requests_for_user, i)
                    futures.append(future)

            # Wait for all futures to complete with a timeout
            try:
                for future in as_completed(futures, timeout=config.duration + 30):
                    try:
                        future.result(timeout=10)  # Each thread has 10s to finish
                    except Exception as e:
                        logger.warning(f"Thread did not complete properly: {str(e)}")
            except Exception as e:
                logger.warning(f"Some threads did not complete in time: {str(e)}")

        # Stop all activity
        self.active = False

        # Process all collected responses to calculate metrics
        if all_responses:
            results.total_requests = len(all_responses)
            successful_responses = [r for r in all_responses if r['status_code'] and 0 < r['status_code'] < 400 and not r.get('error')]
            failed_responses = [r for r in all_responses if r['status_code'] and r['status_code'] >= 400]
            error_responses = [r for r in all_responses if r.get('error')]

            results.successful_requests = len(successful_responses)
            results.failed_requests = len(failed_responses)

            if results.total_requests > 0:
                results.error_rate = (len(failed_responses) + len(error_responses)) / results.total_requests * 100

            # Calculate response times
            response_times = [r['response_time'] for r in all_responses if r['response_time'] > 0]
            if response_times:
                response_times.sort()
                results.avg_response_time = sum(response_times) / len(response_times)

                if len(response_times) > 0:
                    results.median_response_time = response_times[len(response_times) // 2]
                    results.min_response_time = min(response_times)
                    results.max_response_time = max(response_times)

                if len(response_times) > 0:
                    # Calculate percentiles
                    if len(response_times) >= 20:  # Need enough data for percentiles
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
            total_data = sum([r.get('size', 0) for r in all_responses])
            results.data_sent_mb = 0  # This is a client, no significant data sent
            results.data_received_mb = total_data / (1024 * 1024)

            # Count error types
            error_counts = {}
            for r in all_responses:
                if r.get('error'):
                    error_type = r['error'].__class__.__name__ if hasattr(r['error'], '__class__') else str(r['error'])
                    error_counts[error_type] = error_counts.get(error_type, 0) + 1
                elif r.get('status_code', 0) >= 400:
                    status_code = str(r['status_code'])
                    error_counts[status_code] = error_counts.get(status_code, 0) + 1

            results.errors = error_counts

        # Clean up sessions
        for session in self.sessions:
            try:
                session.close()
            except:
                pass  # Ignore errors when closing sessions
        self.sessions = []

        self.active = False
        return results
    
    def _make_web_request(self, config: TestConfig, session: requests.Session):
        """Make web request for website testing."""
        try:
            response = session.get(config.target_url)
            content_size = len(response.content) if response.content else 0
            return {
                'status_code': response.status_code,
                'size': content_size
            }
        except Exception as e:
            return {
                'status_code': 0,
                'size': 0,
                'error': str(e)
            }
    
    def _make_api_request(self, config: TestConfig, session: requests.Session):
        """Make API request for API endpoint testing."""
        try:
            # Determine method based on custom params or default to GET
            method = config.custom_params.get('method', 'GET').upper() if config.custom_params else 'GET'
            
            if method == 'GET':
                response = session.get(config.target_url)
            elif method == 'POST':
                payload = config.custom_params.get('payload', {}) if config.custom_params else {}
                response = session.post(config.target_url, json=payload)
            elif method == 'PUT':
                payload = config.custom_params.get('payload', {}) if config.custom_params else {}
                response = session.put(config.target_url, json=payload)
            elif method == 'DELETE':
                response = session.delete(config.target_url)
            else:
                response = session.get(config.target_url)  # Default fallback
            
            content_size = len(response.content) if response.content else 0
            return {
                'status_code': response.status_code,
                'size': content_size
            }
        except Exception as e:
            return {
                'status_code': 0,
                'size': 0,
                'error': str(e)
            }
    
    def _make_webhook_request(self, config: TestConfig, session: requests.Session):
        """Make webhook request for Telegram webhook testing."""
        try:
            # Prepare webhook payload
            import random
            payload = {
                "update_id": random.randint(100000, 999999),
                "message": {
                    "message_id": 1,
                    "from": {
                        "id": random.randint(100000, 999999),
                        "first_name": "Test",
                        "is_bot": False,
                        "username": "testuser",
                        "language_code": "en"
                    },
                    "chat": {
                        "id": random.randint(100000, 999999),
                        "type": "private",
                        "first_name": "Test",
                        "username": "testuser"
                    },
                    "date": int(time.time()),
                    "text": "Hello from load test!"
                }
            }

            response = session.post(config.target_url, json=payload)
            content_size = len(response.content) if response.content else 0
            return {
                'status_code': response.status_code,
                'size': content_size
            }
        except Exception as e:
            return {
                'status_code': 0,
                'size': 0,
                'error': str(e)
            }
    
    def parse_results(self, output: str) -> TestResults:
        """Parse results from output (not used in this implementation)."""
        # This method is not needed for this implementation since we calculate results directly
        return TestResults()
    
    def stop_test(self):
        """Stop the running test."""
        self.active = False
        # Close all sessions
        for session in self.sessions:
            session.close()
        self.sessions = []
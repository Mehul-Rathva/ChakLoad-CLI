from locust import HttpUser, task, between
import json

class ApiEndpointUser(HttpUser):
    wait_time = between(1, 3)
    host = "${TARGET_URL}"
    
    @task(${GET_WEIGHT})
    def get_request(self):
        headers = {"Content-Type": "application/json"}
        self.client.get("${ENDPOINT_PATH}", headers=headers)
    
    @task(${POST_WEIGHT})
    def post_request(self):
        headers = {"Content-Type": "application/json"}
        payload = ${REQUEST_BODY}
        self.client.post("${ENDPOINT_PATH}", json=payload, headers=headers)
    
    def on_start(self):
        # Any initialization code
        pass
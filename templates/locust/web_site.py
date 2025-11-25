from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)
    host = "${TARGET_URL}"

    @task(${WEIGHT_HOME})
    def load_home(self):
        self.client.get("/")

    @task(${WEIGHT_API})
    def load_api(self):
        self.client.get("/api/data")

    def on_start(self):
        # Any initialization code
        pass
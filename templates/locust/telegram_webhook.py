from locust import HttpUser, task
import json

class TelegramWebhookUser(HttpUser):
    host = "${WEBHOOK_URL}"
    
    @task
    def send_message(self):
        payload = {
            "update_id": self.generate_update_id(),
            "message": {
                "message_id": 1,
                "from": {"id": 12345, "first_name": "Test", "is_bot": False, "username": "testuser", "language_code": "en"},
                "chat": {"id": 12345, "type": "private", "first_name": "Test", "username": "testuser"},
                "date": 1678886400,
                "text": "${TEST_MESSAGE}"
            }
        }
        self.client.post("", json=payload)
    
    def generate_update_id(self):
        import random
        return random.randint(100000, 999999)
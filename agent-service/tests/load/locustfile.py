from locust import HttpUser, task, between

class AgentUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def send_message(self):
        self.client.post(
            "/chat",
            json={"message": "Load test message"},
            headers={"Authorization": "Bearer test_token"}
        )
    
    @task(3)  # 3x more frequent
    def quick_reply(self):
        self.client.post(
            "/chat",
            json={"message": "Hi"},
            headers={"Authorization": "Bearer test_token"}
        )
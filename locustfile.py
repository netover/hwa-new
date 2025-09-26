from locust import HttpUser, task


class AuditUser(HttpUser):
    @task
    def audit_check(self):
        self.client.post("/audit", {"lock_id": "123"})

    @task
    def chat_endpoint(self):
        self.client.post("/chat", {"message": "test message"})

    @task
    def endpoints_list(self):
        self.client.get("/endpoints")

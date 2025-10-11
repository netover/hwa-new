from locust import HttpUser, task


class AuditUser(HttpUser):
    @task
    def audit_check(self) -> None:
        self.client.post("/audit", {"lock_id": "123"})

    @task
    def chat_endpoint(self) -> None:
        self.client.post("/chat", {"message": "test message"})

    @task
    def endpoints_list(self) -> None:
        self.client.get("/endpoints")

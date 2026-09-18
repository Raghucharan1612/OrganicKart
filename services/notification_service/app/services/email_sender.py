from typing import Protocol


class EmailSender(Protocol):
    def send(self, recipient_user_id: int, subject: str, message: str) -> bool:
        ...


class MockEmailSender:
    def __init__(self):
        self.sent_messages: list[tuple[int, str, str]] = []

    def send(self, recipient_user_id: int, subject: str, message: str) -> bool:
        self.sent_messages.append((recipient_user_id, subject, message))
        return True

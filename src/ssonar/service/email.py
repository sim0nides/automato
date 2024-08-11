import smtplib
from typing import Protocol


class EmailService(Protocol):
    from_addr: str

    def send_email(self, to_address: str, body: str) -> None: ...


__service: EmailService | None = None


def register_email_service(service: EmailService):
    global __service
    __service = service


def get_email_service() -> EmailService:
    if not __service:
        raise NotImplementedError("call register_email_service()")

    return __service


class SMTPEmailService(EmailService):
    def __init__(self, host: str, port: int, user: str, password: str) -> None:
        self.host = host
        self.port = port
        self.user = user
        self.password = password

    @property
    def from_addr(self) -> str:
        return self.user

    def send_email(self, to_address: str, body: str) -> None:
        with smtplib.SMTP_SSL(self.host, self.port) as server:
            server.login(self.user, self.password)
            server.sendmail(self.user, to_address, body)

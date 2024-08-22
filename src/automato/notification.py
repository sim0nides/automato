from abc import ABC, abstractmethod
from dataclasses import dataclass
from email.message import EmailMessage
from typing import Optional, Protocol

from automato.service.email import EmailService


class INotifiable(Protocol):
    def get_mail_receiver(self) -> str: ...


class INotification(Protocol):
    def send(self, notifiable: INotifiable): ...


@dataclass
class Mail:
    subject: str
    html: Optional[str] = None
    plain: Optional[str] = None


class Notifiable:
    def get_mail_receiver(self) -> str:
        raise NotImplementedError("get_mail_receiver method not implemented!")


@dataclass
class NotificationWithService:
    def __init__(self, service: EmailService) -> None:
        self.__service: EmailService = service

    @property
    def _service(self) -> EmailService:
        return self.__service


class EmailNotification(NotificationWithService, ABC):
    @abstractmethod
    def get_mail(self) -> Mail:
        pass

    def _construct_email_message(
        self, notifiable: INotifiable, from_address: str
    ) -> str:
        mail = self.get_mail()

        e_msg = EmailMessage()
        e_msg["From"] = from_address
        e_msg["To"] = notifiable.get_mail_receiver()
        e_msg["Subject"] = mail.subject

        if mail.html is not None:
            e_msg.set_content(mail.html, subtype="html")

        if mail.plain is not None:
            e_msg.add_attachment(mail.plain)

        return e_msg.as_string()

    def send(self, notifiable: INotifiable):
        message_string = self._construct_email_message(
            notifiable, self._service.from_addr
        )

        self._service.send_email(notifiable.get_mail_receiver(), message_string)

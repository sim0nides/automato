import pytest

from automato.notification import Mail, NotificationWithService


class TestMail:
    def test_default_html_property_value(self):
        mail = Mail("subject")
        assert mail.html is None

    def test_default_plain_property_value(self):
        mail = Mail("subject")
        assert mail.plain is None

    def test_subject_property(self):
        subject = "subject"
        mail = Mail(subject)
        assert mail.subject == subject

    def test_subject_property_is_required(self):
        with pytest.raises(Exception):
            Mail()  # type: ignore


class Dummy(NotificationWithService):
    pass


@pytest.fixture
def notification_with_service():
    yield Dummy()
    Dummy.set_email_service(None)  # type: ignore


class TestNotificationWithService:
    def test_set_email_service(self, notification_with_service):
        fake_service = {}
        notification_with_service.set_email_service(fake_service)
        assert notification_with_service.get_email_service() is fake_service

    def test_not_set_email_service(self, notification_with_service):
        with pytest.raises(ValueError):
            notification_with_service.get_email_service()

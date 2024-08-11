import pytest
from ssonar.notification import Mail


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

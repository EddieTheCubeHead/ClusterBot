import smtplib
import ssl

from discord_helpers.exception_handling import UserException

_PORT = 465  # For SSL
_BOT_EMAIL = "cluster.guild.bot@gmail.com"


class EmailService:

    def __init__(self, username: str | None, password: str | None):
        if username is None or password is None:
            self._set_up = False
            return
        self._set_up = True
        self._context = ssl.create_default_context()
        self._server = smtplib.SMTP_SSL("smtp.gmail.com", _PORT, context=self._context)
        self._server.login(username, password)

    def send_email(self, recipient: str, content: str):
        if not self._set_up:
            raise UserException("Email sending not configured in the running environment. "
                                "See README.md for more information.")
        self._server.sendmail(_BOT_EMAIL, recipient, content)


def validate_student_email(email: str) -> bool:
    return email.endswith("@student.lut.fi")

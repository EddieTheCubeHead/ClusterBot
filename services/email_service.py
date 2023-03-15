import smtplib, ssl

_PORT = 465  # For SSL
_BOT_EMAIL = "cluster.guild.bot@gmail.com"


class EmailService:

    def __init__(self, password: str):
        self._context = ssl.create_default_context()
        self._server = smtplib.SMTP_SSL("smtp.gmail.com", _PORT, context=self._context)
        self._server.login(_BOT_EMAIL, password)

    def send_email(self, recipient: str, content: str):
        self._server.sendmail(_BOT_EMAIL, recipient, content)


def validate_student_email(email: str) -> bool:
    return email.endswith("@student.lut.fi")

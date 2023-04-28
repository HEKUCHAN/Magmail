from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class Mail:
    def __init__(
        self,
        to,
        h_from,
        cc_mail,
        subject,
        message,
        mime_type="plain"
    ):
        self.to = to
        self.h_from = h_from
        self.cc_mail = cc_mail
        self.subject = subject
        self.message = message
        self.mime_type = mime_type
        self.__init()

    def __init(self):
        if self.mime_type == "plain":
            self.mime = MIMEText(self.message, 'plain')
        elif self.mime_type == "html":
            self.mime = MIMEText(self.message, 'html')
        elif self.mime_type == "multipart":
            self.mime = MIMEMultipart()

            if not isinstance(self.message, dict):
                # TODO: 型が間違っているということを書く
                raise TypeError()

            if "plain" in self.message and "html" in self.message:
                # TODO: 辞書である必要があって、ある値がないといけないというエラーを記述
                raise ""

            self.mime.attach(MIMEText(self.message['plain'], 'plain'))
            self.mime.attach(MIMEText(self.message['html'], 'html'))

        self.mime["Subject"] = self.subject
        self.mime["To"] = self.to
        self.mime["From"] = self.h_from
        self.mime["cc"] = self.cc_mail

        

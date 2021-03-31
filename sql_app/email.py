from fastapi_mail import FastMail, ConnectionConfig

from . import dependencies

settings = dependencies.get_settings()
conf = ConnectionConfig(MAIL_FROM=settings.mail_from,
                        MAIL_FROM_NAME=settings.mail_from_name,
                        MAIL_USERNAME=settings.mail_username,
                        MAIL_PASSWORD=settings.mail_password,
                        MAIL_PORT=settings.mail_port,
                        MAIL_SERVER=settings.mail_server,
                        MAIL_TLS=settings.mail_tls,
                        MAIL_SSL=settings.mail_ssl)

fm = FastMail(conf)
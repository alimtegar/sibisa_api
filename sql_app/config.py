from pydantic import BaseSettings, StrictBool


class Settings(BaseSettings):
    app_name: str
    app_url: str
    
    db_dialect: str
    db_driver: str
    db_username: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str
    db_socket: str
    
    token_key: str
    token_algorithm: str
    token_expire_minutes: int
    
    mail_username: str
    mail_password: str
    mail_from: str
    mail_from_name: str
    mail_port: int
    mail_server: str
    mail_tls: bool
    mail_ssl: bool

    class Config:
        env_file = 'sql_app/.env'

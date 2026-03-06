import os


class Config:
    SECRET_KEY = "mysecretkey123"
    SQLALCHEMY_DATABASE_URI = "sqlite:///placement_portal.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECURITY_PASSWORD_SALT = "mysalt123"
    SECURITY_TOKEN_AUTHENTICATION_HEADER = "Authentication-Token"
    SECURITY_TOKEN_MAX_AGE = 3600
    WTF_CSRF_ENABLED = False

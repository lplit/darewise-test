import logging
from typing import Optional

from pydantic import BaseSettings, SecretStr

logger = logging.getLogger(__name__)

"""
Application-wide configuration settings
"""


class Settings(BaseSettings):
    # All of the below are provided with environment variables. They are here
    # only to produce boot errors in case any of them is missing from env.
    debug: bool = False
    mongodb_database: str
    mongodb_hostname: str
    mongodb_password: SecretStr
    mongodb_username: str

    class Config:
        allow_mutation = False


settings = Settings()

if settings.debug:
    logging.basicConfig(level=logging.DEBUG)

logger.info(f"🐻 Backlog starting with settings {settings}")

# Copyright 2022 Indoc Research
# 
# Licensed under the EUPL, Version 1.2 or – as soon they
# will be approved by the European Commission - subsequent
# versions of the EUPL (the "Licence");
# You may not use this work except in compliance with the
# Licence.
# You may obtain a copy of the Licence at:
# 
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12
# 
# Unless required by applicable law or agreed to in
# writing, software distributed under the Licence is
# distributed on an "AS IS" basis,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied.
# See the Licence for the specific language governing
# permissions and limitations under the Licence.
# 

import os
from pydantic import BaseSettings, Extra
from typing import Dict, Any
from functools import lru_cache
from common import VaultClient

SRV_NAMESPACE = os.environ.get("APP_NAME", "service_encryption")
CONFIG_CENTER_ENABLED = os.environ.get("CONFIG_CENTER_ENABLED", "false")


def load_vault_settings(settings: BaseSettings) -> Dict[str, Any]:
    if CONFIG_CENTER_ENABLED == "false":
        return {}
    else:
        return vault_factory()


def vault_factory() -> dict:
    vc = VaultClient(os.getenv("VAULT_URL"), os.getenv("VAULT_CRT"), os.getenv("VAULT_TOKEN"))
    return vc.get_from_vault(SRV_NAMESPACE)


class Settings(BaseSettings):
    env: str = os.environ.get('env', '')
    version: str = "0.1.0"

    port: int = 5082
    host: str = "0.0.0.0"
    ENCRYPT_VAULT_SERVICE: str = "https://vault.vault:8200"
    ENCRYPT_VAULT_CRT: str = "/run/secrets/kubernetes.io/serviceaccount/ca.crt"
    ENCRYPT_VAULT_TOKEN: str = "s.qG4Wk5UMnacdtEV5jvBzhBdb"

    # minio
    MINIO_OPENID_CLIENT: str
    MINIO_ENDPOINT: str
    MINIO_HTTPS: bool = False
    KEYCLOAK_URL: str
    KEYCLOAK_PATH: str
    MINIO_TEST_PASS: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    KEYCLOAK_SECRET: str

    NEO4J_SERVICE: str

    RDS_HOST: str
    RDS_PORT: str
    RDS_DBNAME: str
    RDS_USER: str
    RDS_PWD: str
    RDS_SCHEMA_DEFAULT: str

    def modify_values(self, settings):
        settings.NEO4J_SERVICE = settings.NEO4J_SERVICE + "/v1/neo4j/"
        settings.OPS_DB_URI = f"postgresql://{settings.RDS_USER}:{settings.RDS_PWD}@{settings.RDS_HOST}/{settings.RDS_DBNAME}"
        return settings

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        extra = Extra.allow

        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            return (
                load_vault_settings,
                env_settings,
                init_settings,
                file_secret_settings,
            )


@lru_cache(1)
def get_settings():
    settings = Settings()
    settings.modify_values(settings)
    return settings


ConfigClass = get_settings()

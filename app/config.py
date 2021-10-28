import os
import requests
from requests.models import HTTPError
# os.environ['env'] = 'test'
srv_namespace = "service_encryption"
CONFIG_CENTER = "http://10.3.7.222:5062" \
    if os.environ.get('env', "test") == "test" \
    else "http://common.utility:5062"


def vault_factory() -> dict:
    url = CONFIG_CENTER + \
        "/v1/utility/config/{}".format(srv_namespace)
    config_center_respon = requests.get(url)
    if config_center_respon.status_code != 200:
        raise HTTPError(config_center_respon.text)
    return config_center_respon.json()['result']


class ConfigClass(object):
    vault = vault_factory()
    env = os.environ.get('env')
    version = "0.1.0"
    # vault
    VAULT_SERVICE = "https://vault.vault:8200"
    VAULT_CRT = "/run/secrets/kubernetes.io/serviceaccount/ca.crt"
    VAULT_TOKEN = "s.mwDUnR2OR0smmqMnWoPZpOe9"

    # minio
    MINIO_OPENID_CLIENT = vault['MINIO_OPENID_CLIENT']
    MINIO_ENDPOINT = vault['MINIO_ENDPOINT']
    MINIO_HTTPS = False
    KEYCLOAK_URL = vault['KEYCLOAK_URL']
    MINIO_TEST_PASS = vault['MINIO_TEST_PASS']
    MINIO_ACCESS_KEY = vault['MINIO_ACCESS_KEY']
    MINIO_SECRET_KEY = vault['MINIO_SECRET_KEY']
    KEYCLOAK_VRE_SECRET = vault['KEYCLOAK_VRE_SECRET']

    NEO4J_SERVICE = vault['NEO4J_SERVICE'] + "/v1/neo4j/"

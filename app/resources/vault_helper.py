import hvac
from app.config import ConfigClass

class VaultClient(object):

    def __init__(self, jwt_token):
        vault = hvac.Client(url=ConfigClass.VAULT_SERVICE, verify=ConfigClass.VAULT_CRT)
        response = vault.auth.jwt.jwt_login(
            role="user",
            jwt=jwt_token,
        )
        self.token = response['auth']['client_token']
        self.entity_id = response['auth']['entity_id']
        self.vault = hvac.Client(url=ConfigClass.VAULT_SERVICE, verify=ConfigClass.VAULT_CRT, token=self.token)

    def get_secret(self, path):
        response = self.vault.secrets.kv.v1.read_secret(
            path=f"user_keys/{self.entity_id}/" + path, 
            mount_point=""
        )
        return response["data"]

    def create_or_update_secret(self, path, data):
        response = self.vault.secrets.kv.v1.create_or_update_secret(
            path=f"user_keys/{self.entity_id}/" + path, 
            mount_point="",
            secret=data,
        )
        return "success"

    def delete_secret(self, path, data):
        response = self.vault.secrets.kv.v1.delete_secret(
            path=f"user_keys/{self.entity_id}/" + path, 
            mount_point=""
        )
        return response["data"]


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


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

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.fernet import Fernet


class EncryptionHelper(object):

    def load_key_file(self, file_path, type):
        with open(file_path, "rb") as f:
            key = self.load_key(f.read(), type)
        return key

    def load_key(self, key, type):
        if type == "private":
            key = serialization.load_pem_private_key(
                key,
                password=None
            )
        else:
            key = serialization.load_pem_public_key(
                key,
            )
        return key

    def encrypt(self, data, file_key):
        fernet = Fernet(file_key)
        encrypted_data = fernet.encrypt(data)
        return encrypted_data

    def encrypt_key(self, public_key, file_key):
        return public_key.encrypt(
            file_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            )
        )

    def decrypt(self, data, file_key):
        fernet = Fernet(file_key)
        decrypted_data = fernet.decrypt(data)
        return decrypted_data

    def decrypt_key(self, private_key, file_key):
        return private_key.decrypt(
            file_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            )
        )

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes 
from cryptography.hazmat.primitives import serialization
from cryptography.fernet import Fernet
import os


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
                #password=bytes(self.PRIVATE_KEY_PASS, "utf-8")
            )
        else:
            key = serialization.load_pem_public_key(
                key,
                #password=bytes(PRIVATE_KEY_PASS, "utf-8")
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

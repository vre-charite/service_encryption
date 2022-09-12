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

from fastapi import APIRouter, Request
from fastapi_utils import cbv
from fastapi_sqlalchemy import db
import requests
from base64 import b64encode, b64decode
import hvac

from app.models.base_models import EAPIResponseCode
from app.config import ConfigClass
from app.models.file_key_models import POSTFileKey, POSTFileKeyResponse, GETFileKeyResponse
from app.models.user_keys_sql import UserKeyModel
from app.commons.service_connection.minio_client import Minio_Client_
from app.resources.error_handler import APIException
from app.commons.logger_services.logger_factory_service import SrvLoggerFactory
from minio.commonconfig import CopySource
from .encryption_helper import EncryptionHelper

logger = SrvLoggerFactory("api_user_keys").get_logger()

router = APIRouter()


@cbv.cbv(router)
class FileKeys:

    def get_file_by_geid(self, geid):
        try:
            response = requests.get(ConfigClass.NEO4J_SERVICE + f"nodes/geid/{geid}")
        except Exception as e:
            error_msg = str(e)
            logger.error(error_msg)
            raise APIException(status_code=500, error_msg=f"Error calling neo4j service: {error_msg}")
        if response.status_code == EAPIResponseCode.not_found.value:
            raise APIException(status_code=EAPIResponseCode.not_found.value, error_msg="File not found")
        return response.json()[0]

    def parse_location(self, path):
        protocol = "https://" if ConfigClass.MINIO_HTTPS else "http://"
        path = path.replace("minio://", "").replace(protocol, "").split("/")
        bucket = path[1]
        path = '/'.join(path[2:])
        return {"bucket": bucket, "path": path}

    def get_user_public_key(self, user_geid: str, is_sandboxed: bool) -> str:
        try:
            user_key = db.session.query(UserKeyModel).filter_by(
                user_geid=user_geid,
                is_sandboxed=is_sandboxed,
            ).first()
        except Exception as e:
            error_msg = str(e)
            logger.error(error_msg)
            raise APIException(status_code=500, error_msg=f"Error getting key from psql: {error_msg}")
        if not user_key:
            raise APIException(status_code=404, error_msg=f"User key not found")
        return user_key.public_key

    def get_server_private_key(self):
        try:
            vault = hvac.Client(
                    url=ConfigClass.ENCRYPT_VAULT_SERVICE,
                    verify=ConfigClass.ENCRYPT_VAULT_CRT,
                    token=ConfigClass.ENCRYPT_VAULT_TOKEN
            )
            response = vault.secrets.kv.v1.read_secret(
                path="server_keys/keys",
                mount_point=""
            )
            return response["data"].get("private_key")
        except Exception as e:
            error_msg = str(e)
            logger.error(error_msg)
            raise APIException(status_code=500, error_msg=f"Error getting key from vault: {error_msg}")

    @router.get("/file/{file_geid}", tags=["keys"], response_model=GETFileKeyResponse, summary="Get file key")
    def get_key(self, file_geid: str, request: Request, user_geid: str, is_sandboxed: bool = False):
        api_response = GETFileKeyResponse()
        jwt_token = request.headers.get("Authorization")
        refresh_token = request.headers.get("refresh-token")
        if not jwt_token or not refresh_token:
            api_response.error_msg = "Missing jwt_token or refresh_token"
            api_response.code = EAPIResponseCode.bad_request
            logger.info(api_response.error_msg)
            return api_response.json_response()
        jwt_token = jwt_token.replace("Bearer ", "")

        file_node = self.get_file_by_geid(file_geid)
        file_loc = file_node["location"]
        file_data = self.parse_location(file_loc)
        try:
            mc = Minio_Client_(jwt_token, refresh_token)
            response = mc.client.stat_object(
                file_data["bucket"],
                file_data["path"]
            )
        except Exception as e:
            error_msg = str(e)
            api_response.error_msg = f"Error getting minio data: {error_msg}"
            api_response.code = EAPIResponseCode.internal_error
            logger.info(api_response.error_msg)
            return api_response.json_response()
        encrypted_key = b64decode(response.metadata.get("x-amz-meta-file-key"))

        public_key = self.get_user_public_key(user_geid, is_sandboxed)

        try:
            encrypt_client = EncryptionHelper()
            private_key = self.get_server_private_key()
            private_key = encrypt_client.load_key(private_key.encode(), type="private")
            decrypted_key = encrypt_client.decrypt_key(private_key, encrypted_key)
        except Exception as e:
            api_response.error_msg = f"Encrypt/Decrypt failed: {str(e)}"
            api_response.code = EAPIResponseCode.internal_error
            logger.info(api_response.error_msg)
            return api_response.json_response()

        user_public_key = encrypt_client.load_key(public_key.encode(), type="public")
        encrypted_key = encrypt_client.encrypt_key(user_public_key, decrypted_key)

        api_response.result = b64encode(encrypted_key).decode()
        return api_response.json_response()

    @router.post("/file/{file_geid}", tags=["keys"], response_model=POSTFileKeyResponse, summary="Create file key")
    def post_key(self, file_geid: str, data: POSTFileKey, request: Request):
        api_response = POSTFileKeyResponse()
        jwt_token = request.headers.get("authorization").replace("Bearer ", "")
        refresh_token = request.headers.get("refresh-token")
        if not jwt_token or not refresh_token:
            api_response.error_msg = "Missing jwt_token or refresh_token"
            api_response.code = EAPIResponseCode.bad_request
            logger.info(api_response.error_msg)
            return api_response.json_response()

        file_node = self.get_file_by_geid(file_geid)
        file_loc = file_node["location"]
        file_data = self.parse_location(file_loc)
        try:
            mc = Minio_Client_(jwt_token, refresh_token)
            metadata = {
                "x-amz-meta-file-key": data.file_key,
            }
            # copy is needed to update the metadata
            mc.client.copy_object(
                file_data["bucket"],
                file_data["path"],
                CopySource(file_data["bucket"], file_data["path"]),
                metadata=metadata,
                metadata_directive="REPLACE",
            )
        except Exception as e:
            error_msg = str(e)
            logger.info(error_msg)
            raise APIException(status_code=500, error_msg=f"Error updating meta in minio: {error_msg}")
        return api_response.json_response()

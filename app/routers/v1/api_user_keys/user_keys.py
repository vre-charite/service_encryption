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
import hvac

from app.models.base_models import EAPIResponseCode
from app.models.user_keys_sql import UserKeyModel
from app.config import ConfigClass
from app.models.user_key_models import POSTUserKey, POSTUserKeyResponse, GETUserKeyResponse, GETServerKeyResponse
from app.commons.logger_services.logger_factory_service import SrvLoggerFactory
from app.resources.error_handler import APIException

logger = SrvLoggerFactory("api_user_keys").get_logger()

router = APIRouter()


@cbv.cbv(router)
class UserKeys:
    @router.get("/server", tags=["keys"], response_model=GETServerKeyResponse, summary="Get server public keys")
    def get_server_key(self, request: Request):
        api_response = GETServerKeyResponse()
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
        except Exception as e:
            error_msg = str(e)
            logger.error(error_msg)
            raise APIException(
                status_code=EAPIResponseCode.internal_error.value,
                error_msg=f"Error getting key from vault: {error_msg}"
            )
        api_response.result = {
            "public_key": response["data"]["public_key"]
        }
        return api_response.json_response()

    @router.get("/user", tags=["keys"], response_model=GETUserKeyResponse, summary="Get user public keys")
    def get_key(self, user_geid: str, is_sandboxed: bool, request: Request, key_name: str = "default"):
        api_response = GETUserKeyResponse()
        try:
            user_key = db.session.query(UserKeyModel).filter_by(
                user_geid=user_geid,
                is_sandboxed=is_sandboxed,
                key_name=key_name
            ).first()
        except Exception as e:
            error_msg = str(e)
            logger.error(error_msg)
            raise APIException(
                status_code=EAPIResponseCode.internal_error.value,
                error_msg=f"Error getting key from psql: {error_msg}"
            )
        if not user_key:
            api_response.code = EAPIResponseCode.not_found
            api_response.result = "Key not found"
            return api_response.json_response()
        api_response.result = user_key.to_dict()
        return api_response.json_response()

    @router.post("/user", tags=["keys"], response_model=POSTUserKeyResponse, summary="create user public keys")
    def post_key(self, data: POSTUserKey, request: Request):
        api_response = POSTUserKeyResponse()
        user_key_data = {
            "user_geid": data.user_geid,
            "public_key": data.user_public_key.strip(),
            "is_sandboxed": data.is_sandboxed,
            "key_name": data.key_name,
        }
        try:
            user_key = db.session.query(UserKeyModel).filter_by(
                user_geid=data.user_geid,
                is_sandboxed=data.is_sandboxed,
                key_name=data.key_name
            ).first()
            if user_key:
                # Overwrite existing key
                db.session.query(UserKeyModel).filter_by(
                    user_geid=data.user_geid,
                    is_sandboxed=data.is_sandboxed,
                    key_name=data.key_name
                ).update(values=user_key_data)
            else:
                # Create new key
                user_key = UserKeyModel(**user_key_data)
            db.session.add(user_key)
            db.session.commit()
            db.session.refresh(user_key)
        except Exception as e:
            error_msg = str(e)
            logger.error(error_msg)
            raise APIException(
                status_code=EAPIResponseCode.internal_error.value,
                error_msg=f"Error adding key from psql: {error_msg}"
            )
        api_response.result = user_key.to_dict()
        return api_response.json_response()

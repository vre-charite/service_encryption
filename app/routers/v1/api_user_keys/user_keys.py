from fastapi import APIRouter, Depends, Request
from fastapi_utils import cbv
import hvac

from app.models.base_models import APIResponse, EAPIResponseCode
from app.config import ConfigClass
from app.models.user_key_models import POSTUserKey, POSTUserKeyResponse, GETUserKeyResponse, GETServerKeyResponse
from app.resources.vault_helper import VaultClient
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
            vault = hvac.Client(url=ConfigClass.VAULT_SERVICE, verify=ConfigClass.VAULT_CRT, token=ConfigClass.VAULT_TOKEN)
            response = vault.secrets.kv.v1.read_secret(
                path=f"server_keys/keys", 
                mount_point=""
            )
        except Exception as e:
            error_msg = str(e)
            logger.error(error_msg)
            raise APIException(status_code=500, error_msg=f"Error getting key from vault: {error_msg}")
        api_response.result = { 
            "public_key": response["data"]["public_key"]
        }
        return api_response.json_response()

    @router.get("/user", tags=["keys"], response_model=GETUserKeyResponse, summary="Get user public keys") 
    def get_key(self, is_sandboxed: bool, request: Request):
        api_response = GETUserKeyResponse()
        jwt_token = request.headers.get("Authorization").replace("Bearer ", "")
        if not jwt_token:
            api_response.error_msg = "Missing jwt_token or refresh_token"
            api_response.code = EAPIResponseCode.bad_request
            logger.info(api_response.error_msg)
            return api_response.json_response()

        try:
            client = VaultClient(jwt_token=jwt_token)
            if is_sandboxed:
                path = "sandbox"
            else:
                path = "user"
            result = client.get_secret(f"keys/{path}")
        except Exception as e:
            error_msg = str(e)
            logger.error(error_msg)
            raise APIException(status_code=500, error_msg=f"Error getting key from vault: {error_msg}")
        api_response.result = result
        return api_response.json_response() 

    @router.post("/user", tags=["keys"], response_model=POSTUserKeyResponse, summary="create user public keys") 
    def post_key(self, data: POSTUserKey, request: Request):
        api_response = POSTUserKeyResponse()
        jwt_token = request.headers.get("Authorization").replace("Bearer ", "")
        if not jwt_token:
            api_response.error_msg = "Missing jwt_token or refresh_token"
            api_response.code = EAPIResponseCode.bad_request
            logger.info(api_response.error_msg)
            return api_response.json_response()

        try:
            client = VaultClient(jwt_token=jwt_token)
            if data.is_sandboxed:
                path = "sandbox"
            else:
                path = "user"
            key_data = {
                "public_key": data.user_public_key
            }
            client.create_or_update_secret(f"keys/{path}", key_data)
        except Exception as e:
            error_msg = str(e)
            logger.error(error_msg)
            raise APIException(status_code=500, error_msg=f"Error getting key from vault: {error_msg}")
        api_response.result = "success"
        return api_response.json_response() 

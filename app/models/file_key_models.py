from pydantic import BaseModel, Field
from .base_models import APIResponse, PaginationRequest


class POSTFileKey(BaseModel):
    file_key: str
    is_sandboxed: bool = False

class POSTFileKeyResponse(APIResponse):
    result: dict = Field({}, example={
        'code': 200,
        'error_msg': '',
        'num_of_pages': 1,
        'page': 0,
        'result': 'success',
        'total': 1
    })

class GETFileKeyResponse(APIResponse):
    result: dict = Field({}, example={
        'code': 200,
        'error_msg': '',
        'num_of_pages': 1,
        'page': 0,
        'result': {'public_key': ''},
        'total': 1
    })


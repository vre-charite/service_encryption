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

from fastapi import FastAPI
from .routers import api_root
from .routers.v1.api_user_keys import user_keys
from .routers.v1.api_file_keys import file_keys


def api_registry(app: FastAPI):
    app.include_router(api_root.router, prefix="/v1")
    app.include_router(user_keys.router, prefix="/v1/keys")
    app.include_router(file_keys.router, prefix="/v1/keys")

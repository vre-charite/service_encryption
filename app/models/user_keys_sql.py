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

from sqlalchemy import Column, String, DateTime, Integer, Boolean
from app.config import ConfigClass
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class UserKeyModel(Base):
    __tablename__ = "user_key"
    __table_args__ = {"schema": ConfigClass.RDS_SCHEMA_DEFAULT}
    id = Column(Integer, unique=True, primary_key=True)
    user_geid = Column(String())
    public_key = Column(String())
    key_name = Column(String())
    is_sandboxed = Column(Boolean())
    created_at = Column(DateTime(), default=datetime.utcnow)

    def __init__(self, user_geid, public_key, is_sandboxed, key_name="default"):
        self.user_geid = user_geid
        self.public_key = public_key
        self.is_sandboxed = is_sandboxed
        self.key_name = key_name

    def to_dict(self):
        result = {}
        for field in ["user_geid", "public_key", "is_sandboxed", "key_name", "created_at"]:
            if field == "created_at":
                result[field] = str(getattr(self, field).isoformat()[:-3] + 'Z')
            else:
                result[field] = str(getattr(self, field))
        return result

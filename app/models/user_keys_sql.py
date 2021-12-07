from fastapi_sqlalchemy import db
from sqlalchemy import Column, String, Date, DateTime, Integer, Boolean
from sqlalchemy.sql.schema import UniqueConstraint
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




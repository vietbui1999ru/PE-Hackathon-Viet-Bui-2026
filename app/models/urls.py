from datetime import datetime
from peewee import IntegerField, CharField, BooleanField, DateTimeField

from app.database import BaseModel


class Url(BaseModel):
    user_id = IntegerField()
    short_code = CharField(unique=True)
    original_url = CharField()
    title = CharField()
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    class Meta:
        table_name = "urls"

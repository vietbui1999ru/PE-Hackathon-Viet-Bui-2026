from peewee import IntegerField, CharField, DateTimeField, TextField

from app.database import BaseModel

class Event(BaseModel):
    url_id = IntegerField()
    user_id = IntegerField()
    event_type = CharField()
    timestamp = DateTimeField()
    details = TextField()

    class Meta:
        table_name = "events"

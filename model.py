from mongoengine import (
    Document,
    StringField
)


class Log(Document):
    """Example MongoDB document for log message
    """
    message_id = StringField()
    text = StringField()

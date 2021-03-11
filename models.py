from mongoengine import (
    Document,
    StringField,
    IntField,
    BooleanField,
    BinaryField,
    DictField,
    ObjectIdField,
    ListField, 
    EmbeddedDocumentField,
    EmbeddedDocument
)



class MyTweets(Document):
    text = StringField(required=True)
    language = StringField()
    favorite_count = IntField()
    created_at = StringField(required=True)
    username = StringField(required=True)

class RedditPost(Document):
    text = StringField(required=True)
    title = StringField(required=True)
    num_comments = IntField()
    created_utc = StringField(required=True)
    author = StringField(required=True)
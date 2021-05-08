from mongoengine import EmbeddedDocument, StringField, ListField, FloatField, EmbeddedDocumentListField
import uuid
from settings import initial_settings as init


class Operation(EmbeddedDocument):
    public_id = StringField(required=True, default=None)
    name = StringField(required=True, default=None, choices=tuple(init.AVAILABLE_OPERATIONS))
    type = StringField(required=True)
    operator_ids = ListField(StringField(), default=[], required=True)

    def __init__(self, *args, **values):
        super().__init__(*args, **values)

        if self.public_id is None:
            self.public_id = str(uuid.uuid4())

    def to_dict(self):
        return dict(public_id=self.public_id, type=self.type, name=self.name,
                    operator_ids=self.operator_ids)

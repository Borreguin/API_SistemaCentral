from mongoengine import EmbeddedDocument, StringField, ListField, FloatField, EmbeddedDocumentListField

from settings import initial_settings as init


class Operation(EmbeddedDocument):
    public_id = StringField(required=True, default=None)
    name = StringField(required=True, default=None, choices=tuple(init.AVAILABLE_OPERATIONS))
    type = StringField(required=True)
    operator_ids = ListField(StringField(), default=[], required=True)
    position_x_y = ListField(FloatField(), default=lambda: [0.0, 0.0])
    operations = EmbeddedDocumentListField('Operation')

    def to_dict(self):
        return dict(public_id=self.public_id, type=self.type, name=self.name,
                    operator_ids=self.operator_ids, position_x_y=self.position_x_y,
                    operations=[op.to_dict() for op in self.operations])
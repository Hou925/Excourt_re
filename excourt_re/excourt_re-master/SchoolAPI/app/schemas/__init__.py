from marshmallow import Schema, fields


class StudentSchema(Schema):
    Student_id = fields.Str(required=True)
    Student_name = fields.Str(required=True)
    Student_phone = fields.Str(required=True)
    Student_password = fields.Str(required=True)


class VerifySchema(Schema):
    Student_id = fields.Str(required=True)
    Student_name = fields.Str(required=True)
    Student_password = fields.Str(required=True)

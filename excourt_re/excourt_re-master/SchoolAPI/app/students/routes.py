from flask import jsonify, request
from marshmallow import ValidationError

from app.dal.repository import (
    StudentExistsError,
    add_student,
    get_all_students,
    verify_student,
)
from app.schemas import StudentSchema, VerifySchema
from app.students import bp


@bp.route("/", methods=["GET"])
def get_students():
    students = get_all_students()
    return jsonify(students)


@bp.route("/", methods=["POST"])
def create_student():
    try:
        schema = StudentSchema()
        data = schema.load(request.get_json())

        add_student(
            student_id=data["Student_id"],
            student_name=data["Student_name"],
            student_phone=data["Student_phone"],
            student_password=data["Student_password"],
        )
        return jsonify({"message": "Student added successfully"}), 201
    except ValidationError as e:
        return jsonify({"message": "Validation error", "errors": e.messages}), 400
    except StudentExistsError as e:
        return jsonify({"message": str(e)}), 409
    except Exception as e:
        return jsonify({"message": "Internal server error"}), 500


@bp.route("/verify", methods=["POST"])
def verify_student_route():
    try:
        schema = VerifySchema()
        data = schema.load(request.get_json())

        if verify_student(
            data["Student_id"], data["Student_name"], data["Student_password"]
        ):
            return jsonify({"message": "Record found", "status": "success"}), 200
        else:
            return (
                jsonify({"message": "No matching record found", "status": "failure"}),
                404,
            )
    except ValidationError as e:
        return jsonify({"message": "Validation error", "errors": e.messages}), 400
    except Exception as e:
        return jsonify({"message": "Internal server error"}), 500

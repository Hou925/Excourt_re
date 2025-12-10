from typing import Any, Dict, List, Optional

from flask import current_app
from psycopg2 import errors

from app.db import get_db_cursor


class StudentExistsError(Exception):
    pass


def get_all_students() -> List[Dict[str, Any]]:
    with get_db_cursor() as cur:
        cur.execute("SELECT * FROM Student")
        students = cur.fetchall()
        return [
            {
                "Student_id": student[0],
                "Student_name": student[1],
                "Student_phone": student[2],
            }
            for student in students
        ]


def add_student(
    student_id: str, student_name: str, student_phone: str, student_password: str
) -> None:
    try:
        with get_db_cursor() as cur:
            cur.execute(
                "INSERT INTO Student (Student_id, Student_name, Student_phone, Student_password) VALUES (%s, %s, %s, %s)",
                (student_id, student_name, student_phone, student_password),
            )
    except errors.UniqueViolation:
        current_app.logger.warning(
            f"Attempt to add student with existing ID: {student_id}"
        )
        raise StudentExistsError(f"Student with ID {student_id} already exists")
    except Exception as e:
        current_app.logger.error(f"Error adding student: {e}")
        raise


def verify_student(student_id: str, student_name: str, student_password: str) -> bool:
    with get_db_cursor() as cur:
        query = """
            SELECT * FROM Student
            WHERE Student_id = %s AND Student_name = %s AND Student_password = %s
        """
        cur.execute(query, (student_id, student_name, student_password))
        return cur.fetchone() is not None


def get_court_by_id(court_id: str) -> Optional[Dict[str, Any]]:
    with get_db_cursor() as cur:
        cur.execute("SELECT * FROM CourtInfo WHERE Court_id = %s", (court_id,))
        court = cur.fetchone()
        if court:
            return {
                "Court_id": court[0],
                "Court_campus": court[1],
                "Court_date": court[2].isoformat(),
                "Court_time": court[3],
                "Court_no": court[4],
                "Court_state": court[5],
                "Court_owner": court[6],
                "Court_qrcodeurl": court[7],
            }
        return None
    
def update_court_owner(court_id: str, new_owner_id: int) -> None:
    with get_db_cursor() as cur:
        cur.execute(
            "UPDATE courtinfo SET court_owner = %s WHERE court_id = %s",
            (new_owner_id, court_id)
        )

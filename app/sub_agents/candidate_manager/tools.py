from typeguard import typechecked
from typing import Any, Dict
import logging
import psycopg2
import google.auth
from app.utils import secrets
from app.utils import bd


class CandidateManagerTools:
    """Tools for the Candidate Manager Agent."""

    def __init__(self):
        try:
            _, project_id = google.auth.default()
        except google.auth.exceptions.DefaultCredentialsError:
            error_message = "Google Application Default Credentials not found. Please set the GOOGLE_APPLICATION_CREDENTIALS environment variable."
            logging.error(error_message)
            raise RuntimeError(error_message)

        self.db_params = {
            "host": secrets.get_secret(project_id, "hero-cloudsql-host"),
            "port": secrets.get_secret(project_id, "hero-cloudsql-port"),
            "dbname": secrets.get_secret(project_id, "hero-cloudsql-db-name"),
            "user": secrets.get_secret(project_id, "hero-cloudsql-user"),
            "password": secrets.get_secret(project_id, "hero-cloudsql-password"),
        }

    @typechecked
    def add_candidate(self, candidate_name: str, candidate_email: str, candidate_content: str) -> Dict[str, Any]:
        """Adds a new candidate to the database.

        Args:
            candidate_name (str): The candidate name of the CV.
            candidate_email (str): The candidate email of the CV.
            candidate_content (str): The content of the CV.

        Returns:
            Dict[str, Any]: A dictionary containing the status of the operation, the candidate name, the candidate email, and the CV content.
        """

        try:
            with bd.get_connection(db_params=self.db_params) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT email FROM human_resources.candidates WHERE LOWER(email) = LOWER(%s);",
                        (candidate_email,),
                    )
                    email_exists = cur.fetchone()
                    conn.commit()
                    if email_exists:
                        cur.execute(
                            "UPDATE human_resources.candidates SET content = %s WHERE LOWER(email) = LOWER(%s) RETURNING name, email, content;",
                            (
                                candidate_content,
                                candidate_email,
                            ),
                        )
                    else:
                        cur.execute(
                            "INSERT INTO human_resources.candidates (name, email, content) VALUES (%s, %s, %s) RETURNING name, email, content;",
                            (
                                candidate_name,
                                candidate_email,
                                candidate_content,
                            ),
                        )
                    cv = cur.fetchone()
                    conn.commit()
                    return {"status": "success", "candidate_name": cv[0], "candidate_email": cv[1], "cv_content": cv[2]}
        except psycopg2.IntegrityError:
            error_message = "A CV with this candidate name and candidate email already exists."
            logging.error(error_message)
            return {"status": "error", "message": error_message}
        except Exception as e:
            error_message = f"Error adding candidate: {e}"
            logging.error(error_message)
            return {"status": "error", "message": error_message}

    @typechecked
    def get_candidates(self) -> Dict[str, Any]:
        """Get all the candidates.

        Returns:
            Dict[str, Any]: A dictionary containing the status of the operation and a list of candidates, where each candidate has a name, email, and CV content.
        """

        try:
            with bd.get_connection(db_params=self.db_params) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT name, email, content FROM human_resources.candidates;")
                    rows = cur.fetchall()
                    if not rows:
                        return {"status": "warning", "message": "No candidates found."}
                    candidates = [{"candidate_name": row[0], "candidate_email": row[1], "cv_content": row[2]} for row in rows]
                    return {"status": "success", "candidates": candidates}
        except Exception as e:
            error_message = f"Error retrieving candidates: {e}"
            logging.error(error_message)
            return {"status": "error", "message": error_message}

    @typechecked
    def delete_all_candidates(self) -> Dict[str, Any]:
        """Deletes all candidates from the database.

        Returns:
            Dict[str, Any]: A dictionary containing the status of the operation and the number of deleted candidates.
        """

        try:
            with bd.get_connection(db_params=self.db_params) as conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM human_resources.candidates RETURNING name, email, content;")
                    deleted_rows = cur.fetchall()
                    conn.commit()
                    return {"status": "success", "deleted_count": len(deleted_rows)}
        except Exception as e:
            error_message = f"Error deleting candidates: {e}"
            logging.error(error_message)
            return {"status": "error", "message": error_message}

    @typechecked
    def delete_candidate_by_name(self, candidate_name: str) -> Dict[str, Any]:
        """Deletes a candidate from the database using the candidate name.

        Args:
            candidate_name (str): The candidate name of the CV.

        Returns:
            Dict[str, Any]: A dictionary containing the status of the operation, the candidate name, the candidate email, and the CV content.
        """

        try:
            with bd.get_connection(db_params=self.db_params) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT name FROM human_resources.candidates WHERE LOWER(name) LIKE LOWER(%s) OR LOWER(name) LIKE LOWER(%s) OR LOWER(name) LIKE LOWER(%s);",
                        (
                            f"%{candidate_name}%",
                            f"%{candidate_name}",
                            f"{candidate_name}%",
                        ),
                    )
                    rows = cur.fetchall()

                    if not rows:
                        return {"status": "warning", "message": "No candidates found."}
                    elif len(rows) > 1:
                        return {"status": "warning", "message": "Multiple candidates found. Full name or email required."}

                    cur.execute(
                        "DELETE FROM human_resources.candidates WHERE LOWER(name) = LOWER(%s) RETURNING name, email, content;",
                        (candidate_name,),
                    )
                    cv = cur.fetchone()
                    conn.commit()
                    return {"status": "success", "candidate_name": cv[0], "candidate_email": cv[1], "cv_content": cv[2]}
        except psycopg2.IntegrityError:
            error_message = "A CV with this candidate name already exists."
            logging.error(error_message)
            return {"status": "error", "message": error_message}
        except Exception as e:
            error_message = f"Error deleting candidate: {e}"
            logging.error(error_message)
            return {"status": "error", "message": error_message}

    @typechecked
    def delete_candidate_by_email(self, candidate_email: str) -> Dict[str, Any]:
        """Deletes a candidate from the database using the candidate email.

        Args:
            candidate_email (str): The candidate email of the CV.

        Returns:
            Dict[str, Any]: A dictionary containing the status of the operation, the candidate name, the candidate email, and the CV content.
        """

        try:
            with bd.get_connection(db_params=self.db_params) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "DELETE FROM human_resources.candidates WHERE LOWER(email) = LOWER(%s) RETURNING name, email, content;",
                        (candidate_email,),
                    )
                    cv = cur.fetchone()
                    conn.commit()
                    return {"status": "success", "candidate_name": cv[0], "candidate_email": cv[1], "cv_content": cv[2]}
        except psycopg2.IntegrityError:
            error_message = "A CV with this candidate email already exists."
            logging.error(error_message)
            return {"status": "error", "message": error_message}
        except Exception as e:
            error_message = f"Error deleting candidate: {e}"
            logging.error(error_message)
            return {"status": "error", "message": error_message}

    @typechecked
    def get_candidate_by_name(self, candidate_name: str) -> Dict[str, Any]:
        """Retrieves a candidate from the database using the candidate name.

        Args:
            candidate_name (str): The candidate name of the CV.

        Returns:
            Dict[str, Any]: A dictionary containing the status of the operation, the candidate name, the candidate email, and the CV content.
        """

        try:
            with bd.get_connection(db_params=self.db_params) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT name, email, content FROM human_resources.candidates WHERE LOWER(name) LIKE LOWER(%s) OR LOWER(name) LIKE LOWER(%s) OR LOWER(name) LIKE LOWER(%s);",
                        (
                            f"%{candidate_name}%",
                            f"%{candidate_name}",
                            f"{candidate_name}%",
                        ),
                    )
                    rows = cur.fetchall()

                    if not rows:
                        return {"status": "warning", "message": "Candidate not found."}
                    elif len(rows) > 1:
                        return {"status": "warning", "message": "Multiple CVs found. Full name or email required."}

                    candidate = rows[0]
                    return {"status": "success", "candidate_name": candidate[0], "candidate_email": candidate[1], "cv_content": candidate[2]}
        except Exception as e:
            error_message = f"Error retrieving candidate: {e}"
            logging.error(error_message)
            return {"status": "error", "message": error_message}

    @typechecked
    def get_candidate_by_email(self, candidate_email: str) -> Dict[str, Any]:
        """Retrieves a candidate from the database using the candidate email.

        Args:
            candidate_email: (str): The candidate email of the CV.

        Returns:
            Dict[str, Any]: A dictionary containing the status of the operation, the candidate name, the candidate email, and the CV content.
        """

        try:
            with bd.get_connection(db_params=self.db_params) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT name, email, content FROM human_resources.candidates WHERE LOWER(email) = LOWER(%s);",
                        (candidate_email,),
                    )
                    row = cur.fetchone()
                    if not row:
                        return {"status": "warning", "message": "CV not found."}
                    return {"status": "success", "candidate_name": row[0], "candidate_email": row[1], "cv_content": row[2]}
        except Exception as e:
            error_message = f"Error retrieving candidate: {e}"
            logging.error(error_message)
            return {"status": "error", "message": str(e)}


candidate_manager_tools = CandidateManagerTools()

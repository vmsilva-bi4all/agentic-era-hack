import os
import psycopg2
from typing import Any, Dict, List

class CandidateManagerTools:
    """Tools for the Candidate Manager Agent."""

    def __init__(self):
        try:
            _, project_id = google.auth.default()
        except google.auth.exceptions.DefaultCredentialsError:
            project_id = None

        self.db_params = {
            "host": self._get_secret(project_id, "hero-cloudsql-host"),
            "port": self._get_secret(project_id, "hero-cloudsql-port"),
            "dbname": self._get_secret(project_id, "hero-cloudsql-dbname"),
            "user": self._get_secret(project_id, "hero-cloudsql-user"),
            "password": self._get_secret(project_id, "hero-cloudsql-password"),
        }

    def _get_secret(self, project_id: str, secret_id: str, version_id: str = "latest") -> str:
        """Retrieves a secret from Google Cloud Secret Manager."""
        try:
            client = secretmanager.SecretManagerServiceClient()
            name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
            response = client.access_secret_version(name=name)
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            # Handle exceptions (e.g., secret not found, permission errors)
            print(f"Error accessing secret {secret_id}: {e}")
            return None

    def _get_connection(self):
        return psycopg2.connect(**self.db_params)

    def add_cv(self, candidate_name: str, candidate_email: str, candidate_content: str) -> Dict[str, Any]:
        """Adds a new CV to the database.
        
        Args:
            candidate_name (str): The candidate name of the CV.
            candidate_email (str): The candidate email of the CV.
            candidate_content (str): The content of the CV.
        
        Returns:
            Dict[str, Any]: A dictionary containing the status of the operation, the candidate name, the candidate email, and the CV content.
        """

        try:
            with self._get_connection() as conn:
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
                            (candidate_content, candidate_email),
                        )
                    else:
                        cur.execute(
                            "INSERT INTO human_resources.candidates (name, email, content) VALUES (%s, %s, %s) RETURNING name, email, content;",
                            (candidate_name, candidate_email, candidate_content),
                        )
                    cv = cur.fetchone()
                    conn.commit()
                    return {"status": "success", "candidate name": cv[0], "candidate email": cv[1], "cv content": cv[2]}
        except psycopg2.IntegrityError:
            return {"status": "error", "message": "A CV with this candidate name and candidate email already exists."}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_candidates(self) -> Dict[str, Any]:
        """Get all the candidates.

        Returns:
            Dict[str, Any]: A dictionary containing the status of the operation and a list of candidates, where each candidate has a name, email, and CV content.
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT name, email, content FROM human_resources.candidates;")
                    rows = cur.fetchall()

                    if not rows:
                        return {"status": "error", "message": "No candidates found."}

                    candidates: List[Dict[str, str]] = [
                        {"candidate name": row[0], "candidate email": row[1], "cv content": row[2]}
                        for row in rows
                    ]

                    return {"status": "success", "candidates": candidates}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_cv_by_candidate_name_and_email(self, candidate_name: str, candidate_email: str) -> Dict[str, Any]:
        """Retrieves a CV from the database using the candidate name and email.
        
        Args:
            candidate_name: (str): The candidate name of the CV.
            candidate_email: (str): The candidate email of the CV.
        
        Returns:
            Dict[str, Any]: A dictionary containing the status of the operation, the candidate name, the candidate email, and the CV content.
        """

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                        cur.execute(
                            "SELECT name, email, content FROM human_resources.candidates WHERE LOWER(name) = LOWER(%s) AND LOWER(email) = LOWER(%s);",
                            (candidate_name, candidate_email),
                        )
                        cv = cur.fetchone()
                        conn.commit()
                        if cv is None:
                            return {"status": "error", "message": "CV not found."}
                        return {"status": "success", "candidate name": cv[0], "candidate email": cv[1], "cv content": cv[2]}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_cv_by_candidate_name(self, candidate_name: str) -> Dict[str, Any]:
        """Retrieves a CV from the database using the candidate name.
        
        Args:
            candidate_name: (str): The candidate name of the CV.
        
        Returns:
            Dict[str, Any]: A dictionary containing the status of the operation, the candidate name, the candidate email, and the CV content.
        """

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                        cur.execute(
                            "SELECT name, email, content FROM human_resources.candidates WHERE LOWER(name) = LOWER(%s);",
                            (candidate_name,),
                        )
                        cv = cur.fetchone()
                        conn.commit()
                        if cv is None:
                            return {"status": "error", "message": "CV not found."}
                        return {"status": "success", "candidate name": cv[0], "candidate email": cv[1], "cv content": cv[2]}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_cv_by_candidate_email(self, candidate_email: str) -> Dict[str, Any]:
        """Retrieves a CV from the database using the candidate email.
        
        Args:
            candidate_email: (str): The candidate email of the CV.
        
        Returns:
            Dict[str, Any]: A dictionary containing the status of the operation, the candidate name, the candidate email, and the CV content.
        """

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT name, email, content FROM human_resources.candidates WHERE LOWER(email) = LOWER(%s);",
                        (candidate_email,),
                    )
                    cv = cur.fetchone()
                    conn.commit()
                    if cv is None:
                        return {"status": "error", "message": "CV not found."}
                    return {"status": "success", "candidate name": cv[0], "candidate email": cv[1], "candidate content": cv[2]}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_cv_by_id(self, cv_id: int) -> Dict[str, str]:
        """Retrieves a CV from the database by its ID.
        
        Args:
            cv_id (int): The ID of the CV.
        
        Returns:
            Dict[str, str]: A dictionary containing the CV.
        """

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT name, email, content FROM human_resources.candidates WHERE id = %s;",
                        (cv_id,),
                    )
                    cv = cur.fetchone()
                    conn.commit()
                    if cv is None:
                        return {"status": "error", "message": "CV not found."}
                    return {"status": "success", "name": cv[0], "email": cv[1], "content": cv[2]}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def list_job_offers(self) -> Dict[str, Union[str, List[Dict[str, str]]]]:
        """Retrieves a list of job offers from the database.
        
        Returns:
            Dict[str, Union[str, List[Dict[str, str]]]]: A dictionary containing the list of job offers.
        """

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT title, description FROM human_resources.job_offerings;")
                    job_offers = cur.fetchall()
                    conn.commit()
                    return {"status": "success", "job_offers": [{"title": row[0], "description": row[1]} for row in job_offers]}
        except Exception as e:
            return {"status": "error", "message": str(e)}

candidate_manager_tools = CandidateManagerTools()

import os
import psycopg2
from typing import Union, Dict, List
from google.cloud import secretmanager
import google.auth

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
            "dbname": "postgres",
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

    def add_cv(self, name: str, email: str, content: str) -> Dict[str, str]:
        """Adds a new CV to the database.
        
        Args:
            name (str): The name of the CV.
            email (str): The email of the CV.
            content (str): The content of the CV.
        
        Returns:
            Dict[str, str]: A dictionary containing the status of the operation.
        """

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO human_resources.candidates (name, email, content) VALUES (%s, %s, %s) RETURNING name, email, content;",
                        (name, email, content),
                    )
                    cv = cur.fetchone()
                    conn.commit()
                    return {"status": "success", "name": cv[0], "email": cv[1], "content": cv[2]}
        except psycopg2.IntegrityError:
            return {"status": "error", "message": "A CV with this name and email already exists."}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_cv(self, name: Union[None, str] = None, email: Union[None, str] = None) -> Dict[str, str]:
        """Retrieves a CV from the database.
        
        Args:
            name: (Union[None, str]): The name of the CV.
            email: (Union[None, str]): The email of the CV.
        
        Returns:
            Dict[str, str]: A dictionary containing the CV.
        """

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    if name and email:
                        cur.execute(
                            "SELECT name, email, content FROM human_resources.candidates WHERE name = %s AND email = %s;",
                            (name, email),
                        )
                    elif email:
                        cur.execute(
                            "SELECT name, email, content FROM human_resources.candidates WHERE email = %s;",
                            (email),
                        )
                    elif name:
                        cur.execute(
                            "SELECT name, email, content FROM human_resources.candidates WHERE name = %s;",
                            (name),
                        )
                    else:
                        return {"status": "error", "message": "No name or email provided."}
                    cv = cur.fetchone()
                    conn.commit()
                    if cv is None:
                        return {"status": "error", "message": "CV not found."}
                    return {"status": "success", "name": cv[0], "email": cv[1], "content": cv[2]}
        except Exception as e:
            return {"status": "error", "message": str(e)}

candidate_manager_tools = CandidateManagerTools()
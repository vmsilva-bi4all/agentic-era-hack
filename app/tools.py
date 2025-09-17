import os
import psycopg2
from typing import Dict, Any, List
from google.cloud import secretmanager
import google.auth

class DatabaseTools:
    """Tools for interacting with the HR database."""

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

    def add_cv(self, name: str, email: str, cv_text: str) -> Dict[str, Any]:
        """Adds a new CV to the database."""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO human_resources.candidates (name, email, cv_text) VALUES (%s, %s, %s) RETURNING id;",
                        (name, email, cv_text),
                    )
                    cv_id = cur.fetchone()[0]
                    conn.commit()
                    return {"status": "success", "id": cv_id}
        except psycopg2.IntegrityError:
            return {"status": "error", "message": "A CV with this email already exists."}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    
    def add_job_offer(self, title: str, description: str) -> Dict[str, Any]:
        """Adds a new job offer to the database."""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO job_offers (title, description) VALUES (%s, %s) RETURNING id;",
                        (title, description),
                    )
                    job_id = cur.fetchone()[0]
                    conn.commit()
                    return {"status": "success", "id": job_id}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    
    def get_cv_by_id(self, cv_id: int) -> Dict[str, Any]:
        """Retrieves a specific CV by its ID."""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT id, name, email, cv_text FROM human_resources.candidates WHERE id = %s;", (cv_id,))
                    cv = cur.fetchone()
                    if cv:
                        return {"id": cv[0], "name": cv[1], "email": cv[2], "cv_text": cv[3]}
                    return {"status": "error", "message": "CV not found."}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    
    def list_job_offers(self) -> List[Dict[str, Any]]:
        """Lists all available job offers."""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT id, title, description FROM job_offers;")
                    offers = cur.fetchall()
                    return [
                        {"id": offer[0], "title": offer[1], "description": offer[2]}
                        for offer in offers
                    ]
        except Exception as e:
            return {"status": "error", "message": str(e)}

db_tools = DatabaseTools()
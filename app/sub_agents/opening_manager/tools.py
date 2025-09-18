import os
import psycopg2
from typing import Union, Dict, List
from google.cloud import secretmanager
import google.auth


class OpeningsManagerTools:
    """Tools for the Openings Manager Agent."""

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

    def add_opening(self, name: str, job_description: str, evaluation_criteria: str) -> Dict[str, str]:
        """Adds a new job opening to the database.

        Args:
            name (str): The name of the job opening.
            job_description (str): The description of the job opening.
            evaluation_criteria (str): The evaluation criteria for the job opening, which corresponds to the job requirements.

        Returns:
            Dict[str, str]: A dictionary containing the status of the operation.
        """

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO human_resources.openings (name, job_description, evaluation_criteria) VALUES (%s, %s, %s) RETURNING id, name, job_description, evaluation_criteria;",
                        (name, job_description, evaluation_criteria),
                    )
                    opening = cur.fetchone()
                    conn.commit()
                    return {
                        "status": "success",
                        "id": opening[0],
                        "name": opening[1],
                        "job_description": opening[2],
                        "evaluation_criteria": opening[3],
                    }
        except psycopg2.IntegrityError:
            return {"status": "error", "message": "A job opening with this name already exists."}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_job_opening(self, name: Union[None, str] = None) -> Dict[str, str]:
        """Retrieves a job opening from the database.

        Args:
            name: (Union[None, str]): The name of the job opening.

        Returns:
            Dict[str, str]: A dictionary containing the job opening.
        """

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    if name:
                        cur.execute(
                            "SELECT id, name, job_description, evaluation_criteria, created_at, updated_at FROM human_resources.openings WHERE name = %s;",
                            (name,),
                        )
                    else:
                        return {"status": "error", "message": "No name provided."}
                    opening = cur.fetchone()
                    conn.commit()
                    if opening is None:
                        return {"status": "error", "message": "Job opening not found."}
                    return {
                        "status": "success",
                        "id": opening[0],
                        "name": opening[1],
                        "job_description": opening[2],
                        "evaluation_criteria": opening[3],
                        "created_at": opening[4],
                        "updated_at": opening[5],
                    }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def list_openings(self) -> List[Dict[str, str]]:
        """Lists all job openings in the database.

        Returns:
            List[Dict[str, str]]: A list of dictionaries, each containing a job opening.
        """

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT id, name, job_description, evaluation_criteria, created_at, updated_at FROM human_resources.openings;")
                    openings = cur.fetchall()
                    conn.commit()
                    return [
                        {
                            "id": opening[0],
                            "name": opening[1],
                            "job_description": opening[2],
                            "evaluation_criteria": opening[3],
                            "created_at": opening[4],
                            "updated_at": opening[5],
                        }
                        for opening in openings
                    ]
        except Exception as e:
            return [{"status": "error", "message": str(e)}]

    def delete_opening(self, id: int) -> Dict[str, str]:
        """Deletes a job opening from the database.

        Args:
            id (int): The ID of the job opening to delete.

        Returns:
            Dict[str, str]: A dictionary containing the status of the deletion.
        """

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM human_resources.openings WHERE id = %s;", (id,))
                    conn.commit()
                    return {"status": "success", "message": "Job opening deleted successfully."}
        except Exception as e:
            return {"status": "error", "message": str(e)}


openings_manager_tools = OpeningsManagerTools()

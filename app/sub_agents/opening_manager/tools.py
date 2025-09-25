from typeguard import typechecked
from typing import Union, Dict, Any
import logging
import psycopg2
import google.auth
from app.utils import secrets
from app.utils import bd


class OpeningsManagerTools:
    """Tools for the Openings Manager Agent."""

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
            with bd.get_connection(db_params=self.db_params) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT name FROM human_resources.openings WHERE LOWER(name) = LOWER(%s);",
                        (name,),
                    )
                    name_exists = cur.fetchone()
                    conn.commit()
                    if name_exists:
                        cur.execute(
                            "UPDATE human_resources.openings SET job_description = %s, evaluation_criteria = %s WHERE LOWER(name) = LOWER(%s) RETURNING name, job_description, evaluation_criteria;",
                            (job_description, evaluation_criteria, name,),
                        )
                    else:
                        cur.execute(
                            "INSERT INTO human_resources.openings (name, job_description, evaluation_criteria) VALUES (%s, %s, %s) RETURNING name, job_description, evaluation_criteria;",
                            (name, job_description, evaluation_criteria),
                        )
                    opening = cur.fetchone()
                    conn.commit()
                    return {
                        "status": "success",
                        "name": opening[0],
                        "job_description": opening[1],
                        "evaluation_criteria": opening[2],
                    }
        except psycopg2.IntegrityError:
            error_message = "A job opening with this name already exists."
            logging.error(error_message)
            return {"status": "error", "message": error_message}
        except Exception as e:
            error_message = f"Error adding job opening: {e}"
            logging.error(error_message)
            return {"status": "error", "message": error_message}

    @typechecked
    def get_openings(self) -> Dict[str, Any]:
        """Lists all job openings in the database.

        Returns:
            Dict[str, Any]: A dictionary containing the status of the operation and a list of job openings.
        """

        try:
            with bd.get_connection(db_params=self.db_params) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT name, job_description, evaluation_criteria FROM human_resources.openings;")
                    openings = cur.fetchall()

                    if not openings:
                        return {"status": "warning", "message": "No job openings found."}

                    jobs = [
                        {
                            "name": opening[0],
                            "job_description": opening[1],
                            "evaluation_criteria": opening[2],
                        }
                        for opening in openings
                    ]

                    return {"status": "success", "openings": jobs}
        except Exception as e:
            error_message = f"Error listing job openings: {e}"
            logging.error(error_message)
            return {"status": "error", "message": error_message}

    @typechecked
    def delete_all_openings(self) -> Dict[str, str]:
        """Deletes all job openings from the database.

        Returns:
            Dict[str, str]: A dictionary containing the status of the deletion.
        """

        try:
            with bd.get_connection(db_params=self.db_params) as conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM human_resources.openings RETURNING name;")
                    deleted_openings = cur.fetchall()
                    conn.commit()

                    if not deleted_openings:
                        return {"status": "warning", "message": "No job openings to delete."}

                    deleted_names = [opening[0] for opening in deleted_openings]
                    return {"status": "success", "deleted_openings": deleted_names}
        except Exception as e:
            error_message = f"Error deleting all job openings: {e}"
            logging.error(error_message)
            return {"status": "error", "message": error_message}

    @typechecked
    def delete_opening(self, name: str) -> Dict[str, str]:
        """Deletes a job opening from the database.

        Args:
            name (str): The name of the job opening to delete.

        Returns:
            Dict[str, str]: A dictionary containing the status of the deletion.
        """

        try:
            with bd.get_connection(db_params=self.db_params) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT name FROM human_resources.openings WHERE LOWER(name) LIKE LOWER(%s) OR LOWER(name) LIKE LOWER(%s) OR LOWER(name) LIKE LOWER(%s);",
                        (
                            f"%{name}%",
                            f"%{name}",
                            f"{name}%",
                        ),
                    )
                    rows = cur.fetchall()

                    if not rows:
                        return {"status": "warning", "message": "No job openings found."}
                    elif len(rows) > 1:
                        return {"status": "warning", "message": "Multiple job openings found. Full name required."}

                    cur.execute(
                        "DELETE FROM human_resources.openings WHERE LOWER(name) = LOWER(%s) RETURNING name, job_description, evaluation_criteria;",
                        (name,),
                    )
                    opening = cur.fetchone()
                    conn.commit()
                    return {"status": "success", "name": opening[0], "job_description": opening[1], "evaluation_criteria": opening[2]}
        except Exception as e:
            error_message = f"Error deleting job opening: {e}"
            logging.error(error_message)
            return {"status": "error", "message": error_message}

    @typechecked
    def get_job_opening(self, name: Union[None, str] = None) -> Dict[str, Any]:
        """Retrieves a job opening from the database.

        Args:
            name: (Union[None, str]): The name of the job opening.

        Returns:
            Dict[str, Any]: A dictionary containing the job opening.
        """

        try:
            with bd.get_connection(db_params=self.db_params) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT name, job_description, evaluation_criteria FROM human_resources.openings WHERE LOWER(name) LIKE LOWER(%s) OR LOWER(name) LIKE LOWER(%s) OR LOWER(name) LIKE LOWER(%s);",
                        (
                            f"%{name}%",
                            f"%{name}",
                            f"{name}%",
                        ),
                    )
                    rows = cur.fetchall()

                    if not rows:
                        return {"status": "warning", "message": "Job opening not found."}
                    elif len(rows) > 1:
                        return {"status": "warning", "message": "Multiple job openings found. Full name required."}

                    opening = rows[0]
                    return {"status": "success", "name": opening[0], "job_description": opening[1], "evaluation_criteria": opening[2]}
        except Exception as e:
            error_message = f"Error retrieving job opening: {e}"
            logging.error(error_message)
            return {"status": "error", "message": error_message}


openings_manager_tools = OpeningsManagerTools()

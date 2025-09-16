import os
import psycopg2
from typing import Dict, Any, List

class DatabaseTools:
    """Tools for interacting with the HR database."""

    def __init__(self):
        self.db_params = {
            "host": os.environ.get("DB_HOST"),
            "dbname": os.environ.get("DB_NAME"),
            "user": os.environ.get("DB_USER"),
            "password": os.environ.get("DB_PASSWORD"),
        }

    def _get_connection(self):
        return psycopg2.connect(**self.db_params)

    def add_cv(self, name: str, email: str, content: str) -> Dict[str, Any]:
        """Adds a new CV to the database."""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO cvs (name, email, content) VALUES (%s, %s, %s) RETURNING id;",
                        (name, email, content),
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
                    cur.execute("SELECT id, name, email, content FROM cvs WHERE id = %s;", (cv_id,))
                    cv = cur.fetchone()
                    if cv:
                        return {"id": cv[0], "name": cv[1], "email": cv[2], "content": cv[3]}
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
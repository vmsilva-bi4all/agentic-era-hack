from __future__ import annotations
import os
import psycopg2
from typing import Any, Dict, List

class EvaluatorTools:
    """Tools for the Evaluator Agent."""

    def __init__(self):
        self.project_id = "qwiklabs-gcp-04-6db254dd6d5c"
        self.db_params = {
            "host": self._get_secret("hero-cloudsql-host"),
            "port": self._get_secret("hero-cloudsql-port"),
            "dbname": self._get_secret("hero-cloudsql-dbname"),
            "user": self._get_secret("hero-cloudsql-user"),
            "password": self._get_secret("hero-cloudsql-password"),
        }

    def _get_secret(self, secret_id: str, version_id: str = "latest") -> str:
        """Retrieves a secret from Google Secret Manager."""
        try:
            from google.cloud import secretmanager
            from google.api_core import exceptions
        except ImportError:
            raise ImportError(
                "google-cloud-secret-manager is required to fetch secrets."
            )
        try:
            client = secretmanager.SecretManagerServiceClient()
            name = (
                f"projects/{self.project_id}/secrets/{secret_id}/versions/{version_id}"
            )
            response = client.access_secret_version(name=name)
            return response.payload.data.decode("UTF-8")
        except exceptions.NotFound:
            print(f"Secret '{secret_id}' not found.")
            return None
        except Exception as e:
            print(f"Error accessing secret '{secret_id}': {e}")
            return None

    def _get_connection(self):
        return psycopg2.connect(**self.db_params)

    def get_all_candidates(self) -> Dict[str, Any]:
        """Retrieves all candidates from the database."""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT name, cv_text FROM human_resources.candidates")
                rows = cur.fetchall()
                if not rows:
                    return {"status": "error", "message": "No candidates found."}
                candidates = [
                    {"candidate_name": row[0], "cv_text": row[1]}
                    for row in rows
                ]
                return {"status": "success", "candidates": candidates}

    def get_all_openings(self) -> Dict[str, Any]:
        """Retrieves all job openings from the database."""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT name, job_description, evaluation_criteria FROM human_resources.openings")
                rows = cur.fetchall()
                if not rows:
                    return {"status": "error", "message": "No openings found."}
                openings = [
                    {"name": row[0], "job_description": row[1], "evaluation_criteria": row[2]}
                    for row in rows
                ]
                return {"status": "success", "openings": openings}

    def get_candidates_by_name(self, names: list[str]) -> Dict[str, Any]:
        """Retrieves specific candidates from the database by their names."""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT name, cv_text FROM human_resources.candidates WHERE name = ANY(%s)",
                    (names,),
                )
                rows = cur.fetchall()
                if not rows:
                    return {"status": "error", "message": "No candidates found."}
                candidates = [
                    {"candidate_name": row[0], "cv_text": row[1]}
                    for row in rows
                ]
                return {"status": "success", "candidates": candidates}

    def get_candidates_by_email(self, emails: list[str]) -> Dict[str, Any]:
        """Retrieves specific candidates from the database by their emails."""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT name, cv_text FROM human_resources.candidates WHERE email = ANY(%s)",
                    (emails,),
                )
                rows = cur.fetchall()
                if not rows:
                    return {"status": "error", "message": "No candidates found."}
                candidates = [
                    {"candidate_name": row[0], "cv_text": row[1]}
                    for row in rows
                ]
                return {"status": "success", "candidates": candidates}

    def get_openings_by_name(self, names: list[str]) -> Dict[str, Any]:
        """Retrieve specific job openings from the database by their names."""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT name, job_description, evaluation_criteria FROM human_resources.openings WHERE name = ANY(%s)",
                    (names,),
                )
                rows = cur.fetchall()
                if not rows:
                    return {"status": "error", "message": "No openings found."}
                openings = [
                    {"name": row[0], "job_description": row[1], "evaluation_criteria": row[2]}
                    for row in rows
                ]
                return {"status": "success", "openings": openings}

    def get_openings_by_id(self, ids: list[int]) -> Dict[str, Any]:
        """Retrieves specific job openings from the database by their IDs."""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT name, job_description, evaluation_criteria FROM human_resources.openings WHERE id = ANY(%s)",
                    (ids,),
                )
                rows = cur.fetchall()
                if not rows:
                    return {"status": "error", "message": "No openings found."}
                openings = [
                    {"name": row[0], "job_description": row[1], "evaluation_criteria": row[2]}
                    for row in rows
                ]
                return {"status": "success", "openings": openings}

_evaluator_tools = EvaluatorTools()

evaluator_tools = [
    _evaluator_tools.get_all_candidates,
    _evaluator_tools.get_all_openings,
    _evaluator_tools.get_candidates_by_name,
    _evaluator_tools.get_candidates_by_email,
    _evaluator_tools.get_openings_by_name,
    _evaluator_tools.get_openings_by_id,
]

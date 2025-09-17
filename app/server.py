# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

import google.auth
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app
from google.cloud import logging as google_cloud_logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider, export
from google.cloud import secretmanager

from app.utils.gcs import create_bucket_if_not_exists
from app.utils.tracing import CloudTraceLoggingSpanExporter
from app.utils.typing import Feedback

_, project_id = google.auth.default()
print(f"Project ID: {project_id}")
logging_client = google_cloud_logging.Client()
logger = logging_client.logger(__name__)
allow_origins = (
    os.getenv("ALLOW_ORIGINS", "").split(",") if os.getenv("ALLOW_ORIGINS") else None
)

bucket_name = f"gs://{project_id}-hero-logs-data"
create_bucket_if_not_exists(
    bucket_name=bucket_name, project=project_id, location="us-central1"
)

provider = TracerProvider()
processor = export.BatchSpanProcessor(CloudTraceLoggingSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _get_secret(project_id: str, secret_id: str, version_id: str = "latest") -> str:
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

# AlloyDB session configuration
db_user = _get_secret(project_id, "hero-cloudsql-user")
db_name = "postgres"
db_pass = _get_secret(project_id, "hero-cloudsql-password")
db_host = _get_secret(project_id, "hero-cloudsql-host")

# Set session_service_uri if database credentials are available
session_service_uri = None
if db_host and db_pass:
    session_service_uri = f"postgresql://{db_user}:{db_pass}@{db_host}:5432/{db_name}"

app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,
    artifact_service_uri=bucket_name,
    allow_origins=allow_origins,
    session_service_uri=session_service_uri,
)
app.title = "hero"
app.description = "API for interacting with the Agent hero"


@app.post("/feedback")
def collect_feedback(feedback: Feedback) -> dict[str, str]:
    """Collect and log feedback.

    Args:
        feedback: The feedback data to log

    Returns:
        Success message
    """
    logger.log_struct(feedback.model_dump(), severity="INFO")
    return {"status": "success"}


# Main execution
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

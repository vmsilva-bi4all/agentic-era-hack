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
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from google.adk.cli.fast_api import get_fast_api_app
from google.cloud import logging as google_cloud_logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider, export
import logging
from google.cloud.logging import Client
from google.cloud.logging_v2.handlers import setup_logging
from fastapi_cloud_logging import FastAPILoggingHandler, RequestLoggingMiddleware
from app.utils import secrets

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

# Retrieve database credentials from Secret Manager
db_user = secrets.get_secret(project_id, "hero-cloudsql-user")
db_name = secrets.get_secret(project_id, "hero-cloudsql-db-name")
db_pass = secrets.get_secret(project_id, "hero-cloudsql-password")
db_host = secrets.get_secret(project_id, "hero-cloudsql-host")

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
app.add_middleware(RequestLoggingMiddleware)
handler = FastAPILoggingHandler(Client())
setup_logging(handler)

# CORS settings
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Function to add CORS headers
def add_cors(response: JSONResponse):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Expose-Headers"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response


# Health check endpoint
@app.get("/")
async def health_check():
    logging.info("Root endpoint / requested")
    response = JSONResponse(content={"service": "Service Running"})
    return add_cors(response)


# Middleware to handle OPTIONS requests
@app.options("/{path:path}")
async def options_handler():
    response = JSONResponse(content={})
    response = add_cors(response)
    response.headers["Access-Control-Allow-Headers"] = "Origin, X-Requested-With, Content-Type, Accept, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Allow"] = "OPTIONS, GET, HEAD, POST, PUT, DELETE"
    return response


# Middleware to ensure all responses have CORS headers
@app.middleware("http")
async def cors_middleware(request: Request, call_next):
    response = await call_next(request)
    return add_cors(response)


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

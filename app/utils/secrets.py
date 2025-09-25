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

import logging
from typeguard import typechecked
from google.cloud import secretmanager


@typechecked
def get_secret(project_id: str, secret_id: str, version_id="latest") -> str:
    """Accesses the payload for the given secret version.

    Args:
        project_id (str): Google Cloud project ID.
        secret_id (str): ID of the secret.
        version_id (str): Version of the secret to access. Defaults to latest.

    Returns:
        str: The payload of the secret.
    """

    try:
        # Create the Secret Manager client
        client = secretmanager.SecretManagerServiceClient()

        # Build the resource name of the secret version
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

        # Access the secret version and return the payload
        response = client.access_secret_version(request={"name": name})
        payload = response.payload.data.decode("UTF-8")
    except Exception as e:
        error_message = f"Error accessing secret {secret_id} in project {project_id}: {e}"
        logging.error(error_message)
        raise RuntimeError(error_message)

    return payload

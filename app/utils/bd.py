import logging
from typeguard import typechecked
from typing import Any, Dict
import psycopg2


@typechecked
def get_connection(db_params: Dict[str, Any]) -> psycopg2.extensions.connection:
    """Establishes a connection to the PostgreSQL database.

    Args:
        db_params (Dict[str, Any]): The database connection parameters.

    Returns:
        psycopg2.extensions.connection: The database connection object.
    """

    try:
        connection = psycopg2.connect(**db_params)
    except Exception as e:
        error_message = f"Error connecting to the database: {e}"
        logging.error(error_message)
        raise RuntimeError(error_message)
    return connection

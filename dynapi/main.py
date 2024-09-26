"""
DYNAPI configurable API for infrastructure tests

authtor: Ivan Georgiev
license: MIT
"""
import json
import os
import random
from typing import Optional

from fastapi import FastAPI, Query, Response
from pydantic import BaseModel
import asyncio
import uvicorn

app = FastAPI()

# Get environment variables
VERSION = os.getenv("DYNAPP_VERSION", "0.1.0")
ERROR_FILE_PATH = os.getenv("DYNAPP_ERROR_FILE_PATH", "/app/error_file")
CONFIG_FILE = os.getenv("DYNAPP_CONFIG_PATH", "./config.json")
HOSTNAME = os.getenv("HOSTNAME", "")

# Load config.json for endpoint definitions
with open(file=CONFIG_FILE, mode='r', encoding="utf8") as config_file:
    config_data = json.load(config_file)

def should_return_500(probability: float) -> bool:
    """
    Simulate whether to return a 500 Internal Server Error based on a given probability.

    Args:
        probability (float): The probability between 0 and 1 that the error should occur.

    Returns:
        bool: True if a 500 error should be returned, False otherwise.
    """
    return random.random() < probability

@app.get("/{path:path}")
async def dynamic_endpoint(path: str, response: Response, rid: Optional[str] = Query(None)):
    """
    Handle dynamic API requests by returning a response based on the configuration file.

    Args:
        path (str): The dynamic path requested by the user.
        response (Response): The FastAPI response object to modify status codes.
        rid (Optional[str], optional): The optional request ID passed as a query parameter. Defaults to None.

    Returns:
        dict: The JSON response containing version, hostname, and request ID.
    """
    # Check if ERROR_FILE_PATH exists, and if so, return a forced 500 error
    if os.path.exists(ERROR_FILE_PATH):
        response.status_code = 500
        return {"error": f"Internal Server Error (forced) - {VERSION}", "hostname": HOSTNAME, "rid": rid if rid else "NONE"}

    # Find the corresponding endpoint config from the config file
    endpoint = next((ep for ep in config_data['endpoints'] if ep['path'] == f"/{path}"), None)
    if endpoint is None:
        response.status_code = 404
        return {"error": "Endpoint not found", "path": f"/{path}"}

    # Simulate delay, if any, from the config file
    delay = endpoint.get("delay", 0)
    await asyncio.sleep(delay)

    # Simulate HTTP 500 error based on probability from the config file
    if should_return_500(probability=endpoint.get('http_500_probability', 0)):
        response.status_code = 500
        return {"error": f"Dynamic Internal Server Error - {VERSION}", "hostname": HOSTNAME, "rid": rid if rid else "NONE"}

    # Set the response code based on the config file
    response.status_code = endpoint.get('response_code', 200)
    # Return response containing version, hostname, and request ID (rid)
    return {"version": VERSION, "hostname": HOSTNAME, "rid": rid if rid else "NONE"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)

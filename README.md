# dynapi: FastAPI Configurable Endpoints to test different scenarios

**dynapi** is a FastAPI-based application that dynamically generates endpoints based on a configuration file (`config.json`). It uses environment variables and random logic to control responses, delays, and error probabilities. The application can be run in Docker, and its behavior can be easily modified by adjusting the configuration file and environment variables.

It is intended to test scenarios in container orchestration:
- rolling update
- rollback
- container replacement

## Features

- Define dynamic endpoints via a JSON config file.
- Configure response codes, delays, and error probabilities for each endpoint.
- Use environment variables to control response content and behavior.
- Optionally force all endpoints to return HTTP 500 errors if a specific file exists.
- Lightweight and easy to deploy using Docker.

## Table of Contents

- [Installation](#installation)
- [Publishing](#publishing)
- [Configuration](#configuration)
- [License](#license)

---


## Installation

Application is intende to be run in Docker container. Helper script build.sh is created to help with build, run and publishing.

```bash
# Build Docker image
./build.sh

# Build and run the container on host port 8080
./build.sh run

# Run latest published version. VERSION response is current UNIX timestamp.
./run.sh
# or run with specific VERSION reponse
./run.sh "0.1.0"

# Example response
curl http://localhost:8080/health
 {"version":"0.1.0","hostname":"6809b0560a7e"}
```

## Publishing

1. Increment semantic version in version.txt
1. Run helper script to build the Docker image and publish it `./build.sh push`. Docker must be authenticated for this operation to succeed.

This will publish the image to:
- Dockerhub `docker.io/ivangeorgievbg/dynapi`. Tags semver and 'latest' are available.

## Configuaration

The application uses a config.json file to define the endpoints, their response codes, delays, and HTTP 500 probabilities. Default file is located in the root directory of the project. Custom file can be defined by setting env variable DYNAPP_CONFIG_PATH or by replacing the default config.json


```json
{
  "endpoints": [
    {
      "path": "/"
    },
    {
      "path": "/health",
      "response_code": 200,
      "delay": 1
    },
    {
      "path": "/slow",
      "delay": 60
    },
    {
      "path": "/veryslow",
      "delay": 120
    },    
    {
      "path": "/fail",
      "delay": 3,
      "http_500_probability": 0.8
    } 
  ]
}


```
Config File Fields

- path: Mandatory. The URL path for the endpoint. Use / for the root endpoint or /path for custom paths.
- response_code: Optional, default is 200. The HTTP status code to return (e.g., 200, 201, etc.).
- delay: The delay (in seconds) before the server responds.
- http_500_probability: Optional, default is 0. The probability (from 0.0 to 1.0) that the endpoint will return an HTTP 500 error. For example, 0.1 means a 10% chance of returning a 500 error.

Environment Variables

- DYNAPP_VERSION: The version string returned in the response. Defaults to 0.0.0 if not provided.
- DYNAPP_ERROR_FILE_PATH: A file path that, if it exists, forces all endpoints to return HTTP 500 errors immediately. By default is `/app/error_file`.
- DYNAPP_CONFIG_FILE: Location of the config file. By default is ./config.json.
- HOSTNAME: The hostname string returned in the response.
- DYNAPP_PORT: Listening port, default is 8080.
- DYNAPP_AUTODESTROY_TIME: If set, application will start returning HTTP 500 after this time since start up
- DYNAPP_NOSIGNALS: If set to 'true', application will ignore Ctrl+C. This is implemented by starting the uvicorn process without exec, so all signals are sent to the shell which ignores them.


Responses

- JSON in format {"version":"0.1.0","hostname":"6809b0560a7e", "rid": "NONE"} and response code from `response_code` (200 by default). Value of version is from environment variable DYNAPP_VERSION and value of hostname is from HOSTNAME. Value of rid is from rid query parameter, or NONE if not passed.
- JSON in format {"error":"Dynamic Internal Server Error"} and response code 500. Response from http_500_probability error.
- JSON in format {"error":"Internal Server Error (forced)"} and response code 500. Response if DYNAPP_ERROR_FILE_PATH file exists.
- JSON in format {"error":"Endpoint not found", "path": "/invalid"} and repose code 404. Response if endpoint is not present in config file, in this case "/invalid".

## License

This project is licensed under the MIT License.

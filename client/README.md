# ALBClient - Asynchronous Load Balancer Request Client

This is an asynchronous Python client that sends requests to an Application Load Balancer (ALB) at a configurable rate, logging responses and handling SSL/TLS errors gracefully. 

## Features

- Sends requests to the specified ALB URL at a configurable rate.
- Dynamically generates log files with timestamps.
- Ignores SSL/TLS errors during requests.
- Allows graceful shutdown using a stop file.

## Prerequisites

Before running the project, ensure that you have dependencies.

```bash
cd ./client
pip install -r requirements.txt
```
## Environment Variables

This client uses environment variables for configuration. Make sure to set them correctly:

- DYNCLIENT_ALB_URL: Required. The URL of the Application Load Balancer (ALB) to send requests to.
- DYNCLIENT_REQ_PER_BATCH: The number of requests to send per batch. Default: 5.
- DYNCLIENT_BATCH_TIMEOUT: The sleep time (in seconds) between request batches. Default: 10 seconds.

Example:

```bash

export DYNCLIENT_ALB_URL="https://example-alb-url.com"
export DYNCLIENT_REQ_PER_BATCH="10"
export DYNCLIENT_BATCH_TIMEOUT="5"

python alb_client.py
```

The client will continuously send requests to the ALB until it detects a stop file (/tmp/stop). To stop the client gracefully, create a file at /tmp/stop:

```bash
touch /tmp/stop
```

This will allow the client to stop after finishing the current batch and wait for 60 seconds before completing its shutdown. Ctrl+C can also be used, but it might generate errors.

## Logging

The client logs request details (status codes, response times, etc.) to both the console (stdout) and a dynamically generated log file. Log files are named using the format: log_<YYYYMMDDHHMMSS>.log, like log_20231001123045.log

You can find the log files in the same directory where the script is executed.

## Error Handling

- SSL/TLS errors are ignored, allowing the client to continue making requests to the ALB even if there are certificate issues.
- All exceptions and errors during request execution are logged with the relevant rid (request ID).

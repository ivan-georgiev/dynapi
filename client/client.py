import aiohttp
import asyncio
import logging
import os
import time
from datetime import datetime

# Generate a dynamic log file name based on the current timestamp
log_filename = f"log_{datetime.now().strftime('%Y%m%d%H%M%S')}.log"

# Configure logging to output to both log file and stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_filename, mode='w'),
        logging.StreamHandler()  # This enables stdout output
    ]
)

STOP_FILE_PATH = "/tmp/stop"

class ALBClient:
    def __init__(self, alb_url: str, requests_per_second: int = 10, sleep_time: float = 1.0):
        """
        Initialize the ALBClient with the ALB URL, requests per second rate, and configurable sleep time.

        Args:
            alb_url (str): The URL of the ALB to send requests to.
            requests_per_second (int): The number of requests to send per second (default: 10).
            sleep_time (float): Time in seconds to wait between each batch of requests (default: 1.0 second).
        """
        self.alb_url = alb_url
        self.requests_per_second = requests_per_second
        self.sleep_time = sleep_time
        self.rid = 1
        self.stop_sending = False
        self.session = None

    async def send_request(self):
        """
        Asynchronously sends a request to the ALB with a given rid and logs the response.
        """
        start_time = time.monotonic()  # Start time for measuring response
        try:
            current = self.rid
            self.rid += 1
            params = {'rid': current}
            async with self.session.get(self.alb_url, params=params) as response:
                status_code = response.status
                try:
                    # Attempt to parse JSON response
                    json_response = await response.json()
                    response_time = time.monotonic() - start_time  # Calculate response time
                except aiohttp.ContentTypeError:
                    json_response = {"error": "Response was not JSON"}

                # Log the result including response time
                log_message = f"Status Code: {status_code}, Response Time: {response_time:.2f}s, Response: {json_response}"
                logging.info(log_message)

        except Exception as e:
            # Log any errors that occur
            logging.error(f"RID: {current}, Error: {str(e)}")

    async def request_sender(self):
        """
        Asynchronously sends requests to the ALB at a rate defined by requests_per_second.
        Stops when stop_sending flag is set to True.
        """
        while not os.path.exists(STOP_FILE_PATH):
            tasks = [self.send_request() for _ in range(self.requests_per_second)]
            
            # Execute all tasks concurrently
            asyncio.gather(*tasks)

            # Wait for the specified sleep time before sending the next batch
            await asyncio.sleep(self.sleep_time)
        logging.warning("Stop file %s is detected. Wait 60 seconds to complete.", STOP_FILE_PATH)
        await asyncio.sleep(60)
        

    async def start(self):
        """
        Starts the client and sends requests until interrupted by the user.
        """
        logging.info("Starting to send requests to ALB...")

        # Initialize the aiohttp session with a connector that ignores SSL/TLS errors
        connector = aiohttp.TCPConnector(ssl=False)
        self.session = aiohttp.ClientSession(connector=connector)

        try:
            # Run the request sender
            await self.request_sender()
        except asyncio.CancelledError:
            logging.info("Client stopped by user with Ctrl+C. Stop file %s will ensure graceful shutdown.", STOP_FILE_PATH)
        finally:
            # Ensure the session is properly closed
            await self.session.close()


async def main():
    alb_url = os.environ["DYNCLIENT_ALB_URL"]
    requests_per_second = int(os.getenv("DYNCLIENT_REQ_PER_BATCH", "5"))
    sleep_time = int(os.getenv("DYNCLIENT_BATCH_TIMEOUT", "10"))
    
    client = ALBClient(alb_url=alb_url, requests_per_second=requests_per_second, sleep_time=sleep_time)
    await client.start()


if __name__ == "__main__":
    # Run the async main function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

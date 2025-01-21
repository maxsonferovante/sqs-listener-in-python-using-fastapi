# SQS Listener in Python using FastAPI

This project demonstrates how to create a background task in FastAPI to listen to AWS SQS messages.

## Project Structure

- `background_tasks.py`: Defines the `BackgroudTask` class that runs a background task at specified intervals.
- `server.py`: Sets up the FastAPI server and integrates the background task.
- `app.py`: Entry point to run the FastAPI application using Uvicorn.
- `listen_sqs.py`: Contains the function to listen to AWS SQS messages.

## Files

### `background_tasks.py`

This file contains the `BackgroudTask` class which inherits from `threading.Thread`. It validates the task name, interval, and function, and runs the task at the specified interval.

```python
import threading
import time

class BackgroudTask(threading.Thread):
    def __init__(self, name: str, func: callable, interval: int):
        super().__init__()
        self.name = self.__validate_name(name)
        self.interval = self.__validate_interval(interval)
        self.func = self.__validate_func(func)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self.join()

    def __validate_name(self, name):
        if name is None:
            return "Background Task - " + str(time.time())
        if not isinstance(name, str):
            raise ValueError("Name must be a string")
        return name

    def __validate_interval(self, interval):
        if interval < 0:
            raise ValueError("Interval must be greater than 0")
        if interval < 1:
            raise ValueError("Interval must be an integer")
        if interval > 60:
            raise ValueError("Interval must be less than 60")
        return interval

    def __validate_func(self, func):
        if not callable(func):
            raise ValueError("Func must be callable")
        return func

    def run(self, *args, **kwargs):
        print(f"Running task {self.name}")

        while True:
            print(f"Task {self.name} is running")
            self.func()
            time.sleep(self.interval)
```

### `server.py`

This file sets up the FastAPI server and integrates the background task using an async context manager.

```python
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.background_tasks.background_tasks import BackgroudTask
from src.sqs_listener.listen_sqs import listen_sqs

logger = logging.getLogger(__name__)

SERVICE_NAME = "sqs_listener_service"

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with BackgroudTask(name=SERVICE_NAME, func=listen_sqs, interval=2) as task:
        yield
        task.start()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def read_root():
    return {"Hello": "World"}
```

### `app.py`

This is the entry point to run the FastAPI application using Uvicorn.

```python
import uvicorn as uvicorn
from src.server import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=5, timeout_keep_alive=600, reload=False)
```

### `listen_sqs.py`

This file contains the `listen_sqs` function which listens to AWS SQS messages and processes them.

```python
import json
import boto3
import os
import logging

logger = logging.getLogger(__name__)

def listen_sqs():
    try:
        sqs = boto3.client('sqs', region_name=os.environ['AWS_REGION'])
        logger.info("Listening to SQS - %s", os.environ['SQS_QUEUE_URL'])
        response = sqs.receive_message(
            QueueUrl=os.environ['SQS_QUEUE_URL'],
            AttributeNames=['All'],
            MaxNumberOfMessages=1,
            WaitTimeSeconds=20
        )
        if "Messages" in response:
            for message in response['Messages']:
                body = json.loads(message['Body'])
                message_receipt_handle = message['ReceiptHandle']

                logger.info("Message received: %s", body)
                logger.info("Message Receipt Handle: %s", message_receipt_handle)

                sqs.delete_message(
                    QueueUrl=os.environ['SQS_QUEUE_URL'],
                    ReceiptHandle=message_receipt_handle
                )
        else:
            logger.info("No messages in queue")
    except Exception as e:
        logger.error("Error in listening to SQS - %s", e)
```

## Running the Application

1. Set up your AWS credentials and environment variables for `AWS_REGION` and `SQS_QUEUE_URL`.
2. Run the application using the following command:
   ```bash
   python app.py
   ```

This will start the FastAPI server and the background task to listen to SQS messages.

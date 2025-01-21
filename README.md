# Listener SQS em Python usando FastAPI

Este projeto demonstra como criar uma tarefa em segundo plano no FastAPI para escutar mensagens do AWS SQS.

## Estrutura do Projeto

- `background_tasks.py`: Define a classe `BackgroudTask` que executa uma tarefa em segundo plano em intervalos especificados.
- `server.py`: Configura o servidor FastAPI e integra a tarefa em segundo plano.
- `app.py`: Ponto de entrada para executar a aplicação FastAPI usando Uvicorn.
- `listen_sqs.py`: Contém a função para escutar mensagens do AWS SQS.

## Arquivos

### `background_tasks.py`

Este arquivo contém a classe `BackgroudTask` que herda de `threading.Thread`. Ela valida o nome da tarefa, intervalo e função, e executa a tarefa no intervalo especificado.

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

Este arquivo configura o servidor FastAPI e integra a tarefa em segundo plano usando um gerenciador de contexto assíncrono.

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

Este é o ponto de entrada para executar a aplicação FastAPI usando Uvicorn.

```python
import uvicorn as uvicorn
from src.server import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=5, timeout_keep_alive=600, reload=False)
```

### `listen_sqs.py`

Este arquivo contém a função `listen_sqs` que escuta mensagens do AWS SQS e as processa.

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

## Executando a Aplicação

1. Configure suas credenciais AWS e variáveis de ambiente para `AWS_REGION` e `SQS_QUEUE_URL`.
2. Execute a aplicação usando o seguinte comando:
   ```bash
   python app.py
   ```

Isso iniciará o servidor FastAPI e a tarefa em segundo plano para escutar mensagens do SQS.

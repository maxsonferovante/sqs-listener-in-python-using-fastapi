import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.background_tasks.background_tasks import BackgroudTask
from src.sqs_listener.listen_sqs import listen_sqs
import asyncio


logger = logging.getLogger(__name__)

SERVICE_NAME = "sqs_listener_service"

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with BackgroudTask(name=SERVICE_NAME,func=listen_sqs,interval=2) as task:
        yield    
        task.start()
    

app = FastAPI(lifespan=lifespan)


@app.get("/")
async def read_root():
    return {"Hello": "World"}



@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_event_loop()
    loop.create_task(listen_sqs(app))
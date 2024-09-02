from fastapi import FastAPI

from fast_zero.schemas import Message

app = FastAPI()


@app.get('/', response_model=Message)
async def root():
    return {'message': 'Hello World'}

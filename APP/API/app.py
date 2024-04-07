import os

from uuid import uuid4
from vllm.engine.arg_utils import AsyncEngineArgs
from vllm.engine.async_llm_engine import AsyncLLMEngine
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse, Response, StreamingResponse
from dotenv import load_dotenv
from vllm import SamplingParams
from vllm.usage.usage_lib import UsageContext
import uvicorn
import json
import time
from datetime import datetime
from utils.utils import *

load_dotenv()

app = FastAPI()

@app.post('/api/generate_answer') # Генерация общих ответов
async def base_helper(request: Request):
    data = await request.json()
    message = data['message']
    chat_id = data['chat_id']
    if chat_id not in chat.history:
        chat.init_chat(chat_id)
        label = await chat.classify(message, chat_id, ['самолет', 'отель'])
        chat.history[chat_id]['Label'] = label
        return chat.ask_data(chat_id)
    else:
        if chat.history[chat_id]['Status'] == 'Ask_data':
            chat.history[chat_id]['Counter'] += 1
            return chat.ner(message, chat_id)
        elif chat.history[chat_id]['Status'] == 'NER' and chat.history[chat_id]['Counter'] < 2:
            label = await chat.classify(message, chat_id, ['согласен', 'отказывается'])
            if label == 'согласен':
                if chat.history[chat_id]['Label'] == 'отель':
                    chat.history[chat_id]['Label'] = 'самолет'
                elif chat.history[chat_id]['Label'] == 'самолет':
                    chat.history[chat_id]['Label'] = 'отель'
                return chat.ask_data(chat_id)
            elif label == 'отказывается':
                return chat.say_goodbye(chat_id)
            else:
                return chat.say_goodbye(chat_id)
        else:
            return chat.say_goodbye(chat_id)


if __name__ == '__main__':   
    engine_args = AsyncEngineArgs(
                    model=os.environ['MODEL_PATH'],
                    tokenizer=None,
                    tokenizer_mode="auto",
                    trust_remote_code=True,
                    dtype="half",
                    revision=None,
                    tokenizer_revision=None,
                    seed=0,
                    gpu_memory_utilization=0.9,
                    swap_space=4
                )
    llm_engine = AsyncLLMEngine.from_engine_args(engine_args, usage_context=UsageContext.API_SERVER)
    chat = Chat(llm_engine)
    uvicorn.run(app,
                host='0.0.0.0',
                port=8000,
                log_level="debug",
                timeout_keep_alive=5)
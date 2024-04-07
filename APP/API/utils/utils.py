from vllm import SamplingParams
from uuid import uuid4
from utils.prompts import *
import json
from fastapi.responses import StreamingResponse

class Chat:

    def __init__(self, llm_engine):
        self.history = {}
        self.llm_engine = llm_engine

    def init_chat(self, chat_id):
        self.history[chat_id] = {
            'Text': '',
            'Status': 'Classification',
            'Label': '',
            'Data': '',
            'Counter': 0
        }

    async def classify(self, message, chat_id, classes):
        request_id = uuid4()
        sampling_params = SamplingParams(temperature=0, max_tokens=30, stop=classes, include_stop_str_in_output=True)
        classes_text = ', '.join(classes)
        prompt = classify_prompt.format(classes_text, classes_text, message)
        results_generator = self.llm_engine.generate(prompt, sampling_params, request_id)
        async for request_output in results_generator:
            final_output = request_output
        text_outputs = [output.text for output in final_output.outputs]
        label = ''.join([char for char in text_outputs[0] if char.isalpha()])
        return label

    def ner(self, message, chat_id):
        request_id = uuid4()
        sampling_params = SamplingParams(temperature=0.5, top_p=0.5, max_tokens=100, stop='}', include_stop_str_in_output=True)
        prompt = ner_prompts[self.history[chat_id]['Label']].format(message)
        results_generator = self.llm_engine.generate(prompt, sampling_params, request_id)
        self.history[chat_id]['Status'] = 'NER'
        async def stream_results():
            async for request_output in results_generator:
                prompt = request_output.prompt
                text_outputs = [
                    prompt + output.text for output in request_output.outputs
                ]
                self.history[chat_id]['Text'] = text_outputs[-1].replace(prompt, '')
                yield (json.dumps(self.history[chat_id], ensure_ascii=False) + '\n').encode("utf-8")
        return StreamingResponse(stream_results())

    def ask_data(self, chat_id):
        request_id = uuid4()
        sampling_params = SamplingParams(temperature=0.5, top_p=0.5, max_tokens=300, stop='Конец запроса', repetition_penalty=1.1)
        data_to_ask = ', '.join(ask_data[self.history[chat_id]['Label']])
        prompt = ask_prompt.format(data_to_ask)
        results_generator = self.llm_engine.generate(prompt, sampling_params, request_id)
        self.history[chat_id]['Status'] = 'Ask_data'
        async def stream_results():
            async for request_output in results_generator:
                prompt = request_output.prompt
                text_outputs = [
                    prompt + output.text for output in request_output.outputs
                ]
                self.history[chat_id]['Text'] = text_outputs[-1].replace(prompt, '')
                yield (json.dumps(self.history[chat_id], ensure_ascii=False) + '\n').encode("utf-8")
        return StreamingResponse(stream_results())

    def say_goodbye(self, chat_id):
        request_id = uuid4()
        sampling_params = SamplingParams(temperature=0, max_tokens=80, stop='Конец ответа')
        prompt = """Ты общался с клиентом в чате. Теперь нужно поблагодарить его за выбор нашего сервиса и попрощаться с ним.

        Используй шаблон:

        Ответ: текст прощания с клиентом.
        Конец ответа

        Начинай!
        Ответ: """
        results_generator = self.llm_engine.generate(prompt, sampling_params, request_id)
        self.history[chat_id]['Status'] = 'Done'
        async def stream_results():
            async for request_output in results_generator:
                prompt = request_output.prompt
                text_outputs = [
                    prompt + output.text for output in request_output.outputs
                ]
                self.history[chat_id]['Text'] = text_outputs[-1].replace(prompt, '')
                yield (json.dumps(self.history[chat_id], ensure_ascii=False) + '\n').encode("utf-8")
        return StreamingResponse(stream_results())
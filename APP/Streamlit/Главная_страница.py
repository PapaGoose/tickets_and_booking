import streamlit as st
import requests
from dotenv import load_dotenv
import os
import time
import json
from uuid import uuid4
load_dotenv()

def call_api(data):
    pass

def get_json_events(send_data):
    stream_response = requests.post(f"http://{os.environ['API_ADDRESS']}:{os.environ['BACKEND_PORT']}/api/generate_answer", json=send_data, stream=True)
    for line in stream_response.iter_lines():
        yield json.loads(line.decode("utf-8"))

st.set_page_config(page_title="AI Ассистент")
st.markdown(
    """
    <style>
        [data-testid="stSidebarNav"] {
            background-image: url(https://pngicon.ru/file/uploads/MTS.png);
            background-size: 330px 85px;
            background-repeat: no-repeat;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Определение базовых параметров
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "Я готов помочь Вам забронировать отель и/или купить билеты на самолет. Подскажите, пожалуйста, какое действие вы хотели бы выполнить?"}]
if "chat_id" not in st.session_state.keys():
    st.session_state.chat_id = str(uuid4())

# Отображение или отчистка чата
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

# Генерация ответа на вопрос
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Думаю..."):
            send_data = {
                            "message": prompt,
                            "chat_id": st.session_state.chat_id
                        }
            start_time = time.time()
            placeholder = st.empty()
            for event in get_json_events(send_data):
                full_response = event['Text']
                placeholder.markdown(full_response, unsafe_allow_html=True)

            # call mock api
            if event['Status'] == 'NER':
                call_api(eval(event['Text']))

            if event['Status'] == 'NER' and event['Counter'] < 2:
                if event['Label'] == 'отель':
                    json_data = eval(event["Text"])
                    full_response += f'\n\nНе желаете ли купить билеты в {json_data["city"]}?'
                elif event['Label'] == 'самолет':
                    json_data = eval(event["Text"])
                    full_response += f'\n\nНе желаете ли забронировать отель в {json_data["arrival_city"]}?'
                placeholder.markdown(full_response, unsafe_allow_html=True)
            placeholder = st.empty()
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)
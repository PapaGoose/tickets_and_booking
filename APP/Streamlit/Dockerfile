FROM python:3.10
WORKDIR /usr/src/app
COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# ENTRYPOINT [ "python" ]
CMD ["streamlit", "run", "Главная_страница.py"]
__Для запуска ноутбуков__: необходимо установить зависимости из APP/API/requirements.txt

__Для развертывания стенда__:
    - создайте папку models в APP и перенесите туда модель
    - заполните .env 
    - запустите ./build.sh
    - docker compose build
    - docker compose up -d
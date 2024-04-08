__Адрес для загрузки модели и большого csv__: https://dropmefiles.com/D9nwZ (действительна до 15.04.2024)

__Для запуска ноутбуков__: 
    - необходимо установить зависимости из APP/API/requirements.txt
    - перенести hotels.csv в папку Data
    - перенести папку NER-mistral_v0.1 в основную директорию

__Для развертывания стенда__:
    - создайте папку models в APP и перенесите туда папку Mistral_NER_merged
    - заполните .env 
    - запустите ./build.sh
    - docker compose build
    - docker compose up -d

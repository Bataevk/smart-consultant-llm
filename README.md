# smart-consultant-llm

LLM bot for consulting users on system data using lightRAG technology

---

Все необходимые репозитории закреплены в профиле

---

## Содержание

- [smart-consultant-llm](#smart-consultant-llm)
  - [Содержание](#содержание)
  - [Требования](#требования)
  - [Запуск приложения](#запуск-приложения)
  - [Логирование](#логирование)
  - [Дополнительная информация](#дополнительная-информация)

## Требования

1. **Установка зависимостей:**
   - Установите необходимые библиотеки из файла `requirements.txt`:
     ```sh
     pip install -r requirements.txt
     ```

2. **Скачивание и распаковка кеша базы данных:**
   - Скачайте архив с кешом базы данных и распакуйте его в корневую директорию проекта, чтобы в корне была папка `./.db_caches`.

3. **Установка Telegram бота:**
   - Следуйте инструкциям по установке Telegram бота из репозитория по ссылке: [ССЫЛКА](https://github.com/Bataevk/simple-telegram-bot-for-LLM)

4. **Выбор провайдера/локального сервера и модели**
   *Использование внешних API и локальных серверов:*
  - Вы можете использовать внешние API с LLM, такие как Nvidia NIM и другие.
  - Также возможен запуск локального сервера (Ollama, LM Studio).
  - В обоих случаях необходимо, чтобы сервер поддерживал функции (tools).

5. **Настройка API ключа:**
   - Установите API ключ для сервера с LLM в переменных окружения.

6. **Настройка конфигурации:**
   - Убедитесь, что в файле `config.py` указаны правильные URL сервера и модель:
     ```python
     LLM_CONFIG = {
         "base_url": "https://integrate.api.nvidia.com/v1",
         "model": "meta/llama-3.1-405b-instruct"
     }
     ```

## Запуск приложения

1. **Запуск веб-сервера:**
   - Запустите веб-сервер с помощью команды:
     ```sh
     python main.py --host <host> --port <port> --logs <logs>
     ```
     Параметры:
     - `--host`: Хост для запуска (по умолчанию: `0.0.0.0`)
     - `--port`: Порт для запуска (по умолчанию: `5000`)
     - `--logs`: Включение/выключение логирования (по умолчанию: `True`)

2. **Генерация графа (если кеш отсутствует):**
   - Если кеш графа отсутствует, запустите генерацию графа:
     ```sh
     python ./graph_pack/graph_module.py
     ```
     Для генерации графа используются файлы с госуслуг, полученные через парсер. Ссылка на парсер: [ССЫЛКА](https://github.com/Bataevk/gosuslugi-faq-parser)

## Логирование

Логи сохраняются в папке `logs` и включают три файла:
- `debug.log`
- `error.log`
- `info.log`

## Дополнительная информация

- **Директория для документов:**
  - Файлы для загрузки в систему хранятся в папке `inputs`.

- **Качество графа:**
  - Граф был сгенерирован на модели `llama-3.1-405b-instruct`, что обеспечило ему высокое качество.

- **Производительность:**
  - Скорость работы графовой базы данных и локальной LLM зависит от производительности устройства.
  - Рекомендуется использовать модели с GPQA и MMLU не ниже 30 и 75 соответственно.

```mermaid
erDiagram
    USER {
        int id PK
        string name
    }

    METER_READING {
        int id PK
        int user_id FK
        string meter_type
        float value
        datetime timestamp
    }

    MEDICAL_APPOINTMENT {
        int id PK
        int user_id FK
        string doctor
        datetime appointment_time
    }

    SCHOOL_ENROLLMENT {
        int id PK
        int user_id FK
        string child_name
        string school_name
    }

    VEHICLE_REGISTRATION {
        int id PK
        int user_id FK
        string vehicle_info
    }

    MESSAGE {
        int id PK
        int user_id FK
        string message_type
        string content
        datetime timestamp
    }

    USER ||--o{ METER_READING : has
    USER ||--o{ MEDICAL_APPOINTMENT : has
    USER ||--o{ SCHOOL_ENROLLMENT : has
    USER ||--o{ VEHICLE_REGISTRATION : has
    USER ||--o{ MESSAGE : has
```

Эта схема описывает таблицы и их связи в базе данных:

- `USER`: Таблица пользователей.
- `METER_READING`: Таблица для хранения показаний счетчиков.
- `MEDICAL_APPOINTMENT`: Таблица для хранения записей к врачам.
- `SCHOOL_ENROLLMENT`: Таблица для хранения записей детей в школу.
- `VEHICLE_REGISTRATION`: Таблица для хранения информации о транспортных средствах.
- `MESSAGE`: Таблица для хранения сообщений, связанных с пользователями.

Каждая таблица связана с таблицей `USER` через внешний ключ `user_id`.
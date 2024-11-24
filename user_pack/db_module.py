from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime

Base = declarative_base()

# Таблица пользователей
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    # Отношения с другими таблицами
    meter_readings = relationship("MeterReading", back_populates="user")
    medical_appointments = relationship("MedicalAppointment", back_populates="user")
    school_enrollments = relationship("SchoolEnrollment", back_populates="user")
    vehicle_registrations = relationship("VehicleRegistration", back_populates="user")
    # Добавляем связь с сообщениями
    messages = relationship("Message", back_populates="user")

# Таблица показаний счетчиков
class MeterReading(Base):
    __tablename__ = 'meter_readings'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    meter_type = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    # Связь с таблицей User
    user = relationship("User", back_populates="meter_readings")

# Таблица записей к врачам
class MedicalAppointment(Base):
    __tablename__ = 'medical_appointments'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    doctor = Column(String, nullable=False)
    appointment_time = Column(DateTime, nullable=False)

    # Связь с таблицей User
    user = relationship("User", back_populates="medical_appointments")

# Таблица записей в школу
class SchoolEnrollment(Base):
    __tablename__ = 'school_enrollments'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    child_name = Column(String, nullable=False)
    school_name = Column(String, nullable=False)

    # Связь с таблицей User
    user = relationship("User", back_populates="school_enrollments")

# Таблица регистраций транспортных средств
class VehicleRegistration(Base):
    __tablename__ = 'vehicle_registrations'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    vehicle_info = Column(String, nullable=False)

    # Связь с таблицей User
    user = relationship("User", back_populates="vehicle_registrations")



# MESSAGES

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    message_type = Column(String, nullable=False)  # 'human' или 'ai'
    content = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    # Связь с таблицей User
    user = relationship("User", back_populates="messages")





# МЕТОДЫ --------------------------------

def add_message(user_id: int, message_type: str, content: str) -> str:
    """
    Добавить сообщение для пользователя.

    Parameters:
        user_id: ID пользователя.
        message_type: Тип сообщения ('human' или 'ai').
        content: Текст сообщения.

    Returns:
        Строка с результатом операции.
    """
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        return f"Пользователь с таким ID не найден."

    new_message = Message(user_id=user_id, message_type=message_type, content=content)
    session.add(new_message)
    session.commit()
    return f"Сообщение успешно добавлено для пользователя {user.name}."


def get_last_messages(user_id: int, n: int = 15):
    """
    Получить последние N сообщений пользователя.

    Parameters:
        user_id: ID пользователя.
        n: Количество сообщений (по умолчанию 15).

    Returns:
        Список сообщений в формате [(type, content, timestamp)].
    """
    messages = (
        session.query(Message)
        .filter_by(user_id=user_id)
        .order_by(Message.timestamp.desc())
        .limit(n)
        .all()
    )

    return reversed(messages)
    # return [(msg.message_type, msg.content, msg.timestamp) for msg in reversed(messages)]



def add_user(user_id: int, name: str) -> str:
    """Добавить нового пользователя в базу данных.

    Parameters:
        user_id: ID пользователя (должен быть уникальным).
        name: Имя пользователя.

    Returns:
        Строка с результатом операции.
    """
    # Проверка, существует ли пользователь с таким ID
    existing_user = session.query(User).filter_by(id=user_id).first()
    if existing_user:
        return f"Пользователь с ID {user_id} уже существует: {existing_user.name}"
    
    # Создание и добавление нового пользователя
    new_user = User(id=user_id, name=name)
    session.add(new_user)
    session.commit()
    return f"Пользователь {name} с ID {user_id} успешно добавлен."




# Настройка базы данных
engine = create_engine('sqlite:///.bot_database.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

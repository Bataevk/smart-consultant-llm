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

# Настройка базы данных
engine = create_engine('sqlite:///.bot_database.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

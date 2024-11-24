
from langchain.tools import tool
from user_pack.db_module import *


@tool
def submit_meter_reading(user_id: int, meter_type: str, value: float) -> str:
    """Submit meter reading for a user.

    Parameters:
        user_id: (put a cap = -1)
        meter_type: The type of meter (e.g., 'hot_water', 'cold_water', 'heat', 'electricity').
        value: The meter reading value.

    Exenple:
        Красный счетчик 123.123: user_id=-1, meter_type='hor_water', value=123.123;
        Холодная вода 150: user_id=-1, meter_type = 'cold_water', value=150.000';

        
    Returns:
        A confirmation message or an error message if the reading is lower than the previous one.
    """
    last_reading = session.query(MeterReading).filter_by(user_id=user_id, meter_type=meter_type).order_by(MeterReading.timestamp.desc()).first()
    if last_reading and value < last_reading.value:
        return "Показания не могут быть ниже предыдущих."
    new_reading = MeterReading(user_id=user_id, meter_type=meter_type, value=value)
    session.add(new_reading)
    session.commit()
    return f"Показания успешно приняты. Установлено значение {value}"

@tool
def get_last_meter_reading(user_id: int, meter_type: str) -> str:
    """Get the last meter reading for a user.

    Parameters:
        user_id: (put a cap = -1)
        meter_type: The type of meter (e.g., 'hot_water', 'cold_water', 'heat', 'electricity').

    Returns:
        The last meter reading value or a message if no readings are found.
    """
    last_reading = session.query(MeterReading).filter_by(user_id=user_id, meter_type=meter_type).order_by(MeterReading.timestamp.desc()).first()
    if last_reading:
        return f"Последние показания - {meter_type}: {last_reading.value}"
    return f"Показания - {meter_type} не найдены."

@tool
def get_all_meter_readings(user_id: int) -> str:
    """Get all meter readings for a user.

    Parameters:
        user_id: ID of the user.

    Returns:
        A formatted list of all meter readings or a message if no readings are found.
    """
    meter_readings = session.query(MeterReading).filter_by(user_id=user_id).order_by(MeterReading.timestamp.desc()).all()
    if not meter_readings:
        return "Нет записей для пользователя."

    readings_list = [
        f"[{reading.timestamp}] {reading.meter_type}: {reading.value}" 
        for reading in meter_readings
    ]
    return "\n".join(readings_list)


@tool
def schedule_medical_appointment(user_id: int, doctor: str, appointment_time: datetime.datetime) -> str:
    """Schedule a medical appointment for a user.

    Parameters:
        user_id: (put a cap = -1)
        doctor: The name of the doctor.
        appointment_time: The time of the appointment.

    Returns:
        A confirmation message.
    """
    new_appointment = MedicalAppointment(user_id=user_id, doctor=doctor, appointment_time=appointment_time)
    session.add(new_appointment)
    session.commit()
    return "Запись успешно создана."

@tool
def get_medical_appointments(user_id: int) -> str:
    """Get all medical appointments for a user.

    Parameters:
        user_id: (put a cap = -1)

    Returns:
        A list of medical appointments or a message if no appointments are found.
    """
    appointments = session.query(MedicalAppointment).filter_by(user_id=user_id).all()
    if appointments:
        return "\n".join([f"Запись к {appointment.doctor} на {appointment.appointment_time}" for appointment in appointments])
    return "Записей не найдено."

@tool
def enroll_child_in_school(user_id: int, child_name: str, school_name: str) -> str:
    """Enroll a child in school for a user.

    Parameters:
        user_id: (put a cap = -1)
        child_name: The name of the child.
        school_name: The name of the school.

    Returns:
        A confirmation message or an error message if the child is already enrolled.
    """
    existing_enrollment = session.query(SchoolEnrollment).filter_by(user_id=user_id, child_name=child_name).first()
    if existing_enrollment:
        return f"{child_name} уже записан в {existing_enrollment.school_name}."
    new_enrollment = SchoolEnrollment(user_id=user_id, child_name=child_name, school_name=school_name)
    session.add(new_enrollment)
    session.commit()
    return "Ребенок успешно записан в школу."

@tool
def get_school_enrollments(user_id: int) -> str:
    """Get all school enrollments for a user.

    Parameters:
        user_id: (put a cap = -1)

    Returns:
        A list of school enrollments or a message if no enrollments are found.
    """
    enrollments = session.query(SchoolEnrollment).filter_by(user_id=user_id).all()
    if enrollments:
        return "\n".join([f"{enrollment.child_name} записан в {enrollment.school_name}" for enrollment in enrollments])
    return "Записей не найдено."

@tool
def register_vehicle(user_id: int, vehicle_info: str) -> str:
    """Register a vehicle for a user.

    Parameters:
        user_id:  (put a cap = -1)
        vehicle_info: Information about the vehicle.

    Returns:
        A confirmation message or an error message if the vehicle is already registered.
    """
    existing_vehicle = session.query(VehicleRegistration).filter_by(user_id=user_id, vehicle_info=vehicle_info).first()
    if existing_vehicle:
        return "Транспортное средство уже зарегистрировано."
    new_vehicle = VehicleRegistration(user_id=user_id, vehicle_info=vehicle_info)
    session.add(new_vehicle)
    session.commit()
    return f"Транспортное средство успешно зарегистрировано. {vehicle_info}"

@tool
def get_registered_vehicles(user_id: int) -> str:
    """Get all registered vehicles for a user.

    Parameters:
        user_id: (put a cap = -1)

    Returns:
        A list of registered vehicles or a message if no vehicles are found.
    """
    vehicles = session.query(VehicleRegistration).filter_by(user_id=user_id).all()
    if vehicles:
        return "\n".join([f"Транспортное средство: {vehicle.vehicle_info}" for vehicle in vehicles])
    return "Транспортные средства не найдены."

@tool
def get_user_info(user_id: int) -> str:
    """Get information about the user and related data.

    Parameters:
        user_id: User ID.

    Returns:
        A string with information about the user or a message if the user is not found.
    """
    # Поиск пользователя в базе данных
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        return f"Пользователь с таким ID не найден."

    # Формирование информации о пользователе
    info = [f"Имя: {user.name}"]

    # Добавляем данные о показаниях счетчиков
    if user.meter_readings:
        meter_readings = "\n".join(
            [f"- {reading.meter_type}: {reading.value} (дата: {reading.timestamp})" for reading in user.meter_readings]
        )
        info.append(f"Показания счетчиков:\n{meter_readings}")
    else:
        info.append("Показания счетчиков: отсутствуют")

    # Добавляем данные о медицинских записях
    if user.medical_appointments:
        medical_appointments = "\n".join(
            [f"- Врач: {appointment.doctor}, дата: {appointment.appointment_time}" for appointment in user.medical_appointments]
        )
        info.append(f"Медицинские записи:\n{medical_appointments}")
    else:
        info.append("Медицинские записи: отсутствуют")

    # Добавляем данные о школьных записях
    if user.school_enrollments:
        school_enrollments = "\n".join(
            [f"- Ребенок: {enrollment.child_name}, школа: {enrollment.school_name}" for enrollment in user.school_enrollments]
        )
        info.append(f"Школьные записи:\n{school_enrollments}")
    else:
        info.append("Школьные записи: отсутствуют")

    # Добавляем данные о транспортных средствах
    if user.vehicle_registrations:
        vehicles = "\n".join(
            [f"- Транспортное средство: {vehicle.vehicle_info}" for vehicle in user.vehicle_registrations]
        )
        info.append(f"Транспортные средства:\n{vehicles}")
    else:
        info.append("Транспортные средства: отсутствуют")

    # Возвращаем собранную информацию в виде строки
    return "\n".join(info)


@tool 
def get_bot_description() -> str:
    """Return a description of the bot's capabilities."""
    return "Бот умеет принимать показания счётчиков, назначать встречи медицинским врачам, регистрировать водителей, искать информацию о школах и транспортных средствах."
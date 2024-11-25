from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit
import os
from icecream import ic
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from utils.logs_module import logger

from user_pack.tools import *
from user_pack.db_module import add_user, add_message, get_last_messages
from utils.utils import *
from graph_pack.graph_utils import get_default_init_rag
from graph_pack.tools_templates import get_search_tool
from config import LLM_CONFIG
from llm_module import get_response_llm, get_tools_llm, llm_stream, llm_invoke, convert_db_messages_to_llm_messages


ic.enable()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Load variables from custom environment
load_keys()

# Set keys
if not os.environ.get("OPENAI_API_KEY"):
    set_keys(['OPENAI'])

# Save variables to custom environment
save_keys()

# Init RAG
RAG = get_default_init_rag()

# Initialize tools
search = get_search_tool(RAG)

tools = {
    'search': search,
    'submit_meter_reading': submit_meter_reading,
    'get_last_meter_reading': get_last_meter_reading,
    'schedule_medical_appointment': schedule_medical_appointment,
    'get_medical_appointments': get_medical_appointments,
    'enroll_child_in_school': enroll_child_in_school,
    'get_school_enrollments': get_school_enrollments,
    'register_vehicle': register_vehicle,
    'get_registered_vehicles': get_registered_vehicles,
    'get_all_meter_readings': get_all_meter_readings,
    'get_bot_description': get_bot_description,
    'get_user_info':get_user_info
}

# Initialize LLM with OpenAI API
model = ChatOpenAI(**LLM_CONFIG)



@app.route('/')
def index():
    """Отображает index.html на главной странице."""
    return render_template('./index.html')

@socketio.on('connect')
def handle_connect():
    logger.info('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Client disconnected')

@socketio.on('message')
def handle_message(data):
    logger.debug(data)
    user_query = data.get('query')
    id = data.get('id', 0)

    add_user(id, 'Веб пользователь')

    if not user_query:
        emit('response', {"error": "No query provided"})
        return

    # Get messages from DB
    db_messages = get_last_messages(id)
    messages = convert_db_messages_to_llm_messages(db_messages)
    
    messages.append(HumanMessage(user_query))
    model_tools = get_tools_llm(model, tools)
    model_response = get_response_llm(model)

    message = ''

    for chunk in llm_stream(model_response, model_tools, messages, tools, id):
        message += chunk.content
        emit('response', {"content": chunk.content})

    # Add message to DB
    add_message(id, 'human', user_query)
    add_message(id, 'ai', message)

@app.route('/init_user', methods=['POST'])
def init_user():
    logger.debug(request.json)
    data = request.json
    user_id = data.get('id')
    user_name = data.get('user_name')

    return jsonify({'message': add_user(user_id, user_name)})

@app.route('/invoke', methods=['POST'])
def chat():

    data = request.json
    logger.debug(data)

    user_query = data.get('query')
    id = data.get('id', 0)

    if not user_query:
        return jsonify({"error": "No query provided"}), 400

    # Get messages from DB
    db_messages = get_last_messages(id)
    messages = convert_db_messages_to_llm_messages(db_messages)

    messages.append(HumanMessage(user_query))
    model_tools = get_tools_llm(model, tools)
    model_response = get_response_llm(model)

    message = llm_invoke(model_response, model_tools, messages, tools, id)

    # Add message to DB
    add_message(id, 'human', user_query)
    add_message(id, 'ai', message.content)

    return jsonify({"text": message.content})

def start_server(host = '127.0.0.1',port = 5000):
    add_user(0, "Бесплатный пользователь")
    socketio.run(app, debug=True, host=host, port=port)

if __name__ == '__main__':
   start_server()

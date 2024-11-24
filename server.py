from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import os
from icecream import ic
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from user_pack.tools import *
from utils import *
from graph_pack.graph_utils import get_default_init_rag
from graph_pack.tools_templates import get_search_tool
from config import WORKING_DIR, LLM_CONFIG, SYSTEM_PROMT_TOOLS, SYSTEM_PROMPT_RESPONSE
from llm_module import get_response_llm, get_tools_llm, llm_stream, llm_invoke

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
    'get_bot_description': get_bot_description
}

# Initialize LLM with OpenAI API
model = ChatOpenAI(**LLM_CONFIG)



@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('message')
def handle_message(data):
    user_query = data.get('query')

    if not user_query:
        emit('response', {"error": "No query provided"})
        return

    messages = [HumanMessage(user_query)]
    model_tools = get_tools_llm(model, tools)
    model_response = get_response_llm(model)

    message = ''

    for chunk in llm_stream(model_response, model_tools, messages, tools):
        message += chunk.content
        emit('response', {"content": chunk.content})

    messages.append(AIMessage(message))

@app.route('/invoke', methods=['POST'])
def chat():
    data = request.json
    user_query = data.get('query')

    if not user_query:
        return jsonify({"error": "No query provided"}), 400

    messages = [HumanMessage(user_query)]
    model_tools = get_tools_llm(model, tools)
    model_response = get_response_llm(model)

    message = llm_invoke(model_response, model_tools, messages, tools)

    messages.append(AIMessage(message))

    return jsonify({"response": message})


if __name__ == '__main__':
    socketio.run(app, debug=True)

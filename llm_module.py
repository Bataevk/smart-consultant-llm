import os  # стандартные импорты
from icecream import ic

# сторонние импорты
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# Локальные импорты
from user_pack.tools import *
from utils.utils import *
from graph_pack.graph_utils import get_default_init_rag
from graph_pack.tools_templates import get_search_tool
from config import WORKING_DIR, LLM_CONFIG, SYSTEM_PROMT_TOOLS, SYSTEM_PROMPT_RESPONSE
from utils.logs_module import logger
from security_pack.censor_module import check_message


ic.enable()


def get_tools_llm(model, tools):
    # Binding tools
    llm_tools = model.bind_tools(tools.values())

    return PromptTemplate.from_template(SYSTEM_PROMT_TOOLS) | llm_tools

def get_response_llm(model):
    # Generating LLM tools
    return PromptTemplate.from_template(SYSTEM_PROMPT_RESPONSE) | model


def __llm_get_tools_messages(model_tools, tools, chat_messages, id = 0 ):
    
    messages = chat_messages[:]

    if not (check_message(messages[-1].content)):
        return messages[:-1].extend([SystemMessage('Пользователь написал сообщение на запрещенные темы')])
    
    response = model_tools.invoke(messages)


    for tool_call in response.tool_calls:
        tool_name = tool_call["name"].lower()
        selected_tool = tools.get(tool_name, None)

        if selected_tool:
            logger.debug(tool_call)
            
            if tool_call['args'].get('user_id'):
                tool_call['args']['user_id'] = id

            tool_msg = selected_tool.invoke(tool_call)

            logger.debug(tool_msg)

            messages.append(tool_msg)
    
    return messages


def llm_stream(response_model, model_tools, messages, tools, id = 0):
    return response_model.stream(__llm_get_tools_messages(model_tools, tools, messages, id))

def llm_invoke(response_model, model_tools, messages, tools, id = 0):
    return response_model.invoke(__llm_get_tools_messages(model_tools, tools, messages, id))

def convert_db_messages_to_llm_messages(db_messages):
    type = {
        'human': HumanMessage,
        'ai': AIMessage,
        'system': SystemMessage
    }
    return [type.get(msg.message_type, 'human')(msg.content)  for msg in db_messages]
    # Messages by db: (msg.message_type, msg.content, msg.timestamp)


# --------------------------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    # Load variables from custom environment
    load_keys()

    # Set keys 
    if not os.environ.get("OPENAI_API_KEY"):
        set_keys(['OPENAI'])

    # Save variables to custom enviroment 
    save_keys()



    # Init rag 
    RAG = get_default_init_rag()



    # -------------------------------------------------------------TEMP---------------------------------------------------------------

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

    # --------------------------------------------------------------------------------------------------------------------------------




    
    # Инициализация LLM с использованием OpenAI API
    model = ChatOpenAI(**LLM_CONFIG)

    

    if ("y" in input("Ручной режим?: (y/n) ")):
        messages = []


        while True:
            inp = input("QUERY (enter 'exit' to exit): ")
            if 'exit' == inp.strip().lower():
                break

            messages.append(HumanMessage(inp))
            model_tools = get_tools_llm(model, tools)
            model_response = get_response_llm(model)

            message = ''

            for chunk in llm_stream(model_response, model_tools, messages, tools):
                print(chunk.content, end='')
                message += chunk.content
            
            messages += '\n'

            messages.append(AIMessage(message))


    else:
        messages = []


        agent_executor = create_react_agent(model, tools.values())



        while True:
            inp = input("QUERY (enter 'exit' to exit): ")
            if 'exit' == inp.strip().lower():
                break

            messages.append(HumanMessage(inp))

            for chunk in agent_executor.stream(
                {"messages": messages}
            ):
                print(chunk)
                print("----")
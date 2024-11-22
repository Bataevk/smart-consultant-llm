from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, ToolMessage, SystemMessage, AIMessage
from lightrag import QueryParam
# Agents
from langgraph.prebuilt import create_react_agent

from langchain.tools import tool

from utils import *
from graph_utils import get_default_init_rag

from icecream import ic

# Import chat side chats
from langchain_openai import ChatOpenAI



ic.enable()

WORKING_DIR = "./db_caches/"

config = {
    "base_url": "https://integrate.api.nvidia.com/v1",
    "model": "meta/llama-3.1-405b-instruct"
}


system_prompt = '''\
You are an AI-assistant created to consult citizens on government services and offerings.  
You help users find information and perform necessary functions. By default, you look for answers in the knowledge base. Always respond in **Russian**, providing detailed, comprehensive, and contextually appropriate answers. Avoid using English unless explicitly requested.  

Follow these steps depending on the user’s request:  

1. **Analyze the request**: Determine the type of request.  
   - If the request concerns **general information**, use the knowledge base to find the answer.  
   - If the request requires executing a **specific function** (e.g., retrieving, updating, or deleting data), proceed to the next step.  

2. **Execute the function**:  
   - Determine if there is an appropriate function to handle the request.  
     - **If the function exists**: Call it and get the result.  
     - **If the function does not exist**: Inform the user that no suitable function was found.  

3. **Respond to the request**:  
   - Always return the result of the function execution. If the function was executed successfully, formulate a response based on the obtained result. Ensure that the response is detailed and in **Russian**.  
   - If the function was unable to complete the task (execution error), provide a detailed error message with an explanation in **Russian**.  

# **Technical Recommendations:**  
- Always respond in **Russian**. Use a neutral and polite tone.  
- Provide detailed answers that fully cover the user’s question.  
- Use a question-answer structure for intuitive communication.  
- Offer step-by-step instructions when necessary.  

Ensure the instruction to answer in Russian is consistently applied, and reinforce it with examples if needed.  
'''




# --------------------------------------------------------------------------------------------------------------------------------
@tool
def search(query: str) -> str:
    """Search for an answer in the knowledge base.

    Parameters:
        query: Formulate the question clearly and in Russian, replacing pronouns or vague terms with precise nouns or phrases so the question can stand alone without additional context.

    Returns:
        A list of answers or the most relevant response from the knowledge base.
    """

    ic('-------------------------------- USE Graph Search --------------------------------')
    ic('QUERY : ' + query)

    return RAG.query(query, param=QueryParam(mode="hybrid", only_need_context = True))

@tool
def multiply(a: int, b: int) -> int:
    """Multiply a and b."""
    return a * b


tools = {'search': search, 'multiply': multiply}
# --------------------------------------------------------------------------------------------------------------------------------

def get_chain(model):
    # Создание цепочки запросов для LangChain с использованием инструментов
    # response_prompt = PromptTemplate.from_template(response_template)

    # Binding tools
    llm_tools = model.bind_tools(tools.values())

    # Create language chain
    # llm_chain = response_prompt | llm_tools

    return llm_tools


def model_invoke(model, messages):
    response = model.invoke(messages)

    for tool_call in response.tool_calls:
        tool_name = tool_call["name"].lower()
        selected_tool = tools.get(tool_name, None)
        if selected_tool:
            if tool_name == 'search':
                return RAG.query(ic(tool_call['args']['query']), param=QueryParam(mode="hybrid", only_need_context = False))

            tool_msg = selected_tool.invoke(tool_call)
            messages.append(tool_msg)
    
    return model.invoke(messages)

    # for chunk in model.stream(messages):
    #     yield chunk



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
    
    # Инициализация LLM с использованием OpenAI API
    model = ChatOpenAI(**config)

    messages = [
        SystemMessage(system_prompt),
        HumanMessage(input("QUERY: "))
    ]
    

    if ("y" in input("Ручной режим?: (y/n) ")):
        model_chain = get_chain(model)

        print(model_invoke(model_chain, messages))


    else:
        tools = [search, multiply]
        agent_executor = create_react_agent(model, tools)

        for chunk in agent_executor.stream(
            {"messages": messages}
        ):
            print(chunk)
            print("----")
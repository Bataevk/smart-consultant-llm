# Langchain imports
# from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
from langchain_core.prompts import PromptTemplate
# from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain.tools import tool

from utils import *
from graph_utils import get_default_init_rag


# Import chat side chats
from langchain_openai import ChatOpenAI

from lightrag import LightRAG, QueryParam



WORKING_DIR = "./db_caches/"


BASE_TEMPLATE = '''\
## Task:
You are a ai-assistant created to consult citizens on government services and offerings. Your task is to help users find information, answer questions, and provide recommendations in the following categories:

1. **Utilities**: Questions about payment of utility bills, contract agreements, submitting repair or maintenance requests.
2. **Healthcare**: Consultations regarding appointment booking, mandatory health insurance policy issuance, vaccinations, and the operation of medical institutions.
3. **Education**: Information about kindergartens, schools, universities, admission rules, benefits, and supplemental education programs.
4. **Transportation**: Public transport schedules, issuing discounted travel passes, information about fines, and vehicle registration.

**Functional Requirements:**

- Respond to questions very detailed, clearly, and directly.
- If a question goes beyond your functionality, politely redirect the user to the appropriate government services.
- Communication style: polite, neutral, with an emphasis on helpfulness and information accessibility.
- The response format should include:
  - Plain text with specific information.
  - Additional links to official resources, if available.
  - Ask clarifying questions if necessary to better understand the user's request.

**For answering questions in the main four areas (Utilities, Healthcare, Education, Transportation)**, use the function to search for answers in the knowledge base. This will ensure the accuracy and relevance of the information. 
  For example:
- For questions about utility bill payments or booking an appointment with a doctor, queries should be executed through a knowledge base containing up-to-date information on tariffs, services, and available offerings.
- For obtaining information on school rules or transportation services, the database should also be utilized.
  

**For processing requests related to personal user information**, such as:
- viewing meter readings (e.g., water, gas, electricity meters),
- the time to book an appointment with a doctor,
- the amount of the current fine,
invoke the relevant functions to handle these requests. 


**Technical Recommendations:**
- Ensure the model understands the context of user inquiries.
- Use a question-answer structure for intuitive communication.
- Provide step-by-step instructions when necessary.

**Working with Functions:**
- For requests involving personal data (meters, fines, doctor appointments), invoke the relevant functions.
- For other questions (general consultations), use the knowledge base for answers.


## Input Format:
Chat History: 
```
{chat_history}
```
Question: {question}

'''


config = {
    "base_url": "https://integrate.api.nvidia.com/v1",
    "model": "nvidia/llama-3.1-nemotron-70b-instruct"
}




@tool
def search(query: str) -> str:
    """search for an answer in the knowledge base.
    
    parameters:
        query: For the query parameter, formulate questions in such a way that they are as detailed and understandable as possible. All pronouns and vague terms should be replaced with corresponding nouns or phrases so that questions can be used as stand-alone queries without the need for additional context.
    
    returns a list of answers
    """

    return RAG.query(query, only_need_context = True)


    

def get_chain(llm, response_template):
    # Создание цепочки запросов для LangChain с использованием инструментов
    response_prompt = PromptTemplate.from_template(response_template)

    llm.bind_tools([search])
    llm_chain = response_prompt | llm

    return llm_chain



if __name__ == '__main__':
    # Load variables from custom environment
    load_keys()

    # Set keys 
    if not os.environ.get("OPENAI_API_KEY") or True:
        set_keys(['OPENAI','NVIDIA'])

    # Save variables to custom enviroment 
    save_keys()

    
    # Инициализация LLM с использованием OpenAI API
    llm = ChatOpenAI(**config)

    # Init rag 
    RAG = get_default_init_rag()


    llm_chain = get_chain(llm, BASE_TEMPLATE)


    # Запрос на выполнение
    query = {"question": "Как заплатить за ЖКХ?", "chat_history": []}
    response = llm_chain.invoke(query)
    print(response)

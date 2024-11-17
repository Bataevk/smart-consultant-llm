# Langchain imports
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from utils import *


# Import chat side chats
from langchain_openai import ChatOpenAI

from lightrag import LightRAG, QueryParam



WORKING_DIR = "./db_caches/"

rephrase_prompt = '''\

**Task:** You are an advanced text processing model. Your goal is to take the provided chat history and question, then reformulate the question to be more detailed and self-contained. In your response, replace pronouns and vague references with specific nouns and subject matter, ensuring the final question can stand alone without needing the chat history.

**Input Format:**

1. **Chat History:** 
```
{chat_history}
```

2. **Question:** {question}

**Instructions:** 
- Analyze the chat history to understand the context and key subjects discussed.
- Identify and replace all pronouns and ambiguous terms in the question with their corresponding nouns or phrases.
- Ensure that the newly structured question flows logically and makes sense without requiring any additional context.
'''


# Example
'''
**Example:**
1. **Chat History:**  
   User: "Can you tell me how it works?"  
   Assistant: "Sure! It helps people with their tasks."  

2. **Question:** "What is it?"

**Expected Output:**  
"What is the tool that assists people with their tasks, and how does it work?"
'''


response_prompt = '''\
Task: You are an advanced text processing model. Your job is to analyze the provided chat history, user question, and detailed answer from an external source, then generate a contextually relevant response to the user's question, incorporating relevant information from all inputs.

Input Format:

Chat History: 
```
{chat_history}
```
Question: {question}

Detailed Answer:
```
{context}
```

Instructions:

Review the chat history to understand the context of the conversation, including previous questions and answers.
Analyze the user’s question to determine its intent and what specific information the user is seeking.
Consider the detailed answer from the external source as a reference, incorporating its relevant insights while ensuring your response is tailored to the user's question and the overall context of the chat.
Ensure that your response is clear, concise, and directly addresses the user's question.
'''


config = {
    "base_url": "https://openrouter.ai/api/v1",
    "model": "liquid/lfm-40b:free",
    "temperature": 0.3
}






def call_lightrag_directly(query):
    # Query to lightrag
    pass



def get_chain(llm, response_template: str, rephrase_template: str):
    # Создание цепочки запросов для LangChain
    # langchain for query with rephrase and rag

    # Шаблоны для ответа и перефразирования
    response_prompt = PromptTemplate.from_template(response_template)
    rephrase_prompt = PromptTemplate.from_template(rephrase_template)

    # RAG-цепочка с LightRAG через прямой вызов
    light_rag_chain = rephrase_prompt | llm | RunnableLambda(call_lightrag_directly)

    parallel_chain = RunnableParallel(
        {
            "question": RunnableLambda(lambda inputs: inputs['question']),
            "context": light_rag_chain,
            "chat_history": RunnableLambda(lambda inputs: inputs['chat_history'])
        }
    )
    

    # Основная последовательная цепочка обработки и LLM ответа
    main_chain = parallel_chain | response_prompt | llm
    return main_chain


if __name__ == '__main__':
    # Инициализация LLM с использованием OpenAI API
    llm = ChatOpenAI(config)
    # Load variables from custom environment
    load_keys()

    # Set keys 
    if not os.environ.get("OPENAI_API_KEY") or True:
        set_keys(['OPENAI','NVIDIA'])

    # Save variables to custom enviroment 
    save_keys()

    llm_chain = get_chain(llm, response_prompt, rephrase_prompt)


    # Запрос на выполнение
    query = {"question": "Какие задачи решает LightRAG?"}
    response = llm_chain.run(query)
    print(response)

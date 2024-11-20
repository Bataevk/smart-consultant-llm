import os
from lightrag import LightRAG, QueryParam
from lightrag.llm import hf_embedding, openai_complete_if_cache
from transformers import AutoModel, AutoTokenizer
from lightrag.utils import EmbeddingFunc



#########
# Uncomment the below two lines if running in a jupyter notebook to handle the async nature of rag.insert()
# import nest_asyncio
# nest_asyncio.apply()
#########

async def llm_model_func(
    prompt, system_prompt=None, history_messages=[], **kwargs
) -> str:
    return await openai_complete_if_cache(
        "nvidia/llama-3.1-nemotron-70b-instruct",
        prompt,
        system_prompt=system_prompt,
        history_messages=history_messages,
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url="https://integrate.api.nvidia.com/v1",
        **kwargs
    )
    # return await openai_complete_if_cache(
    #     "meta-llama/llama-3.2-3b-instruct:free",
    #     prompt,
    #     system_prompt=system_prompt,
    #     history_messages=history_messages,
    #     api_key=os.getenv("OPENAI_API_KEY"),
    #     base_url="https://openrouter.ai/api/v1",
    #     **kwargs
    # )


def init_db_directory(name_directory):    
    if not os.path.exists(name_directory):
        os.mkdir(name_directory)


def init_rag(working_dir, model, files_dir = './inputs/' ,loaded_files = True):
    init_db_directory(working_dir)
    rag = LightRAG(
        working_dir=working_dir,
        llm_model_func=model,
        # Use Hugging Face embedding function
        embedding_func=EmbeddingFunc(
            embedding_dim=384,
            max_token_size=5000,
            func=lambda texts: hf_embedding(
                texts,
                tokenizer=AutoTokenizer.from_pretrained("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"),
                embed_model=AutoModel.from_pretrained("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
            )
        ),
    )

    if loaded_files:
        for file in os.listdir(files_dir):
            if file.endswith(".txt"):
                with open(os.path.join(files_dir, file), 'r', encoding = "utf-8") as f:
                    rag.insert(f.read())


    return rag



def get_default_init_rag(loaded_files = False, working_dir="./.db_caches/", files_dir='./.inputs'):
    return init_rag(
        working_dir = working_dir, 
        model = llm_model_func, 
        files_dir = files_dir, 
        loaded_files=loaded_files
    )



if __name__ == '__main__':
    from utils import load_keys

    load_keys()

    WORKING_DIR = "./.db_caches/"
    rag = init_rag(
        working_dir = WORKING_DIR, 
        model = llm_model_func , 
        files_dir='./.inputs', 
        loaded_files=True 
    )

    # # Perform naive search
    # print(rag.query("What are the top themes in this story?", param=QueryParam(mode="naive")))

    # # Perform local search
    # print(rag.query("What are the top themes in this story?", param=QueryParam(mode="local")))

    # # Perform global search
    # print(rag.query("What are the top themes in this story?", param=QueryParam(mode="global")))

    # Perform hybrid search
    print(rag.query("What are the top themes in this story?", param=QueryParam(mode="hybrid")))


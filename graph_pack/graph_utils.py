import os
from lightrag import LightRAG, QueryParam
from lightrag.llm import hf_embedding, openai_complete_if_cache
from transformers import AutoModel, AutoTokenizer
from lightrag.utils import EmbeddingFunc
from config import WORKING_DIR, LLM_CONFIG, DOCUMENTS_DIR



async def llm_model_func(
    prompt, system_prompt=None, history_messages=[], **kwargs
) -> str:
    return await openai_complete_if_cache(
        LLM_CONFIG['model'],
        prompt,
        system_prompt=system_prompt,
        history_messages=history_messages,
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=LLM_CONFIG['base_url'],
        **kwargs
    )


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
    # загрузка сущностей из файлов в граф
    from utils import load_keys

    load_keys()

    rag = init_rag(
        working_dir = WORKING_DIR, 
        model = llm_model_func , 
        files_dir=DOCUMENTS_DIR, 
        loaded_files=False 
    )

    print('Загрузка выполнена!')

    # Perform hybrid search - other: (native, local, global)
    while True:
        print(rag.query(input('User query: '), param=QueryParam(mode="hybrid" , only_need_context=False)))


# Сторонние импорты
from icecream import ic
from langchain.tools import tool  
from lightrag import QueryParam
import logging

# Локальные импорты
from graph_pack.graph_utils import get_default_init_rag
from config import GRAPH_SEARCH_MODE

def get_search_tool(RAG):
    @tool
    def search(query: str) -> str:
        """Search for an answer in the knowledge base.

        Parameters:
            query: Formulate the question clearly and in Russian, replacing pronouns or vague terms with precise nouns or phrases so the question can stand alone without additional context.

        Returns:
            A list of answers or the most relevant response from the knowledge base.
        """
        logging.debug('-------------------------------- USE Graph Search --------------------------------')
        logging.debug('QUERY : ' + query)

        return RAG.query(query, param=QueryParam(mode=GRAPH_SEARCH_MODE, only_need_context = False))
    return search
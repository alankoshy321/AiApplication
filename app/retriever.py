from langchain.chains import RetrievalQA
from langchain_community.llms import GPT4All
from langchain_community.vectorstores import Weaviate
from langchain_core.embeddings import Embeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.language_models.llms import BaseLLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from typing import Any, List, Optional
import weaviate
import os

from app.config import Settings
from app.ingest import ensure_schema


class WeaviateVectorRetriever(BaseRetriever):
    """Custom retriever using Weaviate's nearVector API."""
    
    client: weaviate.Client
    collection_name: str
    embeddings: Embeddings
    k: int = 3
    
    def __init__(self, client: weaviate.Client, collection_name: str, 
                 embeddings: Embeddings, k: int = 3, **kwargs):
        super().__init__(client=client, collection_name=collection_name, 
                        embeddings=embeddings, k=k, **kwargs)
    
    def _get_relevant_documents(self, query: str) -> List[Document]:
        """Retrieve documents using vector similarity."""
        query_vector = self.embeddings.embed_query(query)
        
        result = (
            self.client.query
            .get(self.collection_name, ["text", "source", "title"])
            .with_near_vector({"vector": query_vector})
            .with_limit(self.k)
            .do()
        )
        
        docs = []
        if "data" in result and "Get" in result["data"]:
            for item in result["data"]["Get"].get(self.collection_name, []):
                docs.append(Document(
                    page_content=item.get("text", ""),
                    metadata={
                        "source": item.get("source", ""),
                        "title": item.get("title", "")
                    }
                ))
        return docs
    
    async def _aget_relevant_documents(self, query: str) -> List[Document]:
        return self._get_relevant_documents(query)


class MockLLM(BaseLLM):
    """Simple mock LLM for demonstration when GPT4All is unavailable."""
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        # Return a simple response based on the prompt
        if "question" in prompt.lower() or "query" in prompt.lower():
            return "Based on the retrieved documents, this appears to be a relevant answer to your question."
        return "This is a generated hypothetical document that would answer the user question."

    def _generate(
        self,
        prompts: List[str],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Any:
        from langchain_core.outputs import LLMResult, Generation
        generations = []
        for prompt in prompts:
            text = self._call(prompt, stop=stop, run_manager=run_manager, **kwargs)
            generations.append([Generation(text=text)])
        return LLMResult(generations=generations)

    @property
    def _llm_type(self) -> str:
        return "mock"


class SimpleHydeEmbedder(Embeddings):
    """Simple HyDE embedder that generates hypothetical documents and embeds them."""
    
    def __init__(self, llm: BaseLLM, base_embeddings: Embeddings):
        self.llm = llm
        self.base_embeddings = base_embeddings
        self.prompt_template = PromptTemplate(
            input_variables=["input"],
            template="Generate a short passage that would answer the user question. Keep it concise.\n\nQuestion: {input}"
        )
    
    def embed_query(self, query: str) -> list[float]:
        """Generate hypothetical document and embed it."""
        # Generate hypothetical document
        prompt = self.prompt_template.format(input=query)
        hypothetical_doc = self.llm.invoke(prompt)
        # Embed the hypothetical document instead of the query
        return self.base_embeddings.embed_query(hypothetical_doc)
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed documents (for compatibility)."""
        return self.base_embeddings.embed_documents(texts)


def build_vectorstore(
    client: weaviate.Client,
    settings: Settings,
    embeddings: Embeddings,
    hyde_embedder: SimpleHydeEmbedder | None = None,
) -> Weaviate:
    ensure_schema(client, settings.collection_name)
    embed_fn = hyde_embedder.embed_query if hyde_embedder else embeddings.embed_query
    return Weaviate(
        client=client,
        index_name=settings.collection_name,
        text_key="text",
        embedding=embed_fn,
        attributes=["source", "title"],
    )


def build_llm(settings: Settings) -> BaseLLM:
    """Build LLM, falling back to MockLLM if GPT4All fails."""
    # Try to use GPT4All if available, otherwise use mock
    use_mock = os.getenv("USE_MOCK_LLM", "false").lower() == "true"
    if use_mock:
        return MockLLM()
    
    try:
        return GPT4All(
            model=settings.gpt4all_model, 
            verbose=False,
            allow_download=True,
            model_path="/root/.cache/gpt4all"
        )
    except Exception as e:
        print(f"Warning: GPT4All initialization failed ({e}), using MockLLM")
        return MockLLM()


def build_chain(
    client: weaviate.Client, collection_name: str, embeddings: Embeddings, 
    llm: BaseLLM, k: int = 3
) -> RetrievalQA:
    retriever = WeaviateVectorRetriever(client, collection_name, embeddings, k)
    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
    )


def build_hyde_embedder(llm: BaseLLM, base_embeddings: Embeddings) -> SimpleHydeEmbedder:
    return SimpleHydeEmbedder(llm=llm, base_embeddings=base_embeddings)



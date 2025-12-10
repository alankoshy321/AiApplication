from pathlib import Path
from typing import Iterable
import logging

from langchain.docstore.document import Document
from langchain_community.vectorstores import Weaviate
from langchain_core.embeddings import Embeddings
import weaviate

logger = logging.getLogger(__name__)


def load_pdf(path: Path) -> list[Document]:
    """Load text from PDF file."""
    try:
        import PyPDF2
        documents = []
        with open(path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for i, page in enumerate(pdf_reader.pages):
                text = page.extract_text().strip()
                if text:
                    documents.append(
                        Document(
                            page_content=text,
                            metadata={
                                "source": str(path.name),
                                "title": path.stem,
                                "page": i + 1,
                            },
                        )
                    )
        return documents
    except ImportError:
        logger.warning("PyPDF2 not installed. Install with: pip install PyPDF2")
        return []
    except Exception as e:
        logger.error(f"Error reading PDF {path}: {e}")
        return []


def load_documents(data_path: str) -> list[Document]:
    """Load documents from various file formats."""
    base = Path(data_path)
    documents: list[Document] = []
    
    # Load text files
    for path in base.glob("**/*.txt"):
        try:
            text = path.read_text(encoding="utf-8").strip()
            if text:
                documents.append(
                    Document(
                        page_content=text,
                        metadata={"source": str(path.relative_to(base)), "title": path.stem},
                    )
                )
        except Exception as e:
            logger.error(f"Error reading {path}: {e}")
    
    # Load PDF files
    for path in base.glob("**/*.pdf"):
        pdf_docs = load_pdf(path)
        documents.extend(pdf_docs)
    
    # Load markdown files
    for path in base.glob("**/*.md"):
        try:
            text = path.read_text(encoding="utf-8").strip()
            if text:
                documents.append(
                    Document(
                        page_content=text,
                        metadata={"source": str(path.relative_to(base)), "title": path.stem},
                    )
                )
        except Exception as e:
            logger.error(f"Error reading {path}: {e}")
    
    logger.info(f"Loaded {len(documents)} documents from {data_path}")
    return documents


def ensure_schema(client: weaviate.Client, class_name: str, text_key: str = "text") -> None:
    schema = client.schema.get()
    existing = {c["class"] for c in schema.get("classes", [])}
    if class_name in existing:
        return
    client.schema.create_class(
        {
            "class": class_name,
            "description": "Simple document store",
            "properties": [
                {"dataType": ["text"], "name": text_key},
                {"dataType": ["text"], "name": "source"},
                {"dataType": ["text"], "name": "title"},
            ],
            "vectorizer": "none",
        }
    )


def ingest_documents(
    client: weaviate.Client,
    embeddings: Embeddings,
    collection_name: str,
    documents: Iterable[Document],
) -> int:
    ensure_schema(client, collection_name)
    docs_list = list(documents)
    vectorstore = Weaviate(
        client=client,
        index_name=collection_name,
        text_key="text",
        embedding=embeddings,
        attributes=["source", "title"],
    )
    if docs_list:
        vectorstore.add_documents(docs_list)
    return len(docs_list)


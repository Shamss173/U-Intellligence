"""
RAG Service with Chroma Vector Database Integration and Google Gemini
Provides document ingestion, retrieval, and LLM-based response generation.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from pathlib import Path
import logging
import os

# Load .env file first
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

from app.core.config import settings

logger = logging.getLogger(__name__)

# Import dependencies
try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    logger.warning("Chroma not installed. Install with: pip install chromadb")

try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.document_loaders import PyPDFLoader, TextLoader
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logger.warning("LangChain not installed. Install with: pip install langchain pypdf")

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError as e:
    GEMINI_AVAILABLE = False
    logger.warning(f"Google Generative AI not installed. Install with: pip install google-generativeai. Error: {e}")
except Exception as e:
    GEMINI_AVAILABLE = False
    logger.warning(f"Error importing Google Generative AI: {e}")


class RAGServiceInterface(ABC):
    """Abstract interface for RAG operations"""
    
    @abstractmethod
    async def ingest_document(self, department_id: str, file_path: str, metadata: Dict) -> bool:
        """Ingest a document into department-specific RAG database"""
        pass
    
    @abstractmethod
    async def query(self, department_id: str, query: str, context: Optional[List[Dict]] = None) -> str:
        """Query the RAG database for department-specific information"""
        pass
    
    @abstractmethod
    async def delete_document(self, department_id: str, document_id: str) -> bool:
        """Delete a document from RAG database"""
        pass


class GeminiRAGService(RAGServiceInterface):
    """
    RAG Service Implementation using Chroma Vector Database and Google Gemini
    Integrates with Gemini for embeddings and LLM responses.
    """
    
    _initialized = False  # Class variable to track if already initialized
    
    def __init__(self):
        import uuid
        self.instance_id = str(uuid.uuid4())[:8]
        self.enabled = settings.RAG_ENABLED
        self.client = None
        self.gemini_client = None
        
        logger.info(f"RAG Service initializing [ID: {self.instance_id}]. RAG_ENABLED: {settings.RAG_ENABLED}")
        
        if self.enabled:
            self._initialize_services()
        
        logger.info(f"RAG Service initialized [ID: {self.instance_id}]. Enabled: {self.enabled}, Client: {self.client is not None}, Gemini: {self.gemini_client is not None}")
    
    def _initialize_services(self):
        """Initialize Chroma and Gemini clients"""
        logger.info("Initializing RAG services...")
        
        if not CHROMA_AVAILABLE:
            logger.error("Chroma not available. RAG disabled.")
            self.enabled = False
            return
        
        if not GEMINI_AVAILABLE:
            logger.error("Google Generative AI not available. RAG disabled.")
            self.enabled = False
            return
        
        if not settings.GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY not set. RAG disabled.")
            self.enabled = False
            return
        
        try:
            # Initialize Chroma client with persistent storage
            chroma_path = Path(settings.RAG_VECTOR_DB_PATH)
            chroma_path_absolute = chroma_path.absolute()
            chroma_path.mkdir(parents=True, exist_ok=True)
            
            logger.debug(f"Initializing Chroma at {chroma_path_absolute}")
            
            self.client = chromadb.PersistentClient(
                path=str(chroma_path_absolute),
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # List collections to verify connection
            collections = self.client.list_collections()
            collection_names = [c.name for c in collections]
            logger.info(f"Chroma initialized. Collections: {collection_names}")
            
            # Initialize Gemini client
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.gemini_client = genai
            
            logger.info("RAG services initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RAG services: {e}", exc_info=True)
            self.enabled = False
    
    def _get_collection(self, department_id: str):
        """Get or create a collection for a department"""
        if not self.client:
            return None
        
        collection_name = f"dept_{department_id}".replace("-", "_").lower()
        return self.client.get_or_create_collection(
            name=collection_name,
            metadata={"department": department_id}
        )
    
    def _load_document(self, file_path: str) -> str:
        """Load document content based on file type"""
        file_ext = Path(file_path).suffix.lower()
        
        try:
            if file_ext == ".pdf":
                if not LANGCHAIN_AVAILABLE:
                    logger.error("LangChain required for PDF parsing")
                    return ""
                loader = PyPDFLoader(file_path)
                pages = loader.load()
                return "\n".join([page.page_content for page in pages])
            
            elif file_ext in [".txt", ".doc", ".docx"]:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            
            else:
                logger.warning(f"Unsupported file type: {file_ext}")
                return ""
        
        except Exception as e:
            logger.error(f"Error loading document {file_path}: {e}")
            return ""
    
    def _chunk_document(self, content: str) -> List[str]:
        """Split document into chunks"""
        if not LANGCHAIN_AVAILABLE:
            # Fallback: simple chunking
            chunk_size = settings.RAG_CHUNK_SIZE
            chunks = []
            for i in range(0, len(content), chunk_size):
                chunks.append(content[i:i + chunk_size])
            return chunks
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.RAG_CHUNK_SIZE,
            chunk_overlap=settings.RAG_CHUNK_OVERLAP,
            separators=["\n\n", "\n", " ", ""]
        )
        return splitter.split_text(content)
    
    def _get_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using Gemini"""
        if not self.gemini_client:
            return []
        
        try:
            result = self.gemini_client.embed_content(
                model=settings.RAG_EMBEDDING_MODEL,
                content=text
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return []
    
    async def ingest_document(self, department_id: str, file_path: str, metadata: Dict) -> bool:
        """
        Ingest a document into department-specific RAG database
        """
        if not self.enabled:
            logger.info(f"RAG disabled. Document ingestion skipped for {department_id}: {file_path}")
            return True
        
        logger.info(f"Starting document ingestion: {file_path}")
        try:
            collection = self._get_collection(department_id)
            if not collection:
                logger.error(f"Failed to get collection for {department_id}")
                return False
            
            logger.info(f"Collection obtained: {collection.name}")
            
            # Load document
            content = self._load_document(file_path)
            if not content:
                logger.warning(f"No content extracted from {file_path}")
                return False
            
            logger.info(f"Document loaded, content length: {len(content)}")
            
            # Chunk document
            chunks = self._chunk_document(content)
            logger.info(f"Document split into {len(chunks)} chunks")
            
            # Add chunks to collection
            successful_chunks = 0
            for i, chunk in enumerate(chunks):
                chunk_id = f"{metadata['filename']}_{i}"
                embedding = self._get_embedding(chunk)
                
                if not embedding:
                    logger.warning(f"Failed to generate embedding for chunk {i}")
                    continue
                
                collection.add(
                    ids=[chunk_id],
                    embeddings=[embedding],
                    documents=[chunk],
                    metadatas=[{
                        **metadata,
                        "chunk_index": i,
                        "total_chunks": len(chunks)
                    }]
                )
                successful_chunks += 1
            
            logger.info(f"Successfully ingested {successful_chunks}/{len(chunks)} chunks for {file_path} into {department_id} collection")
            return True
        
        except Exception as e:
            logger.error(f"Error ingesting document: {e}", exc_info=True)
            return False
    
    async def query(self, department_id: str, query: str, context: Optional[List[Dict]] = None) -> str:
        """
        Query the RAG database and generate response using Gemini LLM
        Uses the pre-existing my_permanent_docs_v2 collection with 1024D embeddings
        """
        logger.debug(f"Query called [ID: {self.instance_id}]. Enabled: {self.enabled}")
        
        if not self.enabled:
            logger.info(f"RAG disabled. Returning placeholder response for {department_id}")
            return f"I understand you're asking about: {query}. RAG functionality is currently disabled."
        
        try:
            # List available collections to debug
            available_collections = self.client.list_collections()
            collection_names = [c.name for c in available_collections]
            logger.debug(f"Available collections: {collection_names}")
            
            if "my_permanent_docs_v2" not in collection_names:
                logger.error(f"Collection 'my_permanent_docs_v2' not found. Available: {collection_names}")
                return "Knowledge base not available."
            
            collection = self.client.get_collection(name="my_permanent_docs_v2")
            logger.debug(f"Using collection: {collection.name}, count: {collection.count()}")
            
            # Generate query embedding
            query_embedding = self._get_embedding(query)
            if not query_embedding:
                return "Unable to process your query. Please try again."
            
            # Try to query - if dimension mismatch, fall back to simple search
            try:
                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=settings.RAG_TOP_K
                )
                retrieved_docs = []
                if results and results['documents']:
                    retrieved_docs = results['documents'][0]
            except Exception as e:
                if "dimension" in str(e).lower():
                    logger.warning(f"Embedding dimension mismatch. Falling back to simple retrieval.")
                    all_docs = collection.get(limit=settings.RAG_TOP_K)
                    retrieved_docs = all_docs['documents'] if all_docs and all_docs['documents'] else []
                else:
                    raise
            
            if not retrieved_docs:
                return f"I couldn't find relevant information about '{query}' in the knowledge base."
            
            # Build context for LLM
            context_text = "\n\n".join(retrieved_docs)
            
            # Generate response using LLM
            response = self._generate_response(query, context_text, context)
            return response
        
        except Exception as e:
            logger.error(f"Error querying RAG: {e}", exc_info=True)
            return "An error occurred while processing your query."
    
    def _generate_response(self, query: str, context: str, conversation_context: Optional[List[Dict]] = None) -> str:
        """Generate response using Gemini LLM"""
        if not self.gemini_client:
            return "LLM service unavailable."
        
        try:
            # Build system prompt
            system_prompt = """You are a helpful assistant for a department-specific knowledge base. 
Answer questions based on the provided context. If the context doesn't contain relevant information, 
say so clearly. Be concise and professional."""
            
            # Build messages
            messages = [
                f"System: {system_prompt}",
                f"Context:\n{context}",
                f"Question: {query}"
            ]
            
            # Add conversation context if available
            if conversation_context:
                for msg in conversation_context[-4:]:  # Last 4 messages for context
                    messages.insert(1, f"{msg['role'].capitalize()}: {msg['content']}")
            
            # Combine all messages
            full_prompt = "\n\n".join(messages)
            
            # Call Gemini LLM
            model = self.gemini_client.GenerativeModel(settings.RAG_LLM_MODEL)
            response = model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=settings.RAG_LLM_TEMPERATURE,
                    max_output_tokens=settings.RAG_LLM_MAX_TOKENS,
                )
            )
            
            return response.text
        
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "Unable to generate response at this time."
    
    async def delete_document(self, department_id: str, document_id: str) -> bool:
        """
        Delete a document from RAG database
        """
        if not self.enabled:
            logger.info(f"RAG disabled. Document deletion skipped")
            return True
        
        try:
            collection = self._get_collection(department_id)
            if not collection:
                return False
            
            # Delete all chunks for this document
            # Chroma doesn't have direct document deletion, so we delete by ID pattern
            results = collection.get(
                where={"filename": {"$eq": document_id}}
            )
            
            if results and results['ids']:
                collection.delete(ids=results['ids'])
                logger.info(f"Deleted {len(results['ids'])} chunks for document {document_id}")
            
            return True
        
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return False


# Singleton instance with lazy initialization
_rag_service_instance = None

def get_rag_service():
    """Get or create the RAG service singleton"""
    global _rag_service_instance
    if _rag_service_instance is None:
        _rag_service_instance = GeminiRAGService()
    return _rag_service_instance

# For backward compatibility, create the instance at import time
rag_service = get_rag_service()


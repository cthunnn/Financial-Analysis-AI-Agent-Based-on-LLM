"""
backend/app/rag/knowledge_base.py
知识库管理器 - 负责文档加载、文本分块与向量化存储
"""
import uuid
import hashlib
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from app.core.llm import get_llm_service, LLMService
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class ChunkResult:
    """文档分块结果"""
    chunk_id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None


class KnowledgeBaseManager:
    """
    知识库管理器
    核心职责：文档加载 -> 文本分块 -> 向量化 -> 持久化存储
    """

    def __init__(self, llm_service: Optional[LLMService] = None):
        self.llm = llm_service or get_llm_service()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len,
            separators=["\n\n", "\n", ". ", ". ", "! ", "? ", "; ", ", ", " ", ""],
        )
        self._collection = None

    @property
    def collection(self):
        """延迟获取 ChromaDB 集合"""
        if self._collection is None:
            try:
                import chromadb
                from chromadb.config import Settings as ChromaSettings

                client = chromadb.PersistentClient(
                    path=settings.CHROMA_PERSIST_DIR,
                    settings=ChromaSettings(anonymized_telemetry=False),
                )
                self._collection = client.get_or_create_collection(
                    name=settings.CHROMA_COLLECTION_NAME,
                    metadata={"hnsw:space": "cosine"},
                )
                logger.info(f"[知识库] ChromaDB 已连接: {settings.CHROMA_COLLECTION_NAME}")
            except ImportError:
                logger.warning("[知识库] ChromaDB 未安装，向量存储不可用")
                self._collection = None
        return self._collection

    def chunk_documents(
        self,
        documents: List[Document],
        chunk_size: int = 500,
        chunk_overlap: int = 50,
    ) -> List[ChunkResult]:
        """将文档列表切分为文本块"""
        self.text_splitter.chunk_size = chunk_size
        self.text_splitter.chunk_overlap = chunk_overlap

        chunks = self.text_splitter.split_documents(documents)
        results = []

        for i, chunk in enumerate(chunks):
            chunk_id = str(uuid.uuid4())
            results.append(ChunkResult(
                chunk_id=chunk_id,
                content=chunk.page_content,
                metadata={
                    **chunk.metadata,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "content_hash": hashlib.md5(
                        chunk.page_content.encode()
                    ).hexdigest(),
                },
            ))

        logger.info(f"[知识库] 分块完成: {len(documents)} 篇文档 -> {len(results)} 个文本块")
        return results

    async def add_chunks_to_vectorstore(
        self, chunks: List[ChunkResult], batch_size: int = 100
    ) -> int:
        """将文本块向量化后存入 ChromaDB"""
        if not self.collection:
            logger.warning("[知识库] 向量存储未初始化，跳过写入")
            return 0

        texts = [c.content for c in chunks]
        metadatas = [c.metadata for c in chunks]
        ids = [c.chunk_id for c in chunks]

        total_added = 0
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_metas = metadatas[i:i + batch_size]
            batch_ids = ids[i:i + batch_size]

            embeddings = await self.llm.embed(batch_texts)
            self.collection.add(
                embeddings=embeddings,
                documents=batch_texts,
                metadatas=batch_metas,
                ids=batch_ids,
            )
            total_added += len(batch_texts)

        logger.info(f"[知识库] 已写入 {total_added} 个文本块到向量存储")
        return total_added

    async def add_text_chunks(
        self,
        texts: List[str],
        category: str = "general",
        metadata_list: Optional[List[Dict]] = None,
    ) -> int:
        """便捷方法：直接添加文本块到知识库"""
        results = []
        for i, text in enumerate(texts):
            meta = metadata_list[i] if metadata_list else {}
            results.append(ChunkResult(
                chunk_id=str(uuid.uuid4()),
                content=text,
                metadata={**meta, "category": category},
            ))
        return await self.add_chunks_to_vectorstore(results)

    def count_documents(self) -> int:
        """获取知识库中的文档块总数"""
        if self.collection:
            return self.collection.count()
        return 0


# 模块级单例
kb_manager = KnowledgeBaseManager()


def get_kb_manager() -> KnowledgeBaseManager:
    """获取知识库管理器单例"""
    return kb_manager

"""
backend/app/core/vectorstore.py
向量数据库统一抽象接口 - 屏蔽 ChromaDB / Milvus 等底层实现差异
"""
from typing import List, Dict, Any, Optional

from app.config import get_settings

settings = get_settings()


class VectorStoreInterface:
    """
    向量数据库统一接口
    当前支持 ChromaDB（开发环境）和 Milvus（生产环境）
    """

    def __init__(self, store_type: Optional[str] = None):
        self.store_type = store_type or settings.VECTORSTORE_TYPE
        self._client = None

    async def add(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
        ids: List[str],
    ) -> bool:
        """添加向量记录"""
        if self.store_type == "chroma":
            return await self._add_chroma(texts, embeddings, metadatas, ids)
        elif self.store_type == "milvus":
            return await self._add_milvus(texts, embeddings, metadatas, ids)
        return False

    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        filters: Optional[Dict] = None,
    ) -> List[Dict[str, Any]]:
        """向量相似度搜索"""
        if self.store_type == "chroma":
            return await self._search_chroma(query_embedding, top_k, filters)
        elif self.store_type == "milvus":
            return await self._search_milvus(query_embedding, top_k, filters)
        return []

    async def _add_chroma(self, texts, embeddings, metadatas, ids) -> bool:
        # TODO: 实现 ChromaDB 写入逻辑
        return True

    async def _search_chroma(self, query_embedding, top_k, filters) -> List[Dict]:
        # TODO: 实现 ChromaDB 搜索逻辑
        return []

    async def _add_milvus(self, texts, embeddings, metadatas, ids) -> bool:
        # TODO: 实现 Milvus 写入逻辑
        return True

    async def _search_milvus(self, query_embedding, top_k, filters) -> List[Dict]:
        # TODO: 实现 Milvus 搜索逻辑
        return []

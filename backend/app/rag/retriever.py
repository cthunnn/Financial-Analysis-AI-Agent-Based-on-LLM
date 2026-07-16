"""
backend/app/rag/retriever.py
混合检索器 - Dense 向量检索 + Cross-Encoder 重排序 + 查询扩展
"""
import logging
from typing import List, Dict, Any, Optional

from app.core.llm import get_llm_service, LLMService
from app.rag.knowledge_base import get_kb_manager, KnowledgeBaseManager

logger = logging.getLogger(__name__)


class HybridRetriever:
    """
    混合检索器
    检索流程：用户查询 -> 向量检索 -> 相似度过滤 -> Cross-Encoder 重排序 -> 返回Top-K结果
    """

    def __init__(self, llm_service: Optional[LLMService] = None):
        self.llm = llm_service or get_llm_service()
        self.kb = get_kb_manager()

    async def retrieve(
        self,
        query: str,
        top_k: int = 10,
        score_threshold: float = 0.5,
        filters: Optional[Dict[str, Any]] = None,
        enable_rerank: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        执行混合检索

        Args:
            query: 用户查询文本
            top_k: 最大返回数量
            score_threshold: 相似度最低阈值
            filters: ChromaDB 元数据过滤条件
            enable_rerank: 是否启用 Cross-Encoder 重排序

        Returns:
            检索结果列表，每条包含 chunk_id, content, score, metadata
        """
        logger.info(f"[检索器] 查询: {query[:50]}... top_k={top_k} rerank={enable_rerank}")

        # Step 1: 将查询向量化
        query_embedding = await self.llm.embed([query])
        if not query_embedding:
            logger.warning("[检索器] 查询向量化失败")
            return []
        query_vec = query_embedding[0]

        # Step 2: ChromaDB 向量检索
        collection = self.kb.collection
        if not collection:
            logger.warning("[检索器] 向量存储不可用")
            return []

        try:
            results = collection.query(
                query_embeddings=[query_vec],
                n_results=top_k * 2,  # 多取一些供重排序
                where=filters,
                include=["documents", "metadatas", "distances"],
            )

            if not results or not results.get("ids") or not results["ids"][0]:
                logger.info("[检索器] 未找到匹配结果")
                return []

            ids = results["ids"][0]
            documents = results["documents"][0]
            metadatas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]

            # 将 cosine distance 转换为 similarity score
            scores = [1.0 - d for d in distances]

            chunks = []
            for i in range(len(ids)):
                chunks.append({
                    "chunk_id": ids[i],
                    "content": documents[i],
                    "score": scores[i] if i < len(scores) else 0.0,
                    "metadata": metadatas[i] if i < len(metadatas) else {},
                })

        except Exception as e:
            logger.error(f"[检索器] ChromaDB 检索失败: {str(e)}")
            return []

        # Step 3: 按相似度阈值过滤
        chunks = [c for c in chunks if c["score"] >= score_threshold]

        # Step 4: Cross-Encoder 重排序
        if enable_rerank and len(chunks) > 1:
            chunks = await self._rerank(query, chunks, top_k=top_k)

        # Step 5: 截取 Top-K
        chunks = chunks[:top_k]

        logger.info(f"[检索器] 返回 {len(chunks)} 条结果")
        return chunks

    async def _rerank(
        self, query: str, chunks: List[Dict[str, Any]], top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """使用 Cross-Encoder 模型对检索结果进行重排序"""
        try:
            from sentence_transformers import CrossEncoder

            model = CrossEncoder(
                "cross-encoder/ms-marco-MiniLM-L-6-v2",
                max_length=512,
            )
            pairs = [(query, chunk["content"]) for chunk in chunks]
            scores = model.predict(pairs)

            for i, chunk in enumerate(chunks):
                chunk["rerank_score"] = float(scores[i])
                chunk["score"] = float(scores[i])

            chunks.sort(key=lambda x: x["rerank_score"], reverse=True)
            logger.info("[检索器] Cross-Encoder 重排序完成")
        except Exception as e:
            logger.warning(f"[检索器] 重排序失败（降级为原始排序）: {str(e)}")

        return chunks

    async def retrieve_with_expansion(
        self, query: str, top_k: int = 10, **kwargs
    ) -> List[Dict[str, Any]]:
        """带查询扩展的检索：生成多个同义查询并合并去重结果"""
        try:
            from langchain.schema import HumanMessage

            llm = get_llm_service()
            expansion_prompt = (
                f"请为以下金融分析查询生成3个同义表达，每行一个，不要有其他内容。\n"
                f"原始查询: {query}"
            )
            messages = [HumanMessage(content=expansion_prompt)]
            content, log = await llm.chat(messages, stream=False)

            expanded_queries = [query]
            if log.success and content:
                expanded_queries.extend(
                    [q.strip() for q in content.strip().split("\n") if q.strip()][:3]
                )

            all_chunks: Dict[str, Dict] = {}
            for q in expanded_queries:
                chunks = await self.retrieve(q, top_k=top_k // 2, **kwargs)
                for c in chunks:
                    cid = c["chunk_id"]
                    if cid not in all_chunks or c["score"] > all_chunks[cid]["score"]:
                        all_chunks[cid] = c

            merged = sorted(all_chunks.values(), key=lambda x: x["score"], reverse=True)
            return merged[:top_k]

        except Exception as e:
            logger.warning(f"[检索器] 查询扩展失败（降级为单查询）: {str(e)}")
            return await self.retrieve(query, top_k, **kwargs)


# 模块级单例
hybrid_retriever = HybridRetriever()


def get_hybrid_retriever() -> HybridRetriever:
    """获取混合检索器单例"""
    return hybrid_retriever

"""
scripts/seed_data.py
示例数据填充脚本 - 用于开发和测试环境
运行: python scripts/seed_data.py
"""
import asyncio
import uuid
from datetime import datetime


async def seed_users():
    """创建示例用户"""
    # TODO: 在数据库连接就绪后实现
    print("[Seed] 示例用户创建完成（待实现）")


async def seed_knowledge_base():
    """向知识库添加示例金融文档"""
    sample_docs = [
        {
            "title": "2024年A股市场展望",
            "category": "research",
            "content": (
                "2024年A股市场在宏观经济复苏、流动性宽松和政策支持等多重因素驱动下，"
                "有望呈现结构性行情。重点关注科技创新、新能源、消费复苏三大主线。"
                "其中半导体产业链尤其值得关注，国产替代进程加速将为相关企业带来持续增长动力。"
            ),
        },
        {
            "title": "贵州茅台2024年一季度经营数据",
            "category": "report",
            "content": (
                "贵州茅台2024年一季度实现营业收入约460亿元，同比增长18%。"
                "其中茅台酒收入约390亿元，系列酒收入约70亿元。"
                "直销渠道占比持续提升至45%以上，经销商渠道保持稳定。"
                "公司持续推进'i茅台'数字营销平台建设，线上销售渠道增长显著。"
            ),
        },
        {
            "title": "新能源汽车产业链投资分析",
            "category": "research",
            "content": (
                "新能源汽车产业链包括上游锂矿、中游电池材料、下游整车制造。"
                "2024年全球新能源汽车销量预计突破1700万辆，中国市场占比超过60%。"
                "电池级碳酸锂价格回落至10万元/吨以下，中游电池企业成本压力显著缓解。"
                "建议关注具有技术壁垒的电池龙头企业和海外布局领先的整车企业。"
            ),
        },
    ]

    # TODO: 在知识库服务就绪后实现实际写入
    print(f"[Seed] 已准备 {len(sample_docs)} 篇示例文档（待写入知识库）")


async def seed_prompts():
    """注册默认 Prompt 模板"""
    # TODO: 在数据库连接就绪后实现
    print("[Seed] Prompt 模板注册完成（待实现）")


async def main():
    print("=" * 60)
    print("Financial AI Agent - 示例数据填充")
    print("=" * 60)

    await seed_users()
    await seed_knowledge_base()
    await seed_prompts()

    print("\n[Seed] 数据填充完成")


if __name__ == "__main__":
    asyncio.run(main())

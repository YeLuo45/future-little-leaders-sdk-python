"""
FLL AI Summary API - FastAPI Server
V9: 成长报告 AI 总结生成服务
"""

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
import os

app = FastAPI(
    title="FLL AI Summary API",
    description="Future Little Leaders - AI Growth Summary Generation API",
    version="1.0.0"
)


class GrowthStatsRequest(BaseModel):
    baby_id: str
    baby_name: str
    period: str  # 'week' | 'month'
    stats: Dict[str, Any]
    achievements: List[Dict[str, str]]
    skill_tree_progress: Dict[str, int]


class GrowthSummaryResponse(BaseModel):
    summary: str
    strengths: List[str]
    suggestions: List[str]
    highlights: List[str]


def generate_template_summary(data: GrowthStatsRequest) -> GrowthSummaryResponse:
    """模板生成总结（当API不可用时的回退方案）"""
    stats = data.stats
    
    # 生成 summary
    current_streak = stats.get('current_streak', 0)
    tasks_completed = stats.get('tasks_completed', 0)
    
    if current_streak >= 30:
        summary = f"太厉害了！{data.baby_name}已经连续打卡{current_streak}天，你是最棒的！继续保持哦~"
    elif current_streak >= 7:
        summary = f"不错哦！{data.baby_name}已经连续打卡{current_streak}天了，继续加油！"
    elif tasks_completed >= 10:
        summary = f"{data.baby_name}本周完成了{tasks_completed}个任务，真是个任务小能手！"
    else:
        summary = f"{data.baby_name}本周完成了{tasks_completed}个任务，开始就是进步！"
    
    # 分析 strengths
    strengths = []
    if current_streak >= 7:
        strengths.append("连续打卡习惯好")
    if stats.get('completion_rate', 0) >= 0.8:
        strengths.append("任务完成率高")
    top_tags = stats.get('top_tags', [])
    if top_tags and top_tags[0].get('count', 0) >= 5:
        strengths.append(f"{top_tags[0].get('tag')}类任务表现突出")
    
    # 生成 suggestions
    suggestions = []
    tag_names = [t.get('tag', '') for t in top_tags]
    if '运动' not in tag_names:
        suggestions.append("建议增加运动类任务")
    if '习惯' not in tag_names:
        suggestions.append("建议加强习惯养成类任务")
    if current_streak < 3:
        suggestions.append("先从每日一个小任务开始培养连续习惯")
    
    # 检测 highlights
    highlights = []
    if tasks_completed > 10:
        highlights.append("单周完成任务数创新高")
    if current_streak >= stats.get('longest_streak', 0) and current_streak > 3:
        highlights.append("连续打卡天数追平历史记录")
    
    return GrowthSummaryResponse(
        summary=summary,
        strengths=strengths[:3],
        suggestions=suggestions[:3],
        highlights=highlights
    )


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "service": "FLL AI Summary API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check for monitoring"""
    return {"status": "healthy"}


@app.post("/api/v1/ai/growth-summary", response_model=GrowthSummaryResponse)
async def growth_summary(
    body: GrowthStatsRequest,
    authorization: Optional[str] = Header(None)
) -> GrowthSummaryResponse:
    """
    生成成长报告 AI 总结
    
    - 调用 OpenAI/MiniMax API 生成个性化的成长评语
    - Fallback: 当 API 不可用时返回模板生成的总结
    """
    # 检查是否提供了 API key
    api_key = None
    if authorization:
        if authorization.startswith("Bearer "):
            api_key = authorization[7:]
        else:
            api_key = authorization
    
    # 检查环境变量或使用模拟API
    env_api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("MINIMAX_API_KEY")
    
    if api_key or env_api_key:
        # TODO: 实现真实的 API 调用
        # 这里预留接口，实际部署时接入 OpenAI/MiniMax API
        # 使用 api_key 或 env_api_key 调用 LLM 服务
        pass
    
    # Fallback: 使用模板生成总结
    return generate_template_summary(body)


# CORS middleware for H5 frontend
@app.middleware("http")
async def add_cors_headers(request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
    return response


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )
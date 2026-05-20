from __future__ import annotations

import json
import os
from typing import Dict, List

import google.generativeai as genai


PROMPT_TEMPLATE = """
你是新闻编辑部的选题分析助手。请基于 topic 与新闻 signals，输出 JSON，结构必须为：
{
  "angles": [
    {
      "title": "",
      "explanation": "",
      "why_it_matters": ""
    }
  ],
  "keywords": [""]
}
要求：
1) angles 返回 3 条，偏调查与深度报道。
2) 语言必须是简体中文。
3) 只返回 JSON，不要 markdown。

Topic: {topic}
Signals: {signals}
""".strip()


FALLBACK = {
    "angles": [
        {
            "title": "政策执行与地方落地差异",
            "explanation": "对比中央政策与地方实施节奏，寻找执行层面的实际偏差。",
            "why_it_matters": "可以帮助记者识别政策与市场之间的真实摩擦点。",
        },
        {
            "title": "产业链关键环节压力测试",
            "explanation": "从上游供给到终端需求，梳理价格、库存和订单变化。",
            "why_it_matters": "揭示行业短期波动是否正在演变为结构性风险。",
        },
        {
            "title": "公众影响与消费者行为变化",
            "explanation": "观察用户反馈、投诉和购买决策变化，定位社会影响。",
            "why_it_matters": "让选题更贴近受众真实感受和公共利益。",
        },
    ],
    "keywords": ["政策落地", "产业链", "市场需求", "地方样本", "风险敞口"],
}


def generate_angles_and_keywords(topic: str, signals: List[Dict[str, str]]) -> Dict[str, List]:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return FALLBACK

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = PROMPT_TEMPLATE.format(topic=topic, signals=json.dumps(signals, ensure_ascii=False))
        response = model.generate_content(prompt)
        parsed = json.loads(response.text)
        angles = parsed.get("angles") or FALLBACK["angles"]
        keywords = parsed.get("keywords") or FALLBACK["keywords"]
        return {"angles": angles[:3], "keywords": keywords[:8]}
    except Exception:
        return FALLBACK

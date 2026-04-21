"""
Public snippet: Dynamic prompt injection with user context
"""

from datetime import datetime
from langchain.agents.middleware import dynamic_prompt, ModelRequest


@dynamic_prompt
def inject_user_context(request: ModelRequest) -> str:
    context = request.runtime.context or {}
    nickname = context.get("nickname", "익명")
    locale = context.get("locale", "ko-KR")
    ai_info = context.get("ai_info", "")
    base_prompt = context.get("base_prompt", "You are a helpful AI companion.")

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    return f"""
{base_prompt}

[Runtime Context]
- current_time: {now}
- user_nickname: {nickname}
- user_locale: {locale}
- user_ai_info: {ai_info if ai_info else 'N/A'}

Always personalize responses using the runtime context.
"""

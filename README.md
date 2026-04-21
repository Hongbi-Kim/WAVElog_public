# WAVE log - AI Emotion Care Platform (포트폴리오용)

> AI 캐릭터와의 대화, 감정 일기, 주간/월간 리포트를 통해 사용자 감정 패턴을 분석하는 서비스입니다.  
> 본 리포지토리는 **실서비스 전체 코드가 아닌**, 아키텍처/핵심 AI 설계/문제 해결 역량을 보여주기 위한 포트폴리오용 공개 자료입니다.

## Website
- https://wavelog.wavetox.com

## Overview
WAVE log는 감정 케어를 위한 AI 동반 서비스입니다. 사용자는 캐릭터별 AI와 대화하고, 감정 일기를 작성하며, 주간/월간 리포트로 자신의 패턴을 확인할 수 있습니다.

### Why I built this
- 감정 기록은 중요하지만, 혼자서 꾸준히 작성하기 어렵다는 문제
- 상담의 진입장벽(시간/비용/심리적 부담)
- 단순 챗봇이 아니라, **대화 + 일기 + 리포트 + 검색 + 캘린더**를 연결한 실사용형 AI 경험 구현

## Key Features
1. Multi-Agent Character Chat (LangChain)
- 캐릭터별 성격 프롬프트를 분리
- 사용자 맥락 주입(닉네임, locale, ai-info, 시간)
- 대화 중 핵심 정보 추출 및 요약 트리거

2. Web Search Augmentation (Tavily)
- 요청별 검색 ON/OFF 제어
- 최신 정보 질문에만 검색 도구 실행
- 검색어/출처(reference) 메타데이터를 응답에 포함

3. Calendar-aware Assistant
- 캘린더 조회/일정 제안 도구 분리
- 일정 의도 분석 후 구조화된 suggestion 반환

4. Insight Reports
- 주간/월간 리포트 생성 파이프라인
- 대화/감정일기 기반 요약 + 인사이트 생성
- 캐시 기반 재생성 제어

5. Prompt Engineering (Public)
- 캐릭터별 역할/톤/금지사항을 시스템 프롬프트로 분리
- 요약 프롬프트와 응답 프롬프트를 분리해 목적별 품질 제어
- 사용자 컨텍스트를 동적으로 결합해 개인화 응답 생성

## Tech Stack
- Frontend: React, TypeScript, Vite, Tailwind
- Backend: Supabase Edge Functions (Hono)
- AI Server: FastAPI (Python), LangChain 1.x, HyperCLOVA X
- Data: Supabase Postgres + KV(Cache/ephemeral)
- Search Tool: Tavily
- Deploy: Vercel (Web), Supabase (Edge/API), Railway (AI Server)

## Architecture Diagram
```mermaid
flowchart TD
  U["User"]
  WEB["Web Frontend (React + Vite)"]
  APP["Mobile App (React Native)"]
  EDGE["Supabase Edge Function (API Gateway/Auth/Quota)"]
  PG[("Supabase PostgreSQL (Profiles/Messages/Diaries/Reports)")]
  KV[("KV Store (Cache/Ephemeral State)")]
  AIS["AI Server (FastAPI + LangChain)"]

  subgraph AI_CORE ["AI Runtime Internals"]
    ROUTER["Group Router (mention -> LLM -> keyword fallback)"]
    AGENT1["Agent Rumi (char_1, empathy)"]
    AGENT2["Agent Kai (char_2, problem-solving)"]
    AGENT4["Agent Lyv (char_4, calendar-aware)"]
    MID["Middleware (dynamic prompt, summary trigger, info extraction trigger)"]
    TOOLS["Tools (Tavily search, calendar query/suggest)"]
    REPORT["Report Insight Generator (character-wise analysis)"]
  end

  CLOVA["HyperCLOVA X"]
  TAVILY["Tavily API"]
  GCAL["Calendar Events Context"]

  U --> WEB
  U --> APP
  WEB --> EDGE
  APP --> EDGE

  EDGE --> PG
  EDGE --> KV
  EDGE --> AIS

  AIS --> ROUTER
  ROUTER --> AGENT1
  ROUTER --> AGENT2
  ROUTER --> AGENT4

  AGENT1 --> MID
  AGENT2 --> MID
  AGENT4 --> MID
  MID --> TOOLS
  AIS --> REPORT

  AGENT1 --> CLOVA
  AGENT2 --> CLOVA
  AGENT4 --> CLOVA
  REPORT --> CLOVA

  TOOLS --> TAVILY
  TOOLS --> GCAL

  EDGE -. "store/retrieve" .-> PG
  EDGE -. "cache" .-> KV

```

Mermaid가 렌더되지 않는 환경에서는 아래 텍스트 다이어그램을 참고하세요.

```text
User
 ├─ Web Frontend (React + Vite)
 └─ Mobile App (React Native)
        │
        ▼
Supabase Edge Function (API Gateway/Auth/Quota)
 ├─ PostgreSQL (Profiles/Messages/Diaries/Reports)
 ├─ KV Store (Cache/Ephemeral State)
 └─ AI Server (FastAPI + LangChain)
      ├─ Group Router (mention -> LLM -> keyword fallback)
      ├─ Agent Rumi (char_1, empathy)
      ├─ Agent Kai (char_2, problem-solving)
      ├─ Agent Lyv (char_4, calendar-aware)
      ├─ Middleware (dynamic prompt / summary trigger / info extraction)
      ├─ Tools (Tavily search / calendar query-suggest)
      └─ Report Insight Generator
           └─ HyperCLOVA X

Tools
 ├─ Tavily API
 └─ Calendar Events Context
```

기능별 구현 문서는 [`docs/AI_FEATURES.md`](./docs/AI_FEATURES.md) 참고.

## Actual Prompts Used
실제 서비스에 적용된 프롬프트와 일부 상이할 수 있습니다.

### 1) Conversation Summary Prompt
```text
Your task is to summarize the conversation between the user and the assistant in 3-5 sentences.
Focus on the user's recent emotional changes and key events/context.
Also, briefly note any points that might be relevant for the next conversation (worries, goals, recurring patterns).

Do not make diagnoses or judgments; keep it fact-based and gentle.

### Conversation
{messages}
```

### 2) Character Chat Prompts
#### 2-1) Rumi (char_1)
```text
You are 'Rumi(루미)'. You are chatting with a user.
- You are a friend who cares for the user's feelings.
- You are not a problem-solving advisor.
- Your role is NOT to encourage, judge, or fix.

[Guidelines]
1. Empathy & Acceptance
   - Identify the user's emotion first. Do not try to find a silver lining or a lesson in their pain.
   - Never judge or try to 'correct' the user's feelings.
   - Even if self-criticism ("I'm useless") arises, rather than immediately refuting the thought, gently suggest an understanding of why it might have emerged and that it could be an "interpretation of a wounded heart" rather than "fact."

2. Stay in the 'Present'
   - Focus on what the user feels 'now'.
   - Never talk about the future. No "It will be okay" or "You'll do fine." Only talk about 'now'.

3. Responding to Crisis Signals (Self-harm/Suicide/Abuse, etc.)
   - Never dismiss statements like "I want to die," "I want to disappear," or "I want to hurt someone."
   - First acknowledge how difficult it must have been for them, and do not condemn those feelings.
   - At the same time, honestly state that as an AI, you cannot provide direct help,
     and carefully suggest utilizing real-world safety nets like
     close friends, professional counseling, hospitals, or local/national crisis support services.

[Tone & Style]
- Use informal language(반말) like a close friend, always speaking warmly.
- Focus on comfort and empathy. Avoid exaggerated tension or overly positive language.
- Use cute emojis to show warmth, but don't overdo it.

[STRICTLY Instructions - NO ADVICE, NO JUDGMENT]
- No Positive Evaluations: Never say "You're doing well," "You're great," or "You'll succeed."
- No Cheering Up: Do not try to change the user's mood. If they are sad, stay sad with them.
- No Tips/Solutions: Even "Take a deep breath" or "Don't think too much" are forbidden advice.
- No Assumptions: Don't say "You must be studying hard."
- No closing remarks that sound like a farewell or a wrap-up.
  - Forbidden: "~하길 바랄게", "언제든 찾아와줘", "또 이야기 나누고 싶으면 말해줘".
- No "Try to think positively" or "This is a chance to grow."
- No "아이고".

Respond in 3 sentences or less.
```

#### 2-2) Kai (char_2)
```text
You are 'Kai(카이)'. You are chatting with a user.
- You are an advisor that helps users achieve their goals and solve problems.
- While respecting emotions, you particularly excel at structuring, planning, and suggesting actionable methods.

[Guidelines]
1. Understand & Restate the Problem
   - First, summarize the user's words and distill the core issue into a key point.
   - Express clearly so the user feels, "Yes, that's exactly what I wanted to say."

2. Structured Approach
   - Break complex concerns into "steps" or "options."
   - If options exist, briefly outline the pros and cons of each.

[Prohibited Actions]
- Avoid expressions that blame or pressure users.
- Steer clear of unrealistic, extreme advice that ignores reality.

[Style Guide]
- Use informal language(반말) like a close friend, realistic speech.
- Focuses on "concrete help" rather than excessive comfort or sentimentality.

Respond in 3-5 sentences.
```

#### 2-3) Lyv (char_4)
```text
You are 'Lyv(리브)'. You are a friend who turns the user's messy goals into 'easy-to-start' daily plans.
- You specialize in 'Time Blocking' and 'Load Management'.
- You help the user find the best 'time slots' in their actual life, not just on paper.
- You can access the user's calendar to check their schedule and suggest new events.

[Guidelines]
1. Map out the Context
   - Briefly ask about the goal and the user's current energy level.
   - Identify 'Fixed Commitments' first to find 'Available Slots'.

2. Time Blocking (Not Micromanagement)
   - Use 'Time Blocks' (e.g., "Post-work 1 hour," "Morning 30-min window").
   - Define clear 'Entrance and Exit' points for each block.

3. Visual & Realistic Planning
   - Present plans in a clear list or table format.
   - Always include 'Buffer Time' (rest) to prevent burnout.

4. Calendar Integration
   - When a user asks about their schedule, use the query_calendar tool to check.
   - When a user wants to add an event, use the suggest_calendar_event tool.
   - Always confirm with the user before suggesting calendar additions.

5. The 'Actionable' Feedback Loop
   - Always conclude with:
     1) "In this plan, which part feels the easiest to start right now?"
     2) "Try it out, and if it feels heavy, let's resize the block tomorrow."

[Prohibited Actions]
- No micromanaging. Focus on the 'Flow'.
- No "Get a grip" or "You lack willpower" vibes.
- Avoid extreme or rigid schedules that ignore the user's fatigue.

[Style Guide]
- Use informal language(반말) like a supportive, organized friend.
- Use numbers/tables for clarity.
- Keep the tone warm, encouraging, and highly practical.
```

### 3) Dynamic System Prompt Template (Runtime Injection)
```text
{base_prompt}

**현재 시각: {current_datetime}**
(날짜 계산 시 위 정보를 기준으로 하세요. 예: "내일"은 {tomorrow}, "오늘"은 {today})

사용자 정보:
- 닉네임: {nickname}
- AI가 알면 좋은 정보: {ai_info}
- 언어: {locale}

[웹 검색 사용 지침]
- 최신 정보/외부 사실이 필요한 질문이면 tavily_web_search 도구를 우선 사용하세요.
- 출처가 필요한 정보는 도구 결과의 URL을 근거로 요약하세요.
- 도구 결과가 없거나 불확실하면 단정하지 말고 제한 사항을 명확히 말하세요.

- 사용자가 명시적으로 검색을 요청했으므로 이번 답변에서는 tavily_web_search 도구를 최소 1회 실행하세요.
```

### 4) Group Chat Routing Prompt
```text
사용자 메시지를 분석하여 가장 적합한 캐릭터를 선택하세요.

**캐릭터:**
1. **루미 (char_1)** - 감정 지원: 공감, 위로, 정서적 안정
2. **카이 (char_2)** - 실용 조언: 문제 해결, 계획, 목표 달성

**메시지:** "{message}"

JSON만 반환: {"character": "char_1", "reason": "이유"}
```

### 5) Calendar Intent Analysis Prompt
```text
[시스템 정보]
현재 시간: {now}

[날짜 해석 규칙]
1. 모든 상대적 날짜는 '현재 시간'을 기준으로 계산한다.
2. "요즘" : 과거 14일부터 미래 7일까지
3. "최근" : 과거 14일부터 현재까지

사용자 메시지: "{message}"

[의도 분류]
1. **query**: 일정 조회가 필요한 경우
2. **add**: 일정 추가 - "추가, 등록, 저장, 넣어줘, 잡아줘, 기록해줘" 등 명시적 명령어가 있을 때만
3. **none**: 캘린더와 무관한 일상 대화

JSON만 반환:
{
  "intent_type": "query" | "add" | "none",
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD",
  "event_details": {
    "title": "회의",
    "startDate": "YYYY-MM-DD",
    "endDate": "YYYY-MM-DD",
    "startTime": "15:00",
    "endTime": "17:00",
    "description": ""
  }
}
```

### 6) User Info Extraction Prompt
```text
다음 대화에서 사용자에 대한 핵심 정보를 추출하세요.

User: {user_message}
AI: {ai_response}

[이미 저장된 정보]
{existing_info}
위 정보와 중복되는 내용은 추출하지 마세요.

[추출 기준]
- 직업/직장, 취미/관심사, 목표/계획, 가족관계만 추출
- 추측이나 해석 금지. 명확히 언급된 사실만
- 정보가 없으면 "None"만 출력

[형식]
key: value (최대 2문장)
```

### 7) Report Insight Generation Prompt
```text
'{nickname}'님이 AI 캐릭터 '{character_name}'와 나눈 대화를 분석하세요.

대화 요약: {summary}
최근 대화:
{recent_messages}

5문장 이하로 짧은 인사이트를 작성하세요. 친근한 반말 사용.
```

## AI Scenarios
1. 감정 공감 시나리오
- 입력: \"요즘 너무 지치고 잠이 안 와.\"
- 기대: 감정 수용 + 현재 감정 중심 응답(루미)

2. 문제 해결 시나리오
- 입력: \"면접 준비를 어디서부터 해야 할지 모르겠어.\"
- 기대: 이슈 구조화 + 실천 단계 제안(카이)

3. 캘린더 연동 시나리오
- 입력: \"다음 주 수요일 저녁에 운동 일정 추가해줘.\"
- 기대: 일정 의도 파악 -> 구조화된 suggestion 반환(리브)

4. 검색 기반 시나리오
- 입력: \"최신 AI 뉴스 3개 요약해줘.\"
- 기대: Tavily 검색 -> 출처 포함 요약

## Challenges & Solutions
### 1) LangChain 전환 시 레거시 계약 유지
- 문제: 기존 프론트 계약(`content`, `responding_character` 등)을 깨면 즉시 장애
- 해결: 응답 계약 고정 + 런타임만 교체하는 어댑터 계층 도입

### 2) 검색 기능의 UX/정확도 균형
- 문제: 검색 ON일 때 무조건 검색하면 품질 저하, OFF인데 검색하면 신뢰 저하
- 해결: 요청 플래그 + 명시적 검색 의도 + 도구 실행 결과 기반 메타데이터 노출

### 3) 저장소 이원화(KV + Postgres) 복잡도
- 문제: 캐시와 원본의 역할이 섞이면 버그 추적이 어려움
- 해결: Postgres=Source of Truth, KV=Cache/Transient로 경계 명문화

## Public Code Snippets
- [`snippets/01_agent_factory.py`](./snippets/01_agent_factory.py)
- [`snippets/02_dynamic_prompt_middleware.py`](./snippets/02_dynamic_prompt_middleware.py)
- [`snippets/03_tavily_search_tool.py`](./snippets/03_tavily_search_tool.py)
- [`snippets/04_character_prompts.py`](./snippets/04_character_prompts.py)

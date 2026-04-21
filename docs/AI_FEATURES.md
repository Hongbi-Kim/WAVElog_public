# AI Features Overview

이 문서는 Wave LOG의 핵심 AI 기능 4가지를 구현 관점에서 정리한 문서입니다.

## 1) 대화 (Character Chat)
### 목적
- 캐릭터별 성격을 유지한 대화 응답 생성

### 입력
- `character_id`, `messages`, `profile`, `use_memory`, `use_web_search`

### 처리 핵심
- 캐릭터별 프롬프트 + 모델 파라미터(temperature) 분리
- 동적 컨텍스트 주입(닉네임, ai_info, locale, 현재 시간)
- 요약/정보추출 미들웨어 실행

### 출력
- `content`, `model_used`, `extracted_info`, `responding_character`, `search_metadata`

### 관련 공개 코드
- `snippets/01_agent_factory.py`
- `snippets/02_dynamic_prompt_middleware.py`
- `snippets/04_character_prompts.py`

---

## 2) 리포트 (Report Insights)
### 목적
- 기간(주간/월간) 대화 데이터를 캐릭터 단위로 집계해 인사이트 생성

### 입력
- `period`, `characterData`, `userNickname`

### 처리 핵심
- 캐릭터별 메시지 수/요약/최근 대화 구성
- 리포트 인사이트 전용 프롬프트 체인 호출
- 캐시 키 기반 재생성 제어

### 출력
- 캐릭터별 인사이트 텍스트/요약 결과

### 공개 범위
- API 계약 및 데이터 구조 중심 문서 공개
- 상세 리포트 프롬프트 전문은 비공개(운영 품질 보호)

---

## 3) 그룹채팅 (Multi-Agent Routing)
### 목적
- 단일 그룹 채팅 입력을 적절한 캐릭터(루미/카이/리브)로 라우팅

### 라우팅 우선순위
1. 멘션 기반 (`@루미`, `@카이`, `@리브`)
2. LLM 라우팅
3. 키워드 폴백

### 출력
- 실제 응답 캐릭터 메타데이터
  - `responding_character.charId`
  - `responding_character.charName`
  - `responding_character.reason`

### 공개 범위
- 우선순위 정책/결과 스키마 공개
- 내부 라우팅 힌트/운영 룰 일부 비공개

---

## 4) 검색 (Tavily Web Search)
### 목적
- 최신 정보/외부 사실이 필요한 질문에 대해 웹 검색 보강

### 제어 방식
- 전역 토글: `LC_ENABLE_TAVILY`
- 요청 토글: `web_search_enabled`
- 명시적 검색 의도(예: "검색해줘") 시 강제 실행 플래그

### 처리 핵심
- 도구 실행 후 검색어/출처를 정규화
- 응답에 `search_metadata` 포함

### 출력
- `search_metadata.enabled/attempted/used/status/query/references[]`

### 관련 공개 코드
- `snippets/03_tavily_search_tool.py`

---

## Prompt 공개 정책
- 공개: 캐릭터 역할/톤/금지사항/응답 길이 같은 설계 원칙
- 비공개: 운영 성능에 직접 영향을 주는 세부 문구, 방어 로직, 어뷰즈 대응 문장

이 저장소의 프롬프트 코드는 "실제 프롬프트와 유사한 공개 버전"입니다.

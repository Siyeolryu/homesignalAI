"""
프롬프트 버전 1

변경 이력:
- v1.0 (2025-02-25): 초기 버전
"""

SYSTEM_PROMPT_V1 = """당신은 동대문구 지역 전문 부동산 분석가 및 투자 전략가입니다.

## 역할
- 동대문구(청량리, 이문동, 휘경동 등) 부동산 시장에 대한 전문적인 분석 제공
- 시계열 예측 데이터, 뉴스/이슈, 그리고 **선거 공약(지방선거/총선)**을 종합하여 근거 있는 인사이트 전달
- 선거 공약의 경우, 해당 지역(동)과 공약의 관련성 및 시장 기대 심리를 분석하여 설명

## 톤앤매너
- 신뢰감 있고 객관적인 어조
- 전문 용어 사용 시 쉽게 풀어서 설명
- 투자 조언이 아닌 정보 제공 목적임을 명시

## 제약사항
1. 반드시 제공된 시계열 데이터와 뉴스/선거 공약 컨텍스트를 기반으로 답변
2. 선거 공약 언급 시 "실현 여부 및 예산 확보에 따라 변동될 수 있음"을 명시
3. 근거 없는 추측 배제
4. 분석의 한계점 명시 ("본 데이터는 참고용입니다")
5. 답변 마지막에 참고한 데이터 소스 표기

## 출력 형식
- 마크다운(Markdown) 형식 사용
- 핵심 수치는 **볼드체** 처리
- 구조화된 답변 (소제목, 불릿 포인트 활용)
- 선거 공약 관련 답변 시 '선거 시그널(Election Signal)' 섹션을 별도로 구성하여 설명 가능
"""


def build_context_message(
    user_query: str,
    forecast_json: dict | None = None,
    news_chunks: list[dict] | None = None,
    election_signals: str | None = None,
) -> str:
    """
    RAG 컨텍스트 메시지 생성 (대화형 챗봇)

    Args:
        user_query: 사용자 질문
        forecast_json: 시계열 예측 데이터 (JSON 문자열)
        news_chunks: 관련 뉴스 문서 목록
        election_signals: MCP 선거 공약 데이터 (JSON 문자열, 선택사항)

    Returns:
        str: 구조화된 컨텍스트 메시지
    """
    parts = []

    if forecast_json:
        parts.append("## 시계열 예측 데이터")
        parts.append(f"```json\n{forecast_json}\n```")

    if news_chunks:
        parts.append("\n## 관련 뉴스/문서")
        for i, chunk in enumerate(news_chunks, 1):
            source = chunk.get("source", "출처 미상")
            content = chunk.get("content", "")
            parts.append(f"{i}. (출처: {source}) {content}")

    if election_signals:
        parts.append("\n## 선거 시그널 (Election Signals)")
        parts.append("최신 지방선거 및 총선 공약 정보:")
        parts.append(f"```json\n{election_signals}\n```")
        parts.append(
            "※ 선거 공약은 실현 여부 및 예산 확보에 따라 변동될 수 있습니다."
        )

    parts.append(f"\n## 사용자 질문\n{user_query}")

    return "\n".join(parts)

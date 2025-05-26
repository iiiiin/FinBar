def build_stock_prompt(user_info, selected_market=None, selected_sector=None):
    # 필터 텍스트 생성
    if selected_market and selected_sector:
        filter_text = f"{selected_market} 시장의 {selected_sector} 산업군"
    elif selected_market:
        filter_text = f"{selected_market} 시장"
    elif selected_sector:
        filter_text = f"{selected_sector} 산업군"
    else:
        filter_text = "한국 주식 전체"

    return f"""
사용자는 연 수익률 {user_info['required_return']}%를 희망하며, 투자 성향은 {user_info['risk_type']}입니다.
추천 대상은 {filter_text}에 속한 종목으로 한정해 주세요.
성장성, 산업 트렌드, 실적 등을 종합적으로 고려하여 유망한 종목 5개를 추천하고, 각 종목에 대해 간단한 추천 사유를 포함해 주세요.

출력은 반드시 아래 예시와 같은 JSON 배열 형식으로 제공해 주세요. 마침표 없이 JSON만 출력해주세요:

[
    {{
      "type": "주식",
      "name": "삼성전자",
      "code": "005930",
      "market": "KOSPI",
      "sector": "반도체",
      "reason": "메모리 반도체 수요 회복"
    }},
    {{
      "type": "주식",
      "name": "에코프로비엠",
      "code": "247540",
      "market": "KOSDAQ",
      "sector": "2차전지",
      "reason": "전기차 배터리 소재 수요 증가"
    }}
]
"""


def ask_gpt_for_product_recommendation(prompt: str, temperature: float = 0.7) -> list:
    import openai
    import json
    import logging
    from django.conf import settings
    from financial_products.serializers import StockRecommendationSerializer

    logger = logging.getLogger(__name__)

    # 최신 openai SDK 사용
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "당신은 금융 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
        )

        # 최신 응답 구조에 맞는 content 추출
        content = response.choices[0].message.content

        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as json_error:
            logger.warning("GPT 응답 JSON 파싱 실패: %s", json_error)
            logger.debug("GPT 응답 원문:\n%s", content)
            return []

        if not isinstance(parsed, list):
            logger.warning("GPT 응답이 JSON 배열이 아님: %s", type(parsed))
            logger.debug("파싱된 응답:\n%s", parsed)
            return []

        serializer = StockRecommendationSerializer(data=parsed, many=True)
        if serializer.is_valid():
            return serializer.data
        else:
            logger.warning("GPT 응답 시리얼라이저 검증 실패")
            logger.debug("시리얼라이저 오류: %s", serializer.errors)
            return []

    except Exception as e:
        logger.error("GPT API 호출 중 예외 발생: %s", str(e))
        return []

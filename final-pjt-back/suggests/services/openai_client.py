def build_stock_prompt(profile, market_choice, sector_choice):
    required_return = (
        profile.required_return if hasattr(profile, "required_return") else 0
    )

    # 비현실적인 수익률에 대한 경고 메시지 생성
    warning_message = ""
    if required_return > 20:
        warning_message = """
        주의: 요청하신 수익률은 매우 높은 수준입니다. 
        주식 투자는 높은 수익을 기대할 수 있지만, 그만큼 높은 위험도 수반됩니다.
        투자 결정 전에 충분한 리서치와 위험 관리가 필요합니다.
        """
    elif required_return > 15:
        warning_message = """
        참고: 요청하신 수익률은 상당히 높은 수준입니다.
        장기적인 관점에서 접근하고, 분산 투자를 고려하시기 바랍니다.
        """

    prompt = f"""
    {warning_message}
    
    사용자는 연 수익률 {required_return}%를 희망하며, 투자 성향은 {profile.risk_type}입니다.
    선호하는 시장은 {market_choice}이며, 관심 있는 섹터는 {sector_choice}입니다.
    
    위 정보를 바탕으로 적합한 주식 종목을 추천해주세요.
    각 종목에 대해 다음 정보를 포함해주세요:
    1. 종목명
    2. 종목코드
    3. 현재가
    4. 52주 최고/최저가
    5. 시가총액
    6. PER
    7. PBR
    8. 배당수익률
    9. 추천 이유
    10. 투자 시 고려사항
    
    응답은 반드시 아래 예시와 같은 JSON 배열 형식으로 제공해주세요:
    [
        {{
            "name": "삼성전자",
            "code": "005930",
            "market": "KOSPI",
            "sector": "반도체",
            "current_price": "80,500",
            "high_52w": "89,000",
            "low_52w": "58,300",
            "market_cap": "5조 380억원",
            "per": 17.68,
            "pbr": 1.82,
            "dividend_yield": "2.34",
            "reason": "반도체 시장에서의 선두 기업으로 기술력과 글로벌 시장 점유율이 뛰어나며 안정적인 성과를 보여줌",
            "considerations": "경기 변동성에 취약하며 대외적인 정치/경제적 요인에 민감할 수 있음"
        }},
        {{
            "name": "SK하이닉스",
            "code": "000660",
            "market": "KOSPI",
            "sector": "반도체",
            "current_price": "139,000",
            "high_52w": "160,500",
            "low_52w": "79,400",
            "market_cap": "1조 910억원",
            "per": 25.21,
            "pbr": 1.94,
            "dividend_yield": "1.00",
            "reason": "반도체 시장에서 높은 기술력을 바탕으로 글로벌 경쟁력을 확보하고 있으며, 수요 증가에 대응할 수 있는 생산 인프라 보유",
            "considerations": "가격 변동성이 높은 섹터이므로 주가의 변동을 주시하며 시장 동향을 주의깊게 관찰해야 함"
        }}
    ]
    
    반드시 위 형식의 JSON 배열만 반환해주세요. 다른 설명이나 텍스트는 포함하지 마세요.
    market 필드는 반드시 "KOSPI", "KOSDAQ", "KONEX" 중 하나여야 합니다.
    sector 필드는 반드시 "반도체", "바이오", "2차전지", "자동차", "금융", "건설", "에너지", "유통", "플랫폼", "기타" 중 하나여야 합니다.
    """
    return prompt


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
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "당신은 금융 전문가입니다. 응답은 반드시 JSON 배열만 반환하세요.",
                },
                {"role": "user", "content": prompt},
            ],
        )

        # 최신 응답 구조에 맞는 content 추출
        content = response.choices[0].message.content

        # 응답 정제 (```json 등 제거)
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

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

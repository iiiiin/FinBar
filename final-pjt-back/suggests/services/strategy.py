def determine_recommendation_factors(required_return, risk_type, preferred_period):
    short_term = preferred_period <= 6
    long_term = preferred_period > 24

    # 수익률 기반
    if required_return <= 3:
        by_return = "예금"
    elif 3 < required_return <= 5:
        by_return = "예적금 혼합"
    elif 5 < required_return <= 7:
        by_return = "적금+주식"
    else:
        by_return = "주식"

    # 성향 기반
    if risk_type in ["안정형", "안정추구형"]:
        by_risk = "예금"
    elif risk_type == "위험중립형":
        by_risk = "예적금 혼합"
    elif risk_type in ["적극투자형"]:
        by_risk = "적금+주식"
    else:  # 공격투자형
        by_risk = "주식"

    # 결합 판단
    if required_return > 5 and by_risk == "예금" and short_term:
        final = "경고: 수익률 도달 어려움"
    elif by_return == by_risk:
        final = by_return
    else:
        # 우선순위 또는 조합 로직을 구성할 수 있음
        final = by_return if by_return != "주식" else by_risk

    return {
        "by_return": by_return,
        "by_risk": by_risk,
        "final": final
    }

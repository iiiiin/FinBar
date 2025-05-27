import re


def remove_special_and_space(text: str) -> str:
    # \W: 영숫자와 언더바(_)를 제외한 모든 문자
    # \s: 모든 공백 문자
    # +: 1회 이상 반복
    pattern = r'[\W\s]+'
    return re.sub(pattern, '', text)

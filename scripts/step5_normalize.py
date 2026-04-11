# scripts/step5_normalize.py
"""
Step 5: 청크 본문 정규화 (검색·임베딩용)
"""
import re
import json

# Unicode 원숫자 → "N항:"
CIRCLED_DIGIT_MAP = {
    "①": "1항", "②": "2항", "③": "3항", "④": "4항", "⑤": "5항",
    "⑥": "6항", "⑦": "7항", "⑧": "8항", "⑨": "9항", "⑩": "10항",
    "⑪": "11항", "⑫": "12항", "⑬": "13항", "⑭": "14항", "⑮": "15항",
    "⑯": "16항", "⑰": "17항", "⑱": "18항", "⑲": "19항", "⑳": "20항",
}

# 개정/신설/삭제 이력 제거
HISTORY_PATTERN = re.compile(r'<(?:개정|신설|삭제|전문개정|제목개정)[^>]*>')

# 볼드 표시 제거
BOLD_PATTERN = re.compile(r'\*\*([^*]+)\*\*')

# 들여쓰기된 호(號)
# 기존 HO_PATTERN 교체
HO_PATTERN = re.compile(r'^\s*(\d+)\s*\\?\.\s+', re.MULTILINE)
NUM_PAREN_PATTERN = re.compile(r'^\s*(\d+)\)\s+', re.MULTILINE)
MOK_PATTERN = re.compile(r'^\s*([가-하])\.\s+', re.MULTILINE)

# 낫표 제거 (검색용)
BRACKET_LAW_PATTERN = re.compile(r'「([^」]+)」')

# 여러 공백/줄바꿈
MULTI_WHITESPACE = re.compile(r'\s+')
MULTI_NEWLINE = re.compile(r'\n{3,}')


def normalize_content(body: str, article_no: str, article_title: str) -> str:
    """
    조문 본문을 검색·임베딩용으로 정규화.
    
    Args:
        body: Step 4의 "body" (조문 헤더 제외한 본문)
        article_no: "제53조"
        article_title: "연장 근로의 제한"
    
    Returns:
        정규화된 텍스트
    """
    text = body
    
    # 1. 개정 이력 제거
    text = HISTORY_PATTERN.sub('', text)
    
    # 2. 볼드 마크 제거 (원숫자 추출 전)
    # **①** → ①
    text = BOLD_PATTERN.sub(r'\1', text)
    
    # 3. Unicode 원숫자 → "N항:"
    for circled, text_form in CIRCLED_DIGIT_MAP.items():
        text = text.replace(circled, f"{text_form}:")
    
    # 4. 호(號) 정규화: "  1\. " → "1호: "
    text = HO_PATTERN.sub(r'\1호: ', text)
    text = NUM_PAREN_PATTERN.sub(r'\1호: ', text)
    text = MOK_PATTERN.sub(r'\1목: ', text)
    
    # 5. 낫표 제거: 「근로기준법」 → 근로기준법
    text = BRACKET_LAW_PATTERN.sub(r'\1', text)
    
    # 6. 공백 정리
    text = MULTI_NEWLINE.sub('\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = text.strip()
    
    # 7. 헤더 재구성 (검색 시 제목 매칭 강화)
    header = f"{article_no}"
    if article_title:
        header += f" ({article_title})"
    
    return f"{header}\n\n{text}"


def main():
    print("=" * 60)
    print("Step 5: 조문 내용 정규화")
    print("=" * 60)
    
    with open("scripts/step4_raw_chunks.json", encoding="utf-8") as f:
        chunks = json.load(f)
    
    for chunk in chunks:
        chunk["content_normalized"] = normalize_content(
            chunk["body"],
            chunk["article_no"],
            chunk["article_title"]
        )
        chunk["char_count_original"] = len(chunk["content"])
        chunk["char_count_normalized"] = len(chunk["content_normalized"])
        # body는 이제 불필요
        del chunk["body"]
    
    # 샘플 확인
    print("\n=== 정규화 샘플 (근로기준법 제53조) ===")
    for c in chunks:
        if c["law_name"] == "근로기준법" and c["article_no"] == "제53조":
            print("\n[원본 content]")
            print(c["content"][:400])
            print("\n[정규화 content_normalized]")
            print(c["content_normalized"][:400])
            break
    
    with open("scripts/step5_normalized_chunks.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    
    print(f"\n→ scripts/step5_normalized_chunks.json 저장 완료")


if __name__ == "__main__":
    main()
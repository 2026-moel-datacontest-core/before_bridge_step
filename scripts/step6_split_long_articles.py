# scripts/step6_split_long_articles.py
"""
Step 6: 긴 조문을 항(項) 단위로 재분해
"""
import re
import json

LONG_THRESHOLD = 2000  # 문자 단위

# 항 분리 패턴 (정규화된 텍스트 기준)
# "1항: ...\n\n2항: ..." 형태로 되어있음
PARAGRAPH_PATTERN = re.compile(
    r'(\d+항:)(.*?)(?=\n\n\d+항:|\Z)',
    re.DOTALL
)


def mark_unsplit(chunk: dict) -> dict:
    """분해되지 않은 청크도 필드를 일관되게 유지"""
    chunk["parent_article"] = None
    chunk["paragraph_no"] = None
    chunk["chunk_id_suffix"] = ""
    return chunk


def split_by_paragraph(chunk: dict) -> list[dict]:
    """긴 조문을 항 단위 서브청크로 분해"""
    normalized = chunk["content_normalized"]
    
    # 조문 헤더 분리
    lines = normalized.split("\n\n", 1)
    if len(lines) < 2:
        return [mark_unsplit(dict(chunk))]  # 분해 불가
    
    header = lines[0]
    body = lines[1]
    
    # 항 추출
    paragraphs = list(PARAGRAPH_PATTERN.finditer(body))
    
    if len(paragraphs) < 2:
        # 항이 2개 미만이면 분해 안 함
        return [mark_unsplit(dict(chunk))]
    
    subchunks = []
    for i, match in enumerate(paragraphs, 1):
        para_no = match.group(1)  # "1항:"
        para_body = match.group(2).strip()
        
        if not para_body:
            continue
        
        # 서브청크 생성
        sub_content = f"{header}\n\n{para_no} {para_body}"
        
        sub = dict(chunk)  # 원본 복사
        sub["content_normalized"] = sub_content
        sub["char_count_normalized"] = len(sub_content)
        sub["parent_article"] = chunk["article_no"]
        sub["paragraph_no"] = i
        sub["chunk_id_suffix"] = f"_{i}항"
        subchunks.append(sub)
    
    return subchunks if subchunks else [mark_unsplit(dict(chunk))]


def main():
    print("=" * 60)
    print("Step 6: 긴 조문 재분해")
    print("=" * 60)
    
    with open("scripts/step5_normalized_chunks.json", encoding="utf-8") as f:
        chunks = json.load(f)
    
    final_chunks = []
    split_count = 0
    
    for chunk in chunks:
        if chunk["char_count_normalized"] > LONG_THRESHOLD:
            subs = split_by_paragraph(chunk)
            if len(subs) > 1:
                split_count += 1
                final_chunks.extend(subs)
            else:
                final_chunks.extend(subs)
        else:
            # 원본 유지
            final_chunks.append(mark_unsplit(chunk))
    
    print(f"  원본 청크: {len(chunks)}")
    print(f"  긴 조문 분해: {split_count}건")
    print(f"  최종 청크: {len(final_chunks)}")
    
    # 길이 분포
    lengths = [c["char_count_normalized"] for c in final_chunks]
    print(f"\n청크 길이 통계:")
    print(f"  최소: {min(lengths)}자")
    print(f"  최대: {max(lengths)}자")
    print(f"  평균: {sum(lengths) // len(lengths)}자")
    
    with open("scripts/step6_split_chunks.json", "w", encoding="utf-8") as f:
        json.dump(final_chunks, f, ensure_ascii=False, indent=2)
    
    print(f"\n→ scripts/step6_split_chunks.json 저장 완료")


if __name__ == "__main__":
    main()

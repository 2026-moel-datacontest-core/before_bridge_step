# scripts/step8_dedupe_and_validate.py
"""
Step 8: 중복 제거 및 검증
"""
import json
from collections import Counter
import hashlib


def content_hash(text: str) -> str:
    """본문 내용 해시"""
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def main():
    print("=" * 60)
    print("Step 8: 중복 제거 및 검증")
    print("=" * 60)
    
    with open("scripts/step7_finalized_chunks.json", encoding="utf-8") as f:
        chunks = json.load(f)
    
    # 1. chunk_id 중복 검사
    id_counts = Counter(c["chunk_id"] for c in chunks)
    duplicates = {k: v for k, v in id_counts.items() if v > 1}
    
    if duplicates:
        print(f"\n⚠️  chunk_id 중복 발견: {len(duplicates)}건")
        for cid, count in list(duplicates.items())[:5]:
            print(f"  {cid}: {count}회")
    else:
        print("✓ chunk_id 중복 없음")
    
    # 2. 내용 중복 검사
    content_hashes = Counter(
        content_hash(c["content_normalized"]) for c in chunks
    )
    content_dups = {k: v for k, v in content_hashes.items() if v > 1}
    
    if content_dups:
        print(f"\n⚠️  내용 중복 발견: {len(content_dups)}건")
        # 중복 내용 샘플 출력
        for h, count in list(content_dups.items())[:3]:
            same = [c for c in chunks if content_hash(c["content_normalized"]) == h]
            print(f"  해시 {h[:8]}: {count}회")
            for s in same[:2]:
                print(f"    - {s['chunk_id']}")
    else:
        print("✓ 내용 중복 없음")
    
    # 3. 필수 필드 검증
    required_fields = [
    "chunk_id", "law_name", "full_title", "doc_type",
    "article_no", "article_ordinal",
    "content", "content_normalized", "embedding_text",
    "citation_label",
    "law_mst", "enforcement_date", "tier"
    ]       
    missing_field_count = 0
    for c in chunks:
        for f in required_fields:
            if f not in c or c[f] is None:
                if f == "content_normalized":
                    missing_field_count += 1
    
    if missing_field_count:
        print(f"\n⚠️  필수 필드 누락: {missing_field_count}건")
    else:
        print("✓ 필수 필드 모두 존재")
    
    # 4. 빈 청크 검사
    empty_chunks = [c for c in chunks if len(c["content_normalized"].strip()) < 20]
    if empty_chunks:
        print(f"\n⚠️  내용이 너무 짧은 청크: {len(empty_chunks)}건 (20자 미만)")
        chunks = [c for c in chunks if len(c["content_normalized"].strip()) >= 20]
    else:
        print("✓ 짧은 청크 없음")
    
    # 5. 중복 제거 (chunk_id 기준)
    seen_ids = set()
    unique_chunks = []
    for c in chunks:
        if c["chunk_id"] not in seen_ids:
            seen_ids.add(c["chunk_id"])
            unique_chunks.append(c)
    
    print(f"\n최종 청크: {len(unique_chunks)}개")
    
    with open("scripts/step8_validated_chunks.json", "w", encoding="utf-8") as f:
        json.dump(unique_chunks, f, ensure_ascii=False, indent=2)
    
    print("→ scripts/step8_validated_chunks.json 저장 완료")


if __name__ == "__main__":
    main()
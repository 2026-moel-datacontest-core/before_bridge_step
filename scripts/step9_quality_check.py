# scripts/step9_quality_check.py
"""
Step 9: 청크 품질 자동 검사
"""
import json
import re

# 반드시 존재해야 하는 핵심 조문 (검증용)
KEY_ARTICLES = {
    "근로기준법": ["제2조", "제17조", "제50조", "제53조", "제54조", "제55조", "제56조", "제76조의2"],
    "산업안전보건법": ["제5조", "제29조", "제38조"],
    "최저임금법": ["제5조", "제6조"],
    "근로자퇴직급여보장법": ["제8조", "제9조"],
    "외국인근로자의고용등에관한법률": ["제9조", "제25조"],
    "남녀고용평등과일ㆍ가정양립지원에관한법률": ["제7조", "제8조", "제11조"],
    "산업재해보상보험법": ["제5조", "제37조", "제52조"],
    "중대재해처벌등에관한법률": ["제2조", "제4조", "제6조"],
}


def main():
    print("=" * 60)
    print("Step 9: 청크 품질 검사")
    print("=" * 60)
    
    with open("scripts/step8_validated_chunks.json", encoding="utf-8") as f:
        chunks = json.load(f)
    
    # 법령별 조문 인덱스
    index = {}
    for c in chunks:
        key = (c["law_name"], c["article_no"])
        if key not in index:
            index[key] = []
        index[key].append(c)
    
    # 1. 핵심 조문 존재 확인
    print("\n[핵심 조문 존재 확인]")
    missing = []
    for law, articles in KEY_ARTICLES.items():
        for art in articles:
            if (law, art) not in index:
                missing.append(f"{law} {art}")
                print(f"  ❌ {law} {art}")
            else:
                print(f"  ✓ {law} {art}")
    
    if missing:
        print(f"\n⚠️  누락된 핵심 조문 {len(missing)}개 - 파싱 로직 재점검 필요")
    
    # 2. 길이 분포
    lengths = [c["char_count_normalized"] for c in chunks]
    print(f"\n[길이 분포]")
    print(f"  최소: {min(lengths)}자")
    print(f"  최대: {max(lengths)}자")
    print(f"  평균: {sum(lengths) // len(lengths)}자")
    print(f"  중간값: {sorted(lengths)[len(lengths)//2]}자")
    print(f"  2000자 초과: {sum(1 for l in lengths if l > 2000)}개")
    print(f"  100자 미만: {sum(1 for l in lengths if l < 100)}개")
    
    # 3. 법령별 청크 수
    print(f"\n[법령별 청크 수]")
    from collections import Counter
    law_counts = Counter(c["law_name"] for c in chunks)
    for law, count in sorted(law_counts.items(), key=lambda x: -x[1]):
        print(f"  {law}: {count}")
    
    # 4. doc_type별 청크 수
    print(f"\n[문서 종류별]")
    doc_counts = Counter(c["doc_type"] for c in chunks)
    for doc, count in sorted(doc_counts.items(), key=lambda x: -x[1]):
        print(f"  {doc}: {count}")
    
    # 5. 정규화 품질 확인 (원숫자가 남아있는지)
    print(f"\n[정규화 품질 확인]")
    circled_remnants = sum(
        1 for c in chunks 
        if any(ch in c["content_normalized"] for ch in "①②③④⑤")
    )
    if circled_remnants:
        print(f"  ⚠️  원숫자가 남은 청크: {circled_remnants}개")
    else:
        print(f"  ✓ 원숫자 모두 정규화됨")
    
    history_remnants = sum(
        1 for c in chunks 
        if "<개정" in c["content_normalized"] or "<신설" in c["content_normalized"]
    )
    if history_remnants:
        print(f"  ⚠️  개정 이력이 남은 청크: {history_remnants}개")
    else:
        print(f"  ✓ 개정 이력 모두 제거됨")
        
    # 근로기준법 제76조 중복 검증 (특별 케이스)
    article_76_chunks = [
        c for c in chunks
        if c["law_name"] == "근로기준법"
        and c["doc_type"] == "법률"
        and c["article_no"] == "제76조"
    ]
    print(f"\n[제76조 중복 검증]")
    print(f"  발견: {len(article_76_chunks)}개 (기대: 3개)")
    for c in article_76_chunks:
        print(f"    - ordinal={c['article_ordinal']}: {c['article_title']}")
    if len(article_76_chunks) != 3:
        print("  ⚠️  article_ordinal 로직 실패 — Step 4 재점검 필요")


if __name__ == "__main__":
    main()
# scripts/step10_finalize.py
"""
Step 10: PostgreSQL 저장을 위한 최종 형태로 정리
(임베딩 단계에서 사용)
"""
import json
from pathlib import Path

def main():
    print("=" * 60)
    print("Step 10: 최종 저장")
    print("=" * 60)
    
    with open("scripts/step8_validated_chunks.json", encoding="utf-8") as f:
        chunks = json.load(f)
    
    # 최종 저장 경로
    output_dir = Path("backend/data/law_chunks")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 전체 청크를 하나의 JSON으로
    final_path = output_dir / "all_chunks.json"
    with open(final_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    
    # 법령별 분리 저장 (디버깅용)
    by_law = {}
    for c in chunks:
        law = c["law_name"]
        if law not in by_law:
            by_law[law] = []
        by_law[law].append(c)
    
    for law, law_chunks in by_law.items():
        safe_name = law.replace("ㆍ", "_").replace(" ", "_")
        path = output_dir / f"{safe_name}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(law_chunks, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ 총 {len(chunks)}개 청크")
    print(f"✓ 저장 위치: {output_dir}/")
    print(f"\n다음 단계: embedding 생성 (Master Plan Step A-6)")


if __name__ == "__main__":
    main()
# scripts/step7_finalize_metadata.py
"""
Step 7: 최종 chunk_id / citation_label / embedding_text 생성
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path
from typing import Any, Optional

INPUT_PATH = Path("scripts/step6_split_chunks.json")
OUTPUT_PATH = Path("scripts/step7_finalized_chunks.json")


def compact_slug(text: str, max_len: int = 40) -> str:
    text = unicodedata.normalize("NFKC", text or "")
    text = text.replace("ㆍ", "·")
    text = re.sub(r"\s+", "", text)
    text = re.sub(r"[^0-9A-Za-z가-힣·]+", "-", text).strip("-")
    return (text[:max_len] if text else "na")


def short_sha1(text: str, length: int = 10) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:length]


def to_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def generate_chunk_id(chunk: dict[str, Any]) -> str:
    """
    사람이 읽을 수 있으면서도 충돌 가능성이 낮은 chunk_id.
    commit hash는 넣지 않는다. (force-push 대비)
    """
    article_ordinal = to_int(chunk.get("article_ordinal"), 1)
    paragraph_no = chunk.get("paragraph_no")

    stable_key = "|".join(
        [
            str(chunk.get("law_id") or ""),
            str(chunk.get("law_mst") or ""),
            str(chunk.get("doc_type") or ""),
            str(chunk.get("article_no") or ""),
            str(article_ordinal),
            str(chunk.get("article_title") or ""),
            str(paragraph_no or ""),
        ]
    )
    digest = short_sha1(stable_key, length=12)

    parts = [
        compact_slug(str(chunk.get("full_title") or chunk.get("law_name") or "")),
        compact_slug(str(chunk.get("article_no") or "")),
        f"ord{article_ordinal:02d}",
    ]

    if paragraph_no is not None:
        parts.append(f"para{to_int(paragraph_no, 0):02d}")

    parts.append(f"mst{compact_slug(str(chunk.get('law_mst') or ''))}")
    parts.append(digest)

    return "__".join(parts)


def build_citation_label(chunk: dict[str, Any]) -> str:
    """
    사용자 표시 / 내부 검증용 식별 라벨
    예:
    - 근로기준법 제53조 (연장 근로의 제한)
    - 근로기준법 시행규칙 제7조 (임금체불정보심의위원회 구성 및 운영) [중복순번 2]
    """
    full_title = str(chunk.get("full_title") or chunk.get("law_name") or "").strip()
    article_no = str(chunk.get("article_no") or "").strip()
    article_title = str(chunk.get("article_title") or "").strip()
    article_ordinal = to_int(chunk.get("article_ordinal"), 1)
    paragraph_no = chunk.get("paragraph_no")

    label = f"{full_title} {article_no}".strip()
    if article_title:
        label += f" ({article_title})"
    if article_ordinal > 1:
        label += f" [중복순번 {article_ordinal}]"
    if paragraph_no is not None:
        label += f" [{to_int(paragraph_no, 0)}항 서브청크]"

    return label


def build_source_ref(chunk: dict[str, Any]) -> Optional[str]:
    """
    audit / QC용 참조
    commit hash는 고정 ID가 아니라 추적용으로만 남긴다.
    """
    commit = str(chunk.get("selected_commit") or "").strip()
    rel_path = str(chunk.get("relative_path") or "").strip()
    if commit and rel_path:
        return f"{commit}:{rel_path}"
    return None


def build_embedding_text(chunk: dict[str, Any]) -> str:
    """
    임베딩용 최종 텍스트.
    context headers를 약간 얹어서 검색 품질을 올린다.
    """
    parts: list[str] = []

    parts.append(f"[법령] {chunk['full_title']}")
    parts.append(f"[문서유형] {chunk['doc_type']}")

    legal_type = str(chunk.get("legal_type") or "").strip()
    if legal_type and legal_type != chunk["doc_type"]:
        parts.append(f"[법령구분] {legal_type}")

    if chunk.get("part"):
        parts.append(f"[편] {chunk['part']}")
    if chunk.get("chapter"):
        parts.append(f"[장] {chunk['chapter']}")
    if chunk.get("section"):
        parts.append(f"[절] {chunk['section']}")
    if chunk.get("subsection"):
        parts.append(f"[관] {chunk['subsection']}")

    article_ordinal = to_int(chunk.get("article_ordinal"), 1)
    if article_ordinal > 1:
        parts.append(f"[조문중복순번] {article_ordinal}")

    parts.append("")
    parts.append(chunk["content_normalized"])

    return "\n".join(parts)


def main() -> None:
    print("=" * 70)
    print("Step 7: 최종 메타데이터 부착")
    print("=" * 70)

    with INPUT_PATH.open(encoding="utf-8") as f:
        chunks = json.load(f)

    for chunk in chunks:
        chunk["chunk_id"] = generate_chunk_id(chunk)
        chunk["citation_label"] = build_citation_label(chunk)

        source_ref = build_source_ref(chunk)
        if source_ref:
            chunk["source_ref"] = source_ref

        chunk["embedding_text"] = build_embedding_text(chunk)

    # 샘플 출력
    print("\n=== 샘플 ===")
    sample = None
    for c in chunks:
        if c.get("law_name") == "근로기준법" and c.get("article_no") == "제53조":
            sample = c
            break
    if sample is None and chunks:
        sample = chunks[0]

    if sample:
        print(f"chunk_id: {sample['chunk_id']}")
        print(f"citation_label: {sample['citation_label']}")
        print(f"embedding_text (앞 300자):\n{sample['embedding_text'][:300]}")

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    print(f"\n최종 청크: {len(chunks)}개")
    print(f"→ {OUTPUT_PATH} 저장 완료")


if __name__ == "__main__":
    main()
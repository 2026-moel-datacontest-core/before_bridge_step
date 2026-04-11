# scripts/step4_chunk_articles.py
"""
Step 4: 기준일 유효 스냅샷을 조문 단위 청크로 분해
- Step 3(chapter_map) 의존성 제거
- 편/장/절/관 컨텍스트를 같이 추출
- 부칙 제외
- 삭제 조문 제외
- 같은 article_no가 여러 번 나오면 article_ordinal 부여
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Optional

INPUT_PATH = Path("scripts/step1_effective_snapshots.json")
OUTPUT_PATH = Path("scripts/step4_raw_chunks.json")

APPENDIX_RE = re.compile(r"^#{1,6}\s*부칙(?:\b|[\s<(])")
PART_RE = re.compile(r"^#\s*제\d+편(?:의\d+)?\b")
CHAPTER_RE = re.compile(r"^##\s*제\d+장(?:의\d+)?\b")
SECTION_RE = re.compile(r"^###\s*제\d+절(?:의\d+)?\b")
SUBSECTION_RE = re.compile(r"^####\s*제\d+관(?:의\d+)?\b")
DELETION_ONLY_BODY_RE = re.compile(r"^삭제(?:\s*<[^>]*>)*$")

ARTICLE_RE = re.compile(
    r"^#####\s*"
    r"(제\d+조(?:의\d+)?)"
    r"(?:\s*\(([^)]*)\))?"
    r"(?:\s*(삭제))?"
    r"(?:\s*<[^>]*>)*"
    r"(?:\s+(.*))?$"
)


def strip_heading(line: str) -> str:
    return re.sub(r"^#{1,6}\s*", "", line).strip()


def build_structure_path(
    part: Optional[str],
    chapter: Optional[str],
    section: Optional[str],
    subsection: Optional[str],
) -> Optional[str]:
    parts = [p for p in (part, chapter, section, subsection) if p]
    return " > ".join(parts) if parts else None


def is_deletion_only_body(body: str) -> bool:
    return bool(DELETION_ONLY_BODY_RE.fullmatch(body.strip()))


def chunk_snapshot(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    content = snapshot["content"]

    law_name = snapshot.get("root_law_name") or snapshot["title"].split(" 시행")[0]
    full_title = snapshot["title"]
    doc_type = snapshot["doc_type"]

    ctx = {
        "part": None,
        "chapter": None,
        "section": None,
        "subsection": None,
    }

    article_ordinals: Counter[str] = Counter()
    chunks: list[dict[str, Any]] = []
    current: Optional[dict[str, Any]] = None

    def flush_current() -> None:
        nonlocal current
        if current is None:
            return

        body = "\n".join(current["body_lines"]).strip()

        # 삭제 조문은 청크로 만들지 않음
        if current["is_deleted"] or is_deletion_only_body(body):
            current = None
            return

        if not body:
            current = None
            return

        full_content = current["article_header"] + "\n\n" + body

        chunks.append(
            {
                "law_name": law_name,               # 루트 법령명
                "full_title": full_title,           # 예: 근로기준법 시행규칙
                "doc_type": doc_type,               # canonical role: 법률/시행령/시행규칙
                "legal_type": snapshot.get("legal_type"),  # 예: 고용노동부령
                "part": current["part"],
                "chapter": current["chapter"],
                "section": current["section"],
                "subsection": current["subsection"],
                "structure_path": build_structure_path(
                    current["part"],
                    current["chapter"],
                    current["section"],
                    current["subsection"],
                ),
                "article_no": current["article_no"],
                "article_ordinal": current["article_ordinal"],  # 중복 번호 방지용
                "article_title": current["article_title"],
                "article_label": (
                    f"{current['article_no']} ({current['article_title']})"
                    if current["article_title"]
                    else current["article_no"]
                ),
                "content": full_content,  # 원본 표시용
                "body": body,             # Step 5 정규화용
                "law_mst": snapshot.get("law_mst"),
                "law_id": snapshot.get("law_id"),
                "ministry": snapshot.get("ministry", []),
                "promulgation_date": snapshot.get("promulgation_date"),
                "enforcement_date": snapshot.get("enforcement_date"),
                "field": snapshot.get("field"),
                "status": snapshot.get("status"),
                "source_url": snapshot.get("source_url"),
                "selected_as_of": snapshot.get("selected_as_of"),
                "selected_commit": snapshot.get("selected_commit"),
                "relative_path": snapshot.get("relative_path"),
                "tier": 1,
            }
        )
        current = None

    for raw_line in content.splitlines():
        line = raw_line.rstrip()

        # 부칙부터는 제외
        if APPENDIX_RE.match(line):
            flush_current()
            break

        if PART_RE.match(line):
            flush_current()
            ctx["part"] = strip_heading(line)
            ctx["chapter"] = None
            ctx["section"] = None
            ctx["subsection"] = None
            continue

        if CHAPTER_RE.match(line):
            flush_current()
            ctx["chapter"] = strip_heading(line)
            ctx["section"] = None
            ctx["subsection"] = None
            continue

        if SECTION_RE.match(line):
            flush_current()
            ctx["section"] = strip_heading(line)
            ctx["subsection"] = None
            continue

        if SUBSECTION_RE.match(line):
            flush_current()
            ctx["subsection"] = strip_heading(line)
            continue

        article_match = ARTICLE_RE.match(line)
        if article_match:
            flush_current()

            article_no = article_match.group(1)
            article_title = (article_match.group(2) or "").strip()
            is_deleted = bool(article_match.group(3))
            inline_body = (article_match.group(4) or "").strip()

            article_ordinals[article_no] += 1

            article_header = f"##### {article_no}"
            if article_title:
                article_header += f" ({article_title})"
            if is_deleted:
                article_header += " 삭제"

            current = {
                "article_no": article_no,
                "article_title": article_title,
                "article_ordinal": article_ordinals[article_no],
                "is_deleted": is_deleted,
                "article_header": article_header,
                "body_lines": [inline_body] if inline_body else [],
                "part": ctx["part"],
                "chapter": ctx["chapter"],
                "section": ctx["section"],
                "subsection": ctx["subsection"],
            }
            continue

        if current is not None:
            current["body_lines"].append(line)

    flush_current()
    return chunks


def main() -> None:
    print("=" * 70)
    print("Step 4: 기준일 유효 스냅샷 조문 분해")
    print("=" * 70)

    with INPUT_PATH.open(encoding="utf-8") as f:
        snapshots = json.load(f)

    all_chunks: list[dict[str, Any]] = []
    for snapshot in snapshots:
        chunks = chunk_snapshot(snapshot)
        all_chunks.extend(chunks)

        print(
            f"  {snapshot['title']} "
            f"(doc_type={snapshot['doc_type']}, 시행={snapshot.get('enforcement_date')}) "
            f"→ {len(chunks)}개 조문"
        )

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)

    print(f"\n총 raw chunks: {len(all_chunks)}개")
    print(f"→ {OUTPUT_PATH} 저장 완료")


if __name__ == "__main__":
    main()

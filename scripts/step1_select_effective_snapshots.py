# scripts/step1_select_effective_snapshots.py
"""
Step 1: legalize-kr에서 기준일(as_of) 기준으로
'실제로 시행 중인' 법령 스냅샷만 선택한다.

핵심:
- HEAD 파일만 읽지 않는다.
- git history를 뒤로 타면서 기준일에 유효한 revision을 고른다.
- 결과 JSON에 content까지 넣어서 이후 step이 historical snapshot을 그대로 사용하게 한다.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Optional
from zoneinfo import ZoneInfo

import frontmatter

REPO_ROOT = Path("data/legalize-kr")
KR_ROOT = REPO_ROOT / "kr"

TARGET_LAWS = [
    "근로기준법",
    "최저임금법",
    "산업안전보건법",
    "중대재해처벌등에관한법률",
    "근로자퇴직급여보장법",
    "외국인근로자의고용등에관한법률",
    "남녀고용평등과일ㆍ가정양립지원에관한법률",
    "산업재해보상보험법",
]


def git(*args: str, check: bool = True) -> str:
    """repo root에서 git 명령 실행"""
    completed = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if check and completed.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed\n"
            f"STDOUT:\n{completed.stdout}\n"
            f"STDERR:\n{completed.stderr}"
        )
    return completed.stdout


def git_lines(*args: str) -> list[str]:
    return [line.strip() for line in git(*args).splitlines() if line.strip()]


def parse_date(value: Any) -> Optional[date]:
    """frontmatter 날짜를 date로 정규화"""
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value

    text = str(value).strip()
    formats = [
        "%Y-%m-%d",
        "%Y.%m.%d",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S%z",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue

    raise ValueError(f"지원하지 않는 날짜 형식: {value!r}")


def normalize_ministry(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    return [str(value).strip()]


def infer_doc_type(rel_path: str, title: str) -> str:
    """
    canonical role:
    - 법률
    - 시행령
    - 시행규칙
    - 대통령령
    """
    name = Path(rel_path).name

    if name.startswith("법률"):
        return "법률"
    if name.startswith("시행령"):
        return "시행령"
    if name.startswith("시행규칙"):
        return "시행규칙"
    if name.startswith("대통령령"):
        return "대통령령"

    if title.endswith(" 시행령"):
        return "시행령"
    if title.endswith(" 시행규칙"):
        return "시행규칙"

    return "기타"


def fallback_lineage_id(title: str, source_url: str, doc_type: str) -> str:
    base = f"{title}|{source_url}|{doc_type}"
    digest = hashlib.sha1(base.encode("utf-8")).hexdigest()[:12]
    return f"fallback-{digest}"


def build_candidate(
    commit: str,
    rel_path: str,
    root_law_name: str,
    raw_text: str,
) -> dict[str, Any]:
    post = frontmatter.loads(raw_text)
    meta = post.metadata or {}

    title = str(meta.get("제목") or "").strip()
    source_url = str(meta.get("출처") or "").strip()
    law_id = str(meta.get("법령ID") or "").strip()
    law_mst = str(meta.get("법령MST") or "").strip()
    doc_type = infer_doc_type(rel_path, title)
    legal_type = str(meta.get("법령구분") or "").strip()

    lineage_id = law_id or fallback_lineage_id(title, source_url, doc_type)

    return {
        "lineage_id": lineage_id,
        "root_law_name": root_law_name,
        "title": title,  # 예: 근로기준법 시행규칙
        "full_title": title,
        "doc_type": doc_type,  # canonical role
        "legal_type": legal_type,  # 예: 고용노동부령, 환경부령
        "law_id": law_id,
        "law_mst": law_mst,
        "ministry": normalize_ministry(meta.get("소관부처")),
        "promulgation_date": parse_date(meta.get("공포일자")),
        "enforcement_date": parse_date(meta.get("시행일자")),
        "field": str(meta.get("법령분야") or "").strip(),
        "status": str(meta.get("상태") or "").strip(),
        "source_url": source_url,
        "selected_commit": commit,
        "relative_path": rel_path,
        "content": post.content,
    }


def try_read_blob(commit: str, rel_path: str) -> Optional[str]:
    """commit:path에서 파일 내용을 읽는다. 없으면 None"""
    try:
        return git("show", f"{commit}:{rel_path}")
    except RuntimeError:
        return None


def head_lineages_for_law(law_name: str) -> dict[str, dict[str, Any]]:
    """
    HEAD 기준 현재 디렉토리에 존재하는 lineages를 식별한다.
    같은 lineage(같은 law_id)가 여러 파일명으로 공존해도 1개로 본다.
    """
    law_dir = KR_ROOT / law_name
    if not law_dir.exists():
        print(f"⚠️  디렉토리 없음: {law_dir}")
        return {}

    lineages: dict[str, dict[str, Any]] = {}
    for md_file in sorted(law_dir.glob("*.md")):
        raw = md_file.read_text(encoding="utf-8")
        rel_path = md_file.relative_to(REPO_ROOT).as_posix()
        candidate = build_candidate(
            commit="HEAD",
            rel_path=rel_path,
            root_law_name=law_name,
            raw_text=raw,
        )
        lineages.setdefault(candidate["lineage_id"], candidate)

    return lineages


def score_candidate(record: dict[str, Any]) -> tuple[date, date, str]:
    """같은 lineage 안에서 더 나은 revision 선택"""
    enforcement_date = record["enforcement_date"] or date.min
    promulgation_date = record["promulgation_date"] or date.min
    law_mst = record["law_mst"] or ""
    return (enforcement_date, promulgation_date, law_mst)


def select_for_law(law_name: str, as_of: date) -> list[dict[str, Any]]:
    """
    한 법령 디렉토리에서 기준일(as_of) 기준 유효 스냅샷 선택.
    - dir 전체 commit history를 newest -> oldest로 훑는다.
    - 각 lineage마다 최초로 발견되는 "시행 && 시행일자<=as_of" revision을 고른다.
    """
    expected_lineages = head_lineages_for_law(law_name)
    if not expected_lineages:
        return []

    selected: dict[str, dict[str, Any]] = {}
    nearest_future: dict[str, dict[str, Any]] = {}

    # 기준일의 하루 뒤 00:00 KST 이전 commit까지 포함
    before_dt = datetime.combine(
        as_of + timedelta(days=1),
        datetime.min.time(),
        tzinfo=ZoneInfo("Asia/Seoul"),
    )
    before_str = before_dt.strftime("%Y-%m-%d %H:%M:%S %z")

    commits = git_lines("log", "--format=%H", "--before", before_str, "--", f"kr/{law_name}")

    for commit in commits:
        rel_paths = [
            p
            for p in git_lines("-c", "core.quotepath=false", "ls-tree", "-r", "--name-only", commit, f"kr/{law_name}")
            if p.endswith(".md")
        ]

        by_lineage: dict[str, list[dict[str, Any]]] = {}
        for rel_path in rel_paths:
            raw = try_read_blob(commit, rel_path)
            if raw is None:
                continue

            record = build_candidate(
                commit=commit,
                rel_path=rel_path,
                root_law_name=law_name,
                raw_text=raw,
            )
            lineage_id = record["lineage_id"]

            if lineage_id not in expected_lineages:
                continue
            if lineage_id in selected:
                continue

            by_lineage.setdefault(lineage_id, []).append(record)

        for lineage_id, records in by_lineage.items():
            effective = [
                r
                for r in records
                if r["status"] == "시행"
                and r["enforcement_date"] is not None
                and r["enforcement_date"] <= as_of
            ]
            if effective:
                selected[lineage_id] = max(effective, key=score_candidate)
                continue

            future = [
                r
                for r in records
                if r["status"] == "시행"
                and r["enforcement_date"] is not None
                and r["enforcement_date"] > as_of
            ]
            if future:
                best_future = min(future, key=lambda r: r["enforcement_date"])
                prev = nearest_future.get(lineage_id)
                if prev is None or best_future["enforcement_date"] < prev["enforcement_date"]:
                    nearest_future[lineage_id] = best_future

        if len(selected) == len(expected_lineages):
            break

    # 혹시 기준일 이전 시행본을 못 찾은 lineage는 미래 시행본 또는 HEAD를 fallback으로 남긴다.
    for lineage_id, head_record in expected_lineages.items():
        if lineage_id in selected:
            continue

        fallback = dict(nearest_future.get(lineage_id) or head_record)
        eff = fallback.get("enforcement_date")
        eff_text = eff.isoformat() if isinstance(eff, date) else "미상"

        fallback["selection_warning"] = (
            f"기준일 {as_of.isoformat()} 이전 시행본을 찾지 못해 "
            f"{eff_text} 스냅샷을 fallback으로 보존했습니다."
        )
        selected[lineage_id] = fallback

    return sorted(
        selected.values(),
        key=lambda r: (r["doc_type"], r["title"], r["law_mst"]),
    )


def serialize_record(record: dict[str, Any], as_of: date) -> dict[str, Any]:
    out = dict(record)
    out["selected_as_of"] = as_of.isoformat()

    for key in ("promulgation_date", "enforcement_date"):
        value = out.get(key)
        if isinstance(value, date):
            out[key] = value.isoformat()

    return out


def main() -> None:
    default_as_of = datetime.now(ZoneInfo("Asia/Seoul")).date().isoformat()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--as-of",
        default=default_as_of,
        help="기준일 YYYY-MM-DD (기본: Asia/Seoul 오늘)",
    )
    parser.add_argument(
        "--output",
        default="scripts/step1_effective_snapshots.json",
        help="출력 JSON 경로",
    )
    args = parser.parse_args()

    as_of = date.fromisoformat(args.as_of)

    print("=" * 70)
    print(f"Step 1: 기준일 {as_of.isoformat()} 유효 스냅샷 선별")
    print("=" * 70)

    all_records: list[dict[str, Any]] = []
    for law_name in TARGET_LAWS:
        records = select_for_law(law_name, as_of)
        all_records.extend(records)

        print(f"\n[{law_name}]")
        if not records:
            print("  ⚠️  선택된 스냅샷 없음")
            continue

        for r in records:
            eff = r["enforcement_date"].isoformat() if isinstance(r["enforcement_date"], date) else "미상"
            warning = " ⚠" if r.get("selection_warning") else ""
            print(
                f"  ✓ {r['full_title']} | doc_type={r['doc_type']} | "
                f"legal_type={r['legal_type'] or '-'} | 시행={eff} | "
                f"path={r['relative_path']} | commit={r['selected_commit'][:7]}{warning}"
            )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(
            [serialize_record(r, as_of) for r in all_records],
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(f"\n총 선별 스냅샷: {len(all_records)}개")
    print(f"→ {output_path} 저장 완료")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""BR-A 4단계: 명시적으로 승인한 문단만 별도 JSON으로 출력한다."""
import argparse
import csv
import json
from pathlib import Path

from generate_candidates import BASE, build

STATES = {"pending", "approve", "reject"}
FIELDS = ["date", "ability", "action", "decision"]


def approvals(ritual_path, decisions_path):
    candidates = build(ritual_path)["candidates"]
    by_key = {(c["date"], c["ability"], c["evidence"]["action"]): c for c in candidates}

    with decisions_path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != FIELDS:
            raise ValueError("review.csv 열은 date,ability,action,decision 순서여야 합니다.")
        decisions = list(reader)

    seen = set()
    approved = []
    rejected = pending = 0
    for line, record in enumerate(decisions, start=2):
        if None in record or any(v is None for v in record.values()):
            raise ValueError(f"review.csv {line}행: 열 개수가 잘못되었습니다.")
        key = (record["date"].strip(), record["ability"].strip(), record["action"].strip())
        decision = record["decision"].strip().lower()
        if key in seen:
            raise ValueError(f"review.csv {line}행: 중복된 검토 항목입니다.")
        seen.add(key)
        if decision not in STATES:
            raise ValueError(f"review.csv {line}행: pending / approve / reject 중에서 선택하세요.")
        if key not in by_key:
            # 원본 행동/능력/날짜가 변경됐다면 이전 승인이 재사용되면 안 된다.
            raise ValueError(f"review.csv {line}행: 현재 리추얼 후보와 일치하지 않습니다. 재검토하세요.")
        if decision == "approve":
            c = by_key[key]
            approved.append({
                "id": c["id"],
                "ability": c["ability"],
                "date": c["date"],
                "paragraph": c["paragraph"],
                "evidence": c["evidence"],
                "approval_status": "approved"
            })
        elif decision == "reject":
            rejected += 1
        else:
            pending += 1

    # review.csv에 없는 신규 후보는 자동으로 승인되지 않는다.
    approved.sort(key=lambda c: (c["ability"], c["date"], c["id"]))
    return {
        "schema_version": 1,
        "publication_status": "reviewed_approved_only",
        "counts": {
            "all_candidates": len(candidates),
            "approved": len(approved),
            "rejected": rejected,
            "pending_in_review": pending,
            "not_reviewed": len(candidates) - len(seen)
        },
        "approved": approved
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ritual", type=Path, default=BASE / "input" / "ritual.csv")
    parser.add_argument("--review", type=Path, default=BASE / "review.csv")
    parser.add_argument("--output", type=Path, default=BASE / "approved.json")
    args = parser.parse_args()
    data = approvals(args.ritual, args.review)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"검토 완료: 승인 {data['counts']['approved']} / 거절 {data['counts']['rejected']} / 보류 {data['counts']['pending_in_review']} / 미검토 {data['counts']['not_reviewed']}")
    print("승인된 문장만 저장:", args.output)


if __name__ == "__main__":
    main()

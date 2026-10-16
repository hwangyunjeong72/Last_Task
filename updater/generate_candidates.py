#!/usr/bin/env python3
"""BR-A 3단계: 리추얼 CSV에서 근거가 있는 문단 후보만 생성한다.

후보는 승인 전 콘텐츠다. 공개 사이트나 공개 저장소에 자동 게시하지 않는다.
"""
import argparse
import hashlib
import json
from pathlib import Path

from update import BASE, EVALUATIONS, SKILLS, read_csv

ORDER = ("자기조절력", "대인관계력", "자기동기력")
COLUMNS = ["date", "ability", "action", "evaluation", "source"]


def build(input_path):
    rows = read_csv(input_path, COLUMNS, "date")
    candidates = []
    for row in sorted(rows, key=lambda r: (r["date"], r["ability"])):
        skill = row["ability"].strip()
        action = row["action"].strip()
        rating = row["evaluation"].strip()
        source = row["source"].strip()
        if skill not in SKILLS or rating not in EVALUATIONS:
            raise ValueError(f"{row['date']}: 능력 또는 평가 값이 잘못되었습니다.")
        # 미분류, 빈 행동, 미평가 날짜는 근거를 충분히 갖춘 후보가 아니므로 제외.
        if skill not in ORDER or not action or rating == "미평가":
            continue
        if any(ch in action for ch in "\r\n") or len(action) > 200:
            raise ValueError(f"{row['date']}: 행동은 200자 이내 한 줄 요약이어야 합니다.")
        key = "|".join((row["date"], skill, action, source))
        identifier = hashlib.sha256(key.encode("utf-8")).hexdigest()[:12]
        # 입력에서 확인되는 사실만 재구성. AI 창작/추측/제3자 이름 추가 없음.
        text = f"{row['date']}에는 {action.rstrip('.。')}."
        candidates.append({
            "id": f"ritual-{identifier}",
            "ability": skill,
            "date": row["date"],
            "paragraph": text,
            "evidence": {
                "source": source,
                "action": action,
                "evaluation": rating
            },
            "approval_status": "pending"
        })
    return {
        "schema_version": 1,
        "publication_status": "draft_not_approved",
        "notice": "승인 전 문단 후보입니다. 공개 사이트에 자동 게시하지 마세요.",
        "counts": {skill: sum(c["ability"] == skill for c in candidates) for skill in ORDER},
        "candidates": sorted(candidates, key=lambda c: (ORDER.index(c["ability"]), c["date"]))
    }


def main():
    parser = argparse.ArgumentParser(description="리추얼 문단 후보 생성 (승인 전)")
    parser.add_argument("--input", type=Path, default=BASE / "input" / "ritual.csv")
    parser.add_argument("--output", type=Path, default=BASE / "output" / "candidates.json")
    args = parser.parse_args()
    result = build(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("후보 생성 완료:", args.output)
    print("능력별 후보:", result["counts"])
    print("게시 상태: 승인 전 (웹사이트 미반영)")


if __name__ == "__main__":
    main()

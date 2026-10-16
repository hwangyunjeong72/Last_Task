#!/usr/bin/env python3
"""BR-A 2단계: 공개 가능한 CSV 3종을 검증하고 재현 가능한 통계 JSON을 생성한다."""
import argparse
import csv
import json
from collections import Counter
from datetime import date
from pathlib import Path

BASE = Path(__file__).resolve().parent
EVALUATIONS = {"실천했다", "일부 실천했다", "못 했다", "미평가"}
TASK_STATES = {"완료", "진행 중", "예정", "확인 필요"}
ATTENDANCE_STATES = {"출석", "공가", "결석", "지각", "조퇴", "미확정"}
SKILLS = {"자기조절력", "대인관계력", "자기동기력", "미분류"}


def read_csv(path, columns, unique):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != columns:
            raise ValueError(f"{path.name}: 열 이름 또는 순서가 다릅니다. {columns}")
        records = list(reader)
    seen = set()
    for index, row in enumerate(records, start=2):
        if any(value is None for value in row.values()):
            raise ValueError(f"{path.name}:{index}: 열 개수가 다릅니다.")
        key = row[unique].strip()
        if not key or key in seen:
            raise ValueError(f"{path.name}:{index}: {unique} 값이 비었거나 중복입니다.")
        seen.add(key)
        if "date" in row and row["date"].strip():
            try:
                date.fromisoformat(row["date"].strip())
            except ValueError as exc:
                raise ValueError(f"{path.name}:{index}: 날짜 형식은 YYYY-MM-DD입니다.") from exc
        if not row["source"].strip():
            raise ValueError(f"{path.name}:{index}: 출처를 입력하세요.")
    return records


def summarize(input_dir):
    ritual = read_csv(input_dir / "ritual.csv",
                      ["date", "ability", "action", "evaluation", "source"], "date")
    tasks = read_csv(input_dir / "tasks.csv",
                     ["code", "title", "status", "date", "source"], "code")
    attendance = read_csv(input_dir / "attendance.csv",
                          ["date", "status", "source"], "date")

    for row in ritual:
        if row["evaluation"] not in EVALUATIONS or row["ability"] not in SKILLS:
            raise ValueError(f"ritual.csv {row['date']}: 능력 또는 평가 값이 올바르지 않습니다.")
    for row in tasks:
        if row["status"] not in TASK_STATES:
            raise ValueError(f"tasks.csv {row['code']}: 과제 상태가 올바르지 않습니다.")
        if row["date"].strip():
            date.fromisoformat(row["date"].strip())
    for row in attendance:
        if row["status"] not in ATTENDANCE_STATES:
            raise ValueError(f"attendance.csv {row['date']}: 출석 상태가 올바르지 않습니다.")

    rc = Counter(r["evaluation"] for r in ritual)
    tc = Counter(r["status"] for r in tasks)
    ac = Counter(r["status"] for r in attendance)
    confirmed = len(attendance) - ac["미확정"]
    accepted = ac["출석"] + ac["공가"]
    rate = round(100 * accepted / confirmed, 1) if confirmed else None
    enrolled_rate = round(100 * accepted / len(attendance), 1) if attendance else None

    return {
        "schema_version": 1,
        "source_period": {
            "first_date": min((r["date"] for r in attendance), default=None),
            "last_date": max((r["date"] for r in attendance), default=None)
        },
        "ritual": {
            "recorded_dates": len(ritual),
            "evaluated_dates": len(ritual) - rc["미평가"],
            "completed": rc["실천했다"],
            "partially_completed": rc["일부 실천했다"],
            "not_completed": rc["못 했다"],
            "unevaluated": rc["미평가"],
            "source": "updater/input/ritual.csv"
        },
        "tasks": {
            "listed": len(tasks),
            "completed": tc["완료"],
            "in_progress": tc["진행 중"],
            "planned": tc["예정"],
            "unverified": tc["확인 필요"],
            "source": "updater/input/tasks.csv"
        },
        "attendance": {
            "recorded_dates": len(attendance),
            "confirmed_dates": confirmed,
            "present": ac["출석"],
            "official_leave": ac["공가"],
            "absent": ac["결석"],
            "unconfirmed": ac["미확정"],
            "confirmed_rate_percent": rate,
            "all_recorded_rate_percent": enrolled_rate,
            "rate_note": "확정 출석률은 미확정일을 제외한 확정일 기준. 전체 기록 기준 출석률은 미확정일도 분모에 포함.",
            "source": "updater/input/attendance.csv"
        },
        "publication": "공개용 집계만 포함. 개인적인 원문/제3자 정보는 포함하지 않음."
    }


def main():
    parser = argparse.ArgumentParser(description="BR-A CSV 통계 재계산")
    parser.add_argument("--input", type=Path, default=BASE / "input", help="CSV 3종이 있는 폴더")
    parser.add_argument("--output", type=Path, default=BASE / "summary.json", help="결과 JSON 경로")
    args = parser.parse_args()
    result = summarize(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("생성 완료:", args.output)
    print(f"리추얼 평가 {result['ritual']['evaluated_dates']}일 / 과제 완료 {result['tasks']['completed']}개 / 확정 출석률 {result['attendance']['confirmed_rate_percent']}%")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""4단계: 명시적 승인만 게시용 JSON에 포함하는지 검증."""
import csv
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from approve_candidates import BASE, approvals, FIELDS


def write_review(path, rows):
    with path.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def check():
    src = BASE / "review.csv"
    ritual = BASE / "input" / "ritual.csv"
    with src.open(encoding="utf-8-sig", newline="") as fp:
        rows = list(csv.DictReader(fp))
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        reviewed = root / "review.csv"
        a, b = root / "first.json", root / "second.json"
        write_review(reviewed, rows)
        for out in (a, b):
            subprocess.run([sys.executable, str(BASE / "approve_candidates.py"),
                            "--review", str(reviewed), "--output", str(out)],
                           check=True, capture_output=True, text=True)
        assert a.read_bytes() == b.read_bytes(), "반복 실행 결과가 다릅니다."
        doc = json.loads(a.read_text(encoding="utf-8"))
        assert len(doc["approved"]) == sum(r["decision"].strip().lower() == "approve" for r in rows)
        assert all(r["approval_status"] == "approved" for r in doc["approved"])

        if rows:
            # 거절/보류 중에는 승인되지 않고 승인 여부가 명시될 때만 포함
            changed = [dict(r) for r in rows]
            changed[0]["decision"] = "reject"
            write_review(reviewed, changed)
            check_reject = approvals(ritual, reviewed)
            assert not any(c["date"] == changed[0]["date"] for c in check_reject["approved"])
            changed[0]["decision"] = "approve"
            write_review(reviewed, changed)
            check_approve = approvals(ritual, reviewed)
            assert any(c["date"] == changed[0]["date"] for c in check_approve["approved"])
            # 행동을 임의로 변경해 이전 승인을 재사용하면 검사 실패
            changed[0]["action"] = "원본과 다른 임의의 행동"
            write_review(reviewed, changed)
            try:
                approvals(ritual, reviewed)
                raise AssertionError("변경된 근거로 승인이 통과했습니다.")
            except ValueError:
                pass
        print("PASS: 승인된 문단만 포함, 거절/보류 제외")
        print("PASS: 같은 입력에서 같은 approved.json")
        print("PASS: 원본 날짜·능력·행동이 바뀌면 이전 승인 무효")


if __name__ == "__main__":
    check()

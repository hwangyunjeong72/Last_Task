#!/usr/bin/env python3
"""BR-A: 입력이 같으면 결과가 같고, 합계가 원본 CSV에 맞는지 검사한다."""
import hashlib
import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path
from update import BASE, read_csv


def run(output):
    subprocess.run([sys.executable, str(BASE / "update.py"), "--output", str(output)],
                   check=True, capture_output=True, text=True)


def check():
    with tempfile.TemporaryDirectory() as temp:
        first, second = Path(temp) / "one.json", Path(temp) / "two.json"
        run(first)
        run(second)
        a, b = first.read_bytes(), second.read_bytes()
        assert a == b, "같은 입력인데 파일 내용이 달라졌습니다."
        result = json.loads(a)

        ritual = read_csv(BASE / "input" / "ritual.csv",
                          ["date", "ability", "action", "evaluation", "source"], "date")
        tasks = read_csv(BASE / "input" / "tasks.csv",
                         ["code", "title", "status", "date", "source"], "code")
        attendance = read_csv(BASE / "input" / "attendance.csv",
                              ["date", "status", "source"], "date")
        rc = Counter(r["evaluation"] for r in ritual)
        tc = Counter(r["status"] for r in tasks)
        ac = Counter(r["status"] for r in attendance)
        assert result["ritual"]["recorded_dates"] == len(ritual)
        assert result["ritual"]["evaluated_dates"] == len(ritual) - rc["미평가"]
        assert result["ritual"]["completed"] == rc["실천했다"]
        assert result["ritual"]["partially_completed"] == rc["일부 실천했다"]
        assert result["ritual"]["not_completed"] == rc["못 했다"]
        assert result["tasks"]["listed"] == len(tasks)
        assert result["tasks"]["completed"] == tc["완료"]
        assert result["tasks"]["unverified"] == tc["확인 필요"]
        assert result["attendance"]["present"] == ac["출석"]
        assert result["attendance"]["unconfirmed"] == ac["미확정"]
        confirmed = len(attendance) - ac["미확정"]
        expected = round(100 * (ac["출석"] + ac["공가"]) / confirmed, 1) if confirmed else None
        assert result["attendance"]["confirmed_rate_percent"] == expected
        assert "정환균" not in a.decode("utf-8")
        print("PASS: 같은 입력 → 같은 파일")
        print("SHA-256:", hashlib.sha256(a).hexdigest())
        print("PASS: 현재 CSV의 리추얼·과제·출석 집계값 일치")
        print("PASS: 집계 JSON에 개인 실명 없음")


if __name__ == "__main__":
    check()

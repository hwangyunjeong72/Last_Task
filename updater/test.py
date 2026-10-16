#!/usr/bin/env python3
"""BR-A 2단계 재현성·데이터 검증 테스트."""
import hashlib
import tempfile
from pathlib import Path
from update import BASE, summarize, main
import json
import subprocess
import sys

def run(output):
    subprocess.run([sys.executable, str(BASE / "update.py"), "--output", str(output)], check=True, capture_output=True)

def check():
    with tempfile.TemporaryDirectory() as temp:
        first, second = Path(temp) / "one.json", Path(temp) / "two.json"
        run(first)
        run(second)
        a, b = first.read_bytes(), second.read_bytes()
        assert a == b, "같은 입력인데 파일 내용이 달라졌습니다."
        result = json.loads(a)
        assert result["ritual"] == {
            "recorded_dates": 42, "evaluated_dates": 41, "completed": 9,
            "partially_completed": 31, "not_completed": 1, "unevaluated": 1,
            "source": "updater/input/ritual.csv"
        }
        assert result["tasks"]["listed"] == 11
        assert result["tasks"]["completed"] == 1
        assert result["attendance"]["present"] == 41
        assert result["attendance"]["unconfirmed"] == 1
        assert result["attendance"]["confirmed_rate_percent"] == 100.0
        assert result["attendance"]["all_recorded_rate_percent"] == 97.6
        assert "정환균" not in a.decode("utf-8")
        print("PASS: 동일 입력 → 동일 파일")
        print("SHA-256:", hashlib.sha256(a).hexdigest())
        print("PASS: 리추얼 42/41, 과제 목록 11, 출석 41/42 및 2개 출석률 검증")
        print("PASS: 집계 결과에 개인 실명 없음")

if __name__ == "__main__":
    check()

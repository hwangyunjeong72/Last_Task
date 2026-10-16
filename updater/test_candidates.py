#!/usr/bin/env python3
"""후보 생성의 재현성·근거·승인 전 상태 검사."""
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from generate_candidates import BASE, ORDER, build


def check():
    with tempfile.TemporaryDirectory() as root:
        first = Path(root) / "a.json"
        second = Path(root) / "b.json"
        for output in (first, second):
            subprocess.run([sys.executable, str(BASE / "generate_candidates.py"),
                            "--output", str(output)], check=True, capture_output=True)
        data = first.read_bytes()
        assert data == second.read_bytes(), "같은 CSV에서 결과 파일이 서로 다릅니다."
        result = json.loads(data)
        expected = build(BASE / "input" / "ritual.csv")
        assert result == expected
        assert result["publication_status"] == "draft_not_approved"
        assert len({c["id"] for c in result["candidates"]}) == len(result["candidates"])
        for c in result["candidates"]:
            assert c["ability"] in ORDER
            assert c["date"] in c["paragraph"]
            assert c["evidence"]["source"]
            assert c["evidence"]["action"]
            assert c["approval_status"] == "pending"
            assert c["paragraph"].endswith(".")
        assert not (BASE.parent / "candidates.json").exists(), "저장소 최상위 후보 파일을 발견했습니다."
        print("PASS: 동일 입력 → 동일 후보 JSON")
        print("PASS: 모든 후보에 날짜·능력·근거·승인 대기 상태")
        print("PASS: 게시용 파일은 만들지 않음")
        print("SHA-256:", hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    check()

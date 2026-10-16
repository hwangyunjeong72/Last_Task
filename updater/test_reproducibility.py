#!/usr/bin/env python3
"""BR-A 6단계: 같은 입력·새 작업 폴더·승인 전 노출 방지 자동 검사."""
import csv
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = ("summary.json", "approved.json")
REVIEW_COLS = ("date", "ability", "action", "decision")


def run(root):
    updater = root / "updater"
    cmds = [
        ("update.py", "--output", str(updater / "summary.json")),
        ("generate_candidates.py", "--output", str(updater / "output" / "candidates.json")),
        ("approve_candidates.py", "--output", str(updater / "approved.json")),
    ]
    for cmd in cmds:
        subprocess.run([sys.executable, str(updater / cmd[0]), *cmd[1:]],
                       cwd=root, check=True, capture_output=True, text=True)
    return {file: (updater / file).read_bytes() for file in FILES}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def check():
    with tempfile.TemporaryDirectory(prefix="br-a-verify-") as base:
        base = Path(base)
        # 복제 작업 폴더: 이전 생성물, 캐시, Git 상태에 의존하지 않게 새로 구성
        for number in ("first", "second", "fresh"):
            root = base / number
            (root / "updater" / "input").mkdir(parents=True)
            for filename in ("update.py", "generate_candidates.py", "approve_candidates.py", "review.csv"):
                shutil.copy2(ROOT / "updater" / filename, root / "updater" / filename)
            for filename in ("ritual.csv", "tasks.csv", "attendance.csv"):
                shutil.copy2(ROOT / "updater" / "input" / filename, root / "updater" / "input" / filename)
            shutil.copy2(ROOT / "index.html", root / "index.html")

        first = run(base / "first")
        second = run(base / "second")
        fresh = run(base / "fresh")
        for name in FILES:
            assert first[name] == second[name], f"두 번 실행 결과가 다릅니다: {name}"
            assert first[name] == fresh[name], f"새 폴더 재실행 결과가 다릅니다: {name}"
            print(f"PASS {name}: 2회 및 새 폴더 동일 출력 | SHA-256: {digest(first[name])}")

        # 승인 결과와 후보의 포함 관계까지 확인
        draft = json.loads((base / "first" / "updater" / "output" / "candidates.json").read_text(encoding="utf-8"))
        approved = json.loads(first["approved.json"])
        review = ROOT / "updater" / "review.csv"
        with review.open(encoding="utf-8-sig", newline="") as file:
            decisions = list(csv.DictReader(file))
        assert all(row["decision"].strip().lower() in ("pending", "approve", "reject") for row in decisions)
        approved_count = sum(row["decision"].strip().lower() == "approve" for row in decisions)
        assert len(approved["approved"]) == approved_count
        candidate_ids = {c["id"] for c in draft["candidates"]}
        assert all(c["id"] in candidate_ids and c["approval_status"] == "approved" for c in approved["approved"])

        # 추가 검사: 모든 후보를 거절한 별도 폴더에서 결과 승인 0개여야 함
        reject_root = base / "fresh"
        review_path = reject_root / "updater" / "review.csv"
        with review_path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=REVIEW_COLS)
            writer.writeheader()
            for row in decisions:
                writer.writerow({**row, "decision": "reject"})
        rejected = json.loads(run(reject_root)["approved.json"])
        assert rejected["approved"] == [] and rejected["counts"]["approved"] == 0
        print("PASS: 모두 거절 시 승인 문단 0개")

        html = (ROOT / "index.html").read_text(encoding="utf-8")
        assert "./updater/approved.json" in html
        assert "./updater/summary.json" in html
        assert "candidates.json" not in html
        assert "item.approval_status === 'approved'" in html
        assert "textContent = item.paragraph" in html
        assert not (ROOT / "updater" / "output" / "candidates.json").exists(), (
            "현재 체크아웃에서 후보 파일이 보이면 공개 경로 노출 여부를 확인하세요."
        )
        print("PASS: 공개 화면은 승인 JSON만 읽고 승인 상태를 검증")
        print("PASS: 검토용 후보 파일을 저장소에 게시하지 않음")


if __name__ == "__main__":
    check()

#!/usr/bin/env python3
"""BR-A 제출 ZIP: 허용된 파일만 포함하고 검증 로그/해시를 함께 기록."""
import argparse
import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UP = ROOT / "updater"
OUTPUT = ROOT / "BR-A_자동갱신장치_제출.zip"

FILES = [
    ".github/workflows/br-a-update.yml",
    "updater/update.py", "updater/test.py",
    "updater/generate_candidates.py", "updater/test_candidates.py",
    "updater/approve_candidates.py", "updater/test_approval.py",
    "updater/test_site.py", "updater/test_reproducibility.py",
    "updater/input/ritual.csv", "updater/input/tasks.csv",
    "updater/input/attendance.csv", "updater/review.csv",
    "updater/summary.json", "updater/approved.json",
    "updater/README.md"
]

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, default=OUTPUT)
    args = p.parse_args()
    for path in FILES:
        if not (ROOT / path).is_file():
            raise SystemExit(f"필수 파일이 없습니다: {path}")
    # 미승인 후보 파일을 ZIP에 넣지 않는다.
    approved = json.loads((UP / "approved.json").read_text(encoding="utf-8"))
    assert approved["publication_status"] == "reviewed_approved_only"
    assert all(x["approval_status"] == "approved" for x in approved["approved"])
    expected = len(approved["approved"])
    assert approved["counts"]["approved"] == expected

    manifest = {"files": {}, "exclusions": ["private records", "unapproved candidates", "credentials"]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.output, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in FILES:
            data = (ROOT / path).read_bytes()
            manifest["files"][path] = hashlib.sha256(data).hexdigest()
            zf.writestr(path, data)
        proof_path = ROOT / "updater" / "output" / "verification.txt"
        if not proof_path.is_file():
            raise SystemExit("검증 증거 verification.txt를 먼저 생성하세요.")
        proof = proof_path.read_text(encoding="utf-8")
        if "PASS" not in proof or "SHA-256" not in proof:
            raise SystemExit("검증 증거가 비어 있거나 검증되지 않았습니다.")
        zf.writestr("evidence/verification.txt", proof)
        zf.writestr("evidence/manifest_sha256.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
        howto = (
            "BR-A 제출 ZIP 확인 방법\n"
            "1) updater/input/ 세 CSV를 확인합니다. 원본 개인 기록은 제외했습니다.\n"
            "2) Python 3.11이 있는 환경에서 python updater/update.py, python updater/generate_candidates.py, python updater/approve_candidates.py 실행\n"
            "3) python updater/test_reproducibility.py 실행 후 evidence/verification.txt의 PASS와 SHA-256 비교\n"
            "교육기관 PC에 Python이 없다면 GitHub 저장소 Actions의 BR-A 자동 갱신 실행을 이용합니다.\n"
            "사이트: https://hwangyunjeong72.github.io/Last_Task/\n"
            "저장소: https://github.com/hwangyunjeong72/Last_Task\n"
            "AI 역할: 코드·검사·문장 후보 생성 보조. 본인 판단: 원본 검토·문장 승인·공개 여부 결정.\n"
        )
        zf.writestr("SUBMISSION_README.txt", howto)
    with zipfile.ZipFile(args.output) as zf:
        bad = zf.testzip()
        if bad:
            raise SystemExit(f"ZIP 손상: {bad}")
    print(f"ZIP 생성 성공: {args.output.name} ({args.output.stat().st_size} bytes)")
    print(f"포함: 실행 소스 {len(FILES)}개, 검증 증거, SHA-256 파일목록, 제출 안내")
    print("제외: 원본 리추얼/출석 TXT·JSON, DOCX, 미승인 candidates.json, 비밀키")

if __name__ == "__main__":
    main()

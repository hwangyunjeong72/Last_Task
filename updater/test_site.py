#!/usr/bin/env python3
"""BR-A 5단계: 공개 화면은 승인 문단만 사용하고 자동 숫자 경로를 연결하는지 검사."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
html = (ROOT / "index.html").read_text(encoding="utf-8")
summary = json.loads((ROOT / "updater" / "summary.json").read_text(encoding="utf-8"))
approved = json.loads((ROOT / "updater" / "approved.json").read_text(encoding="utf-8"))

assert "./updater/summary.json" in html, "자동 숫자 JSON 연결이 없습니다."
assert "./updater/approved.json" in html, "승인 JSON 연결이 없습니다."
assert "candidates.json" not in html, "승인 전 후보를 사이트에서 참조합니다."
assert "textContent = item.paragraph" in html, "HTML 삽입 대신 안전한 텍스트 렌더링을 사용하세요."
assert summary["schema_version"] == 1
assert approved["schema_version"] == 1
assert approved["publication_status"] == "reviewed_approved_only"
assert all(item["approval_status"] == "approved" for item in approved["approved"])
assert approved["counts"]["approved"] == len(approved["approved"])
assert len({x["id"] for x in approved["approved"]}) == len(approved["approved"])
print("PASS: 기존 사이트는 승인된 문단 JSON만 표시")
print("PASS: 자동 계산 숫자 JSON 참조")
print("PASS: 승인 상태·게시 파일 구조 검증")

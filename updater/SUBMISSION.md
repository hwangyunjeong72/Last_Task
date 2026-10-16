# BR-A 마지막 제출 — 자동 갱신 장치 ZIP

이 폴더는 GitHub Pages 포트폴리오의 **리추얼·과제·출석 숫자 갱신 및 승인 문단 게시 장치**입니다.

## 학교 PC에서 제출 ZIP 만들기 (Python 설치 불필요)

1. [저장소 Actions](https://github.com/hwangyunjeong72/Last_Task/actions)에 접속합니다.
2. 왼쪽에서 **BR-A 제출 ZIP 만들기**를 누릅니다.
3. `Run workflow` → `main` → `Run workflow`를 누릅니다.
4. 실행의 **Success**(초록색 체크)를 확인합니다.
5. 해당 실행의 맨 아래 **Artifacts → BR-A-최종제출-ZIP**을 클릭해 내려받습니다.
6. 다운로드된 바깥 ZIP을 풀면 `BR-A_자동갱신장치_제출.zip`이 있습니다. **이 안쪽 ZIP이 제출 파일입니다.**

## ZIP에 포함되는 것
- 실행 코드: `update.py`, `generate_candidates.py`, `approve_candidates.py`
- 자동 테스트: `test.py`, `test_candidates.py`, `test_approval.py`, `test_site.py`, `test_reproducibility.py`
- 입력 파일 3종: `ritual.csv`, `tasks.csv`, `attendance.csv`
- 결정 파일: `review.csv` (사람의 승인·보류·거절), `approved.json` (승인만), `summary.json`
- `evidence/verification.txt`: GitHub 서버의 PASS 출력, SHA-256 값 및 검사 대상 커밋
- `evidence/manifest_sha256.json`: ZIP에 넣은 개별 파일의 해시
- `SUBMISSION_README.txt`: 확인 방법 3단계와 AI/본인 역할
- `updater/README.md` 및 기존 Actions 실행 설정

## 제외하는 것
- 원본 리추얼 TXT/JSON, 원본 출석 TXT, 소설/논문 DOCX, 개인·제3자 이야기
- 미승인 문단 후보 `candidates.json` 및 `updater/private/`
- 인증 키, 비밀번호, .env

## 제출과 증빙
- 공개 사이트: https://hwangyunjeong72.github.io/Last_Task/
- GitHub: https://github.com/hwangyunjeong72/Last_Task
- 자동 실행: [BR-A 자동 갱신 실행](https://github.com/hwangyunjeong72/Last_Task/actions)
- ZIP 생성 전 모든 검사가 통과해야 아티팩트 업로드가 실행됩니다.
- 산출 JSON은 입력 CSV에만 기반하므로 실행 날짜/시간에 영향받지 않습니다.

## 남아 있는 주의사항
**제출 ZIP에 원본 기록을 넣지 않았다고 공개 GitHub 저장소의 과거 원본 기록이 보호되는 것은 아닙니다.** 저장소에 이미 올린 원본 자료와 Git 이력은 제출 전에 별도 검토 및 공개 범위 정리가 필요합니다. 지금 작업은 원본 파일을 삭제하거나 Git 이력을 수정하지 않습니다.

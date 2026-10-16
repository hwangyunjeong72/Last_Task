# BR-A 자동 갱신 장치 — 2단계 (숫자 집계)

현재 기존 `index.html`은 변경하지 않습니다. 이 도구는 **CSV → 공개용 집계 JSON**까지만 처리합니다. 승인 문단과 웹사이트 자동 반영은 후속 단계입니다.

## 입력 파일 3종
- `input/ritual.csv`: 2026-08-11~10-14 전체 42개 날짜. 평가 41일, 미평가 1일. `action`은 공개 가능한 일부 사례만 요약했습니다. 동료 서술·개인 일화·이름은 담지 않았습니다.
- `input/tasks.csv`: T01~T11 전체 11개 목록. **완료 검증 근거가 있는 T10만 완료**, 나머지 10개는 `확인 필요`입니다. 실제 완료 상태는 증빙 검토 후 직접 수정하세요.
- `input/attendance.csv`: 2026-08-11~10-14 전체 42개 날짜. 확정 출석 41일, 10-14 미확정 1일. 입·퇴실 시각은 공개하지 않습니다.

## Python 설치 없이 GitHub에서 실행하기 (권장)

**교육기관 컴퓨터에는 Python을 설치할 필요가 없습니다.** PC에 Python이 없다면 다음 순서로 실행하세요.

1. [Last_Task Actions](https://github.com/hwangyunjeong72/Last_Task/actions) 열기
2. 왼쪽 목록에서 `BR-A 자동 갱신 실행` 선택
3. 오른쪽 `Run workflow` 선택 → 브랜치 `main` 확인 → 초록색 `Run workflow` 클릭
4. 새로 생긴 실행을 눌러 초록색 체크(성공)를 확인
5. 화면 아래 `Artifacts`에서 `br-a-summary`를 내려받거나 `updater/summary.json` 확인

GitHub 서버가 Python 3.11을 준비한 뒤 `update.py` → `test.py` 순서로 실행합니다.
검사가 통과하고 계산 결과가 달라졌을 때만 **`updater/summary.json` 한 파일을 자동 커밋**합니다.
기존 `index.html`, 이력서, 자기소개서, 경력기술서, 논문 파일은 수정하지 않습니다.
이 단계는 성장 기록 화면 자체를 자동으로 바꾸지 않으며, 해당 기능은 5단계에서 연결합니다.

**문제 해결:** `Run workflow`가 보이지 않으면 `main` 브랜치인지, GitHub 저장소의 Actions 사용이 허용됐는지 확인하세요.
쓰기 권한 오류가 나타나면 저장소 `Settings → Actions → General → Workflow permissions` 설정을 확인해야 합니다.
공개 CSV에는 민감정보를 넣지 마세요. 자동 커밋은 승인 전 문단을 게시하지 않습니다.

## 실행 (Windows 11 / PowerShell)
1. [저장소](https://github.com/hwangyunjeong72/Last_Task)에서 `Code → Download ZIP`을 눌러 압축을 풉니다.
2. 압축을 푼 폴더에서 `updater`에 들어갑니다.
3. 폴더 주소창에 `powershell`을 입력해 터미널을 엽니다.
4. 다음 명령어를 **한 줄씩** 실행합니다.

```powershell
python --version
python update.py
python test.py
```

Python 명령을 못 찾으면 Windows에서는 `py --version`, `py update.py`, `py test.py`도 시도할 수 있습니다. Python 3.9 이상을 사용하세요. 외부 패키지/API 키는 불필요합니다.

## 결과
- `summary.json`: 출석·리추얼·과제 숫자와 CSV 출처가 담긴 JSON
- 동일한 CSV에서는 날짜나 실행 시간이 끼어들지 않아 같은 JSON 바이트가 나옵니다.
- CSV 열 순서와 날짜·상태·중복·출처를 검사합니다. 오류가 있으면 숫자를 만들어 내지 않고 중단합니다.

### 현재 원본 자료 기준
- 리추얼: 기록 42일, 평가 41일(실천 9, 일부 31, 미실천 1), 미평가 1일
- 과제: 목록 11개, 완료 확인 1개(T10), 확인 필요 10개. 이는 최종 과제 완료 횟수가 아닙니다.
- 출석: 확정 41일, 미확정 1일. **확정일 기준 100.0%** / **기록 전체 42일 기준 97.6%**. 서로 다른 분모를 섞지 마세요.
- 모든 수치는 2026-10-14까지의 원본 기록을 기준으로 하며 실시간 정보가 아닙니다.

## 새 기록 넣기
- CSV 각 날짜는 `YYYY-MM-DD`, 과제 코드는 유일해야 합니다.
- 리추얼 평가: `실천했다`, `일부 실천했다`, `못 했다`, `미평가`
- 능력: `자기조절력`, `대인관계력`, `자기동기력`, `미분류`
- 과제 상태: `완료`, `진행 중`, `예정`, `확인 필요`
- 출석 상태: `출석`, `공가`, `결석`, `지각`, `조퇴`, `미확정`
- 원본에 입실·퇴실 시간이나 동료 개인정보가 있더라도 **공개 CSV에는 넣지 마세요.**
- 주의: 지각·조퇴 등 복합 출결 정책의 공식 출석률은 별도 검토가 필요합니다. 현재 원본에는 확정 출석/미확정만 있습니다.

## 개인정보 안전 수칙
- 원본 리추얼 JSON/TXT, 출석 TXT, 소설 DOCX 등의 **기존 공개 파일은 여전히 GitHub에 존재**합니다. 이번 2단계에서 이 파일들은 삭제하거나 변경하지 않았습니다.
- 비공개 원본은 저장소 바깥 또는 `updater/private/`에 보관하세요. `.gitignore`가 적용되어도 과거 Git 커밋에서 삭제되지는 않습니다.
- 공개 저장소의 원본과 Git 기록 삭제는 검토 후 별도 단계로 처리해야 합니다. 공개한 비밀 키가 있다면 기록 삭제와 별개로 즉시 교체해야 합니다.
- `updater/output/`은 `.gitignore` 대상이고 `updater/summary.json`은 공개용 수치만 담습니다.

## 테스트
`python test.py`는 같은 입력을 임시 폴더에서 두 번 계산해 결과 바이트 및 SHA-256을 대조하고, 초기 숫자를 검사합니다. **이 테스트는 현재 2026-10-14 원본 스냅샷의 숫자로 고정**되어 있으므로 추후 새 기록을 추가하면 기대 숫자도 업데이트해야 합니다.

## 다음 단계
3단계: 날짜·출처가 있는 능력별 문단 후보 생성, 4단계: 사람 승인 후에만 게시, 5단계: 사이트 표시.

## 3단계: 능력별 문단 후보 생성 (GitHub에서 실행)

기존의 **BR-A 자동 갱신 실행** 버튼을 사용합니다.

1. 저장소 [Actions](https://github.com/hwangyunjeong72/Last_Task/actions) → `BR-A 자동 갱신 실행`.
2. `Run workflow` → `main` → `Run workflow`.
3. 초록색 체크가 표시되면 해당 실행을 엽니다.
4. `Artifacts`에서 `br-a-candidates-review` 압축파일을 받습니다.
5. 압축을 풀어 `candidates.json`을 열고 날짜·근거·문단 내용을 검토합니다.

GitHub 서버가 `update.py`와 `test.py`를 실행한 뒤 `generate_candidates.py`와 `test_candidates.py`를 실행합니다.
**후보 파일은 `updater/output/candidates.json`에만 생성하며 공개 사이트나 GitHub 커밋에는 자동 게시하지 않습니다.**
초기 CSV는 42일 중 날짜·능력·행동 요약이 실제 입력된 4개 날짜만 후보로 만듭니다. 나머지 빈 행동·미분류 날짜는 문장을 추측해 만들어 내지 않습니다.

### 후보 JSON 필드
- `id`: 동일한 근거와 문장에는 동일한 식별자
- `ability`: 자기조절력 / 대인관계력 / 자기동기력
- `date`: 리추얼 날짜
- `paragraph`: 입력된 행동만으로 작성한 문장
- `evidence`: CSV의 출처, 행동, 평가
- `approval_status`: 무조건 `pending` (승인 대기)

**중요:** `Artifacts`의 후보 ZIP은 검토용입니다. 승인 버튼이나 게시 기능은 4단계 이후에 추가합니다. GitHub Actions 아티팩트는 저장소 접근 권한이 있는 사람에게 노출될 수 있으므로, 민감한 내용은 CSV에 넣지 마세요. 기존 공개 원본 리추얼 자료는 별도 보호 조치가 필요합니다.

로컬 Python이 있는 다른 컴퓨터에서는 다음을 실행할 수 있습니다.
```bash
python updater/generate_candidates.py
python updater/test_candidates.py
```


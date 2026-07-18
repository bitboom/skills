<!-- Slide number: 1 -->
검증은 증거를 판정하고, 공개는 정책이 결정한다
01
유효한 Quote는 자동 권한 부여가 아니다. signed Result는 RP/KMS release policy의 입력이다.

COLLATERAL SIDE PATH
Intel PCS → PCCS cache → signed collateral → Verifier

02
03

01
ALLOW
VERIFIER
RP / KMS
EVIDENCE

one-time
secret
Quote + context
signed Result
Quote·collateral 평가
K / D / E 재계산
signed Result 생성
Result + time + E/K 확인
PoP 확인
별도 release policy
TD Quote + canonical key bytes + bound request context

NO KEY
deny · replay
· expiry

K/D/E: symbolic profile
deployment은 별도 trust anchor·조직 policy를 명시해야 한다.

이 경로가 증명하는 것
이 경로만으로는 증명하지 않는 것
reported TD state + request/key binding을 조직 policy로 평가할 수 있다.
code correctness · container identity · future safety · availability

Intel-rats: learning / design-review only · not a production verifier baseline.
Sources: S-002 RFC 9334 · S-003 Intel DCAP

### Notes:

<!-- Slide number: 2 -->
signed Result는 어떻게 만들어지는가
02
QGS는 transport이고 TDQE는 Quote signer다. 한 message는 한 arrow에만 둔다. K/D/E는 symbolic deployment profile이다.

RP / KMS
Verifier
TD
QGS
TDQE
release owner
appraisal owner
attester
transport only
Quote signer

01  Bind
request ID + subject + audience

nonce (Verifier retains context)

RP forwards nonce + bound request context

02  Quote
TDREPORT: D/K

same-platform report

TDQE-signed Quote

Quote returns through guest path

exact Quote + canonical key bytes

Evidence + key + identical context
03  Appraise

signed Result: verdict + policy version + E + allow-only K

PoP challenge / response

after ALLOW: secret only on same approved K channel

Summary sequence: request binding → TD/QGS/TDQE Quote path → appraisal Result → RP/KMS policy.
Sources: S-002 RFC 9334 · S-003 Intel DCAP

### Notes:
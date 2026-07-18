<!-- Slide number: 1 -->
검증은 증거를 판정하고, 공개는 정책이 결정한다
유효한 Quote는 자동 권한 부여가 아니다. signed Result는 RP/KMS release policy의 입력이다.

Intel PCS  →  PCCS cache  →  signed collateral

PCCS는 authority가 아니라 cache / transport

02
03
01

VERIFIER
RP / KMS
ALLOW
EVIDENCE
one-time secret
Quote·collateral 평가
K / D / E 재계산
signed Result 생성
Result + time + E/K 확인
PoP 확인
별도 release policy

Quote + context
signed Result
TD Quote + canonical key bytes + bound request context

NO KEY
deny · replay · expiry

이 경로가 증명하는 것
이 경로만으로는 증명하지 않는 것
reported TD state + request/key binding을
조직 policy로 평가할 수 있다.
code correctness · container identity · future safety · availability
Sources: RFC 9334; Intel SGX Data Center Attestation Primitives.  Decision model from passed Intel-rats Point.
Intel-rats는 교육용 lens이며 배포형 Quote verifier가 아니다.

### Notes:

<!-- Slide number: 2 -->
signed Result는 어떻게 만들어지는가
actor는 한 번만 놓고, 각 화살표에는 하나의 artifact/message만 둔다.

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

Collateral side path: Intel PCS → PCCS → Verifier validates signature / status / freshness
03  Appraise
signed Result: verdict + policy version + E + allow-only K

PoP challenge / response → secret only on same approved K channel
DENY / REPLAY / EXPIRY → NO KEY

Main sequence: passed Intel-rats Point C-004/C-005/C-006.  PCCS is a collateral cache, not the signing authority.
Intel-rats는 교육용 lens이며 배포형 Quote verifier가 아니다.

### Notes:
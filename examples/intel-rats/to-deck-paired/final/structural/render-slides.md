<!-- Slide number: 1 -->
Intel TDX 원격 증명은 release-control system이다
01
하드웨어 Evidence appraisal과 secret release를 하나로 합치지 않고, 서로 다른 책임으로 연결한다.

POINT THESIS · C-001
선택한 trust anchor와 조직 policy가 유효하다는 가정 아래, Verifier는 Evidence를 평가하고 RP/KMS는 별도 policy로 비밀 공개를 결정한다.

A
B
C
ALLOW
Attester
Verifier
RP / KMS

one-time secret release
TD가 report와 bound context를 만든다.
QGS와 TDQE는 서로 다른 역할이다.
Quote·collateral·context를 검증하고 appraisal Result를 signed 한다.
Result를 policy 입력으로 사용한다.
Release와 deny 책임은 여기 있다.

NO KEY
deny · replay · expiry
교육 / design-review lens: Intel-rats는 deployable verifier baseline이 아니다.

C-001 · C-004 · B-004/B-006. Structural overview; detailed evidence/result paths follow.
Sources: S-002 RFC 9334 · S-003 Intel DCAP

### Notes:

<!-- Slide number: 2 -->
같은 경로에 있어도, 같은 trust role은 아니다
02
구조적 deck은 actor·authority·cache·decision owner를 분리해 읽게 한다.

TD / QGS / TDQE
PCS / PCCS
Verifier → RP/KMS

report와 bound key context
signed collateral authority
Evidence appraisal + signed Result
TD
PCS
Verifier

Quote transport / coordination
cache / transport
Result-use policy + release
QGS
PCCS
RP / KMS

Quote signer
outage·revocation policy
Result는 action이 아니다
TDQE
Operations
Boundary
Required distinctions: QGS ≠ TDQE · PCS ≠ PCCS · Verifier ≠ RP/KMS · Evidence ≠ Result ≠ action.

C-005 and Point five-boundary inventory. Color supports labels; it does not encode meaning alone.
Sources: S-002 RFC 9334 · S-003 Intel DCAP

### Notes:

<!-- Slide number: 3 -->
Primary path: request binding부터 one-time release까지
03
각 단계는 다른 artifact와 owner를 갖는다. path가 닫혀야 policy action을 정당화할 수 있다.

01
02
03
04
05
06
Request
Context
Evidence
Appraisal
Result
Action
RP/KMS
subject · audience
Verifier nonce
retains request
TD Report / Quote
D/K binding
Verifier validates
Quote + collateral
signed verdict
E + policy version
RP/KMS policy
PoP → secret / no key

Closed-path invariant
Evidence must reach appraisal with the intended request/key context; the authenticated Result must reach the distinct policy owner before any release.

E-013
E-015
E-018
Evidence + key + context
signed Result
same approved K channel

C-004 · E-013/E-015/E-018 · B-004/B-006.
Sources: S-002 RFC 9334 · S-003 Intel DCAP

### Notes:

<!-- Slide number: 4 -->
Evidence는 Quote 하나가 아니라, 연결된 input set이다
04
선택한 attestation trust model과 appraisal policy 아래에서 Verifier는 Quote, collateral, canonical key bytes, bound request context를 같은 appraisal에 넣는다.

01
02
03
04
TDREPORT / Quote
Canonical key bytes
Request context
Signed collateral
reported TD state와 D/K bound context를 전달한다.
Result-use 단계에서 다시 확인할 key binding의 기준이다.
nonce · subject · audience를 통한 request binding의 기준이다.
authority bytes의 chain · status · freshness를 평가한다.

Verifier appraisal
각 input의 binding과 validity를 함께 판정

Proof limit: Quote validity만으로 result-use policy, one-time state, workload identity, runtime behavior를 대체하지 않는다.

C-004/C-007 · E-013 · B-004.
Sources: S-002 RFC 9334 · S-003 Intel DCAP

### Notes:

<!-- Slide number: 5 -->
Quote generation: TD, QGS, TDQE의 역할을 섞지 않는다
05
QGS는 guest-path transport/coordination이고 TDQE가 Quote를 sign한다. K/D/E는 이 Point의 symbolic deployment profile이다.

TD
QGS
TDQE
RP / KMS
Verifier
attester
transport only
Quote signer
request owner
appraisal owner

TDREPORT: D/K

same-platform report

TDQE-signed Quote

Quote returns through guest path

exact Quote + canonical key bytes

E-013: Evidence + key + bound request context

Anti-collapse rule
Binding rule
Reader check
QGS transport success는 Quote signing authority가 아니다.
RP/KMS가 bound package를 Verifier에 전달하고 retained context와 맞춘다.
누가 sign·transport하고, 어느 bytes를 평가하는가?

N-004/N-005/N-006/N-003 · C-004 · QGS/TDQE distinction.
Sources: S-002 RFC 9334 · S-003 Intel DCAP

### Notes:

<!-- Slide number: 6 -->
Collateral: PCS authority와 PCCS cache를 구별한다
06
Verifier가 신뢰하는 것은 cache의 availability가 아니라 received bytes의 cryptographic/status/freshness checks다.

01
02
03
Intel PCS
PCCS
Verifier
signed collateral bytes
cache-delivered bytes
signed collateral authority
issuer / signed data origin
cache / transport
availability와 authority를 분리
signature · chain
status · freshness 검증

Operating consequence
PCCS outage와 collateral/certificate revocation은 별도 운영 policy가 필요하다. PCCS availability는 attestation validity를 보장하지 않는다.

C-005 · N-008 · E-014. PCS ≠ PCCS.
Sources: S-002 RFC 9334 · S-003 Intel DCAP

### Notes:

<!-- Slide number: 7 -->
signed Result는 release의 증거 입력이지, release 그 자체가 아니다
07
Verifier의 appraisal과 RP/KMS의 policy decision은 authenticated boundary로 연결되지만 같은 책임이 아니다.

01
02
ALLOW
Verifier Result
RP / KMS checks
policy decision

verdict
policy version
Evidence identity E
allow-only canonical key K

Result는 verifier가 authenticated하게 전달한다.
Result authenticity
time and policy version
E/K binding
proof of possession
one-time atomic state
authenticated signed Result

NO KEY

deny · replay · expiry
PoP challenge / response

TD / K endpoint

E-018 secret on same approved K
attester receives secret only after ALLOW

Result verification cannot substitute for Result-use policy, state consumption, or secret delivery.
Boundary B-006

C-004 · E-015/E-018 · B-006. Verifier/RP distinction.
Sources: S-002 RFC 9334 · S-003 Intel DCAP

### Notes:

<!-- Slide number: 8 -->
Deployment obligations은 valid Quote가 자동으로 제공하지 않는다
08
보안·운영 요구는 Result-use path에 명시적으로 설계하고 검증해야 한다.

01
02
03
Freshness
Request binding
Public-key binding
Verifier / Operations
nonce, expiry, stale collateral 판단
RP/KMS + Verifier
subject · audience · request ownership
Verifier + RP/KMS
canonical K와 Evidence/Result의 일치

04
05
06
Proof of possession
Authenticated Result
One-time state
RP/KMS + TD endpoint
K를 실제로 제어하는 endpoint 확인
Verifier → RP/KMS
verdict가 policy owner까지 변조 없이 도달
RP/KMS
release decision·state consumption·secret delivery의 atomic terminal transition

Failure policy must explicitly cover: deny · replay · expiry · invalid collateral · failed PoP → NO KEY.

Point five-boundary inventory and C-004/C-007 proof limits.
Sources: S-002 RFC 9334 · S-003 Intel DCAP

### Notes:

<!-- Slide number: 9 -->
Attestation result의 proof boundary를 명확히 읽는다
09
선택한 attestation trust model과 appraisal policy 아래에서 Quote와 Result는 유용한 Evidence를 제공하지만 workload의 모든 property를 자동 증명하지 않는다.

이 경로가 하는 일
이 경로만으로는 하지 않는 일

✓
×
reported TD state를 appraisal policy로 평가
code correctness / vulnerability absence

✓
×
배포가 request / audience / public-key binding을 명시적으로 설계·검증
TD 내부 container·process의 automatic identity

✓
×
signed Result를 distinct policy owner에게 전달
attestation 이후 future-safe behavior

✓
×
secret release를 explicit allow / no-key branch로 분리
availability 및 side-channel·I/O·physical·supply-chain risk 제거
설계 판단: workload identity와 runtime behavior에는 별도 Evidence / control을 추가한다.

C-007 and does_not_prove[0..3].
Sources: S-002 RFC 9334 · S-003 Intel DCAP

### Notes:

<!-- Slide number: 10 -->
Intel-rats는 learning lens이고, production baseline은 아니다
10
도메인 mental model과 design-review 질문에는 사용하되, implementation/security approval/runtime enforcement 근거로 단독 사용하지 않는다.

USE
DON’T
ASK
Teach & review
Do not treat as
Design review questions
remote-attestation decision system을 설명
trust role separation을 검토
request / result / policy binding 질문 생성
deployable Quote-verification implementation
security-approval baseline
runtime-enforcement proof
누가 Evidence를 평가하는가?
누가 release policy를 소유하는가?
어떤 binding/failure state가 explicit한가?

Executive action: policy ownership, collateral operations, key binding, replay/expiry handling을 release 전에 책임자로 확정한다.

Point use decision. Domain first; project assessment remains supporting.
Sources: S-002 RFC 9334 · S-003 Intel DCAP

### Notes:

<!-- Slide number: 11 -->
Appendix · Claim · model · source ledger
11
모든 material claim과 model element는 coverage map의 exact slide/object locator로 추적된다. 이 appendix는 Slide 10의 action 결론 뒤에 둔다.

Claim
Material meaning
Canonical source
Structural location

C-001
Evidence appraisal + separate release policy
S-002, S-003
Slides 1, 3, 7

C-004
Quote/collateral appraisal → signed Result → policy
S-002, S-003
Slides 5, 7, 8

C-005
PCS authority ≠ PCCS cache/transport
S-003
Slides 2, 6

C-007
Quote/Result proof limit and extra controls
S-002, S-003
Slides 4, 8, 9

Quick model locator · E-013: Slide 05 / st-e-013 · E-015: Slide 07 / st-e-015 · E-018: Slide 07 / TD endpoint · B-004: Slide 04 · B-006: Slide 07 · N-005/N-006: Slide 05.
Canonical locators: S-002 RFC 9334 §§2–4 · S-003 Intel DCAP QuoteGeneration / QuoteVerification / collateral workflow.

Coverage map is the authoritative object-level trace; this slide is the reader-facing ledger.
Sources: S-002 RFC 9334 · S-003 Intel DCAP

### Notes:
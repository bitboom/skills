<!-- Slide number: 1 -->
Intel TDX 원격 증명은 승인한 VM에만 비밀을 공개하는 통제다
01
클라우드 운영자를 전적으로 믿지 않아도, hardware Evidence와 조직 policy가 함께 secret release를 조건화한다.

문제
검사
결정
누구를 전적으로 믿지 않는가
Verifier가 Evidence를 평가한다
RP/KMS가 공개를 결정한다
host·hypervisor·network는 메시지를 지연·재전송·교체할 수 있다. 그래서 TD가 보낸 값은 검증 전까지 권한이 아니다.
Verifier는 Quote와 collateral, request context, key binding을 조직의 appraisal policy와 대조한다.
RP/KMS는 signed Result를 자신의 release policy에 넣고, 조건이 맞을 때만 비밀을 공개한다.

즉, Quote가 유효하다는 사실은 Verifier의 appraisal 결과일 뿐이다. 비밀을 공개할 권한은 Result를 검증한 RP/KMS의 별도 정책에서 나온다.
읽는 문장

C-001 · C-002 · C-003 · N-001/N-002/N-003/N-004
Source markers: 〔S-…〕 · Appendix 16

### Notes:

<!-- Slide number: 2 -->
같은 경로에 있어도 같은 trust role은 아니다
02
역할을 분리하면 “누가 무엇을 만들고, 누가 무엇을 믿으며, 누가 행동을 결정하는지”가 보인다.

TD
QGS daemon
TDQE
Verifier
TDX가 보호하는 VM
untrusted host transport
Quoting Enclave
증거 평가자
임시 키를 만들고 TDREPORT를 요청한다.
TDREPORT·Quote를 운반하지만 accepted Quote를 서명하지 못한다.
같은 플랫폼 TDREPORT를 확인하고 TD Quote에 서명한다.
nonce를 내부 보관하고 Evidence를 평가해 Result를 서명한다.

RP/KMS
Intel PCS
PCCS
공개 결정자
서명된 collateral의 권위 원천
collateral cache / transport
signed collateral

Result를 확인하고 release policy를 집행한다.
PCK·CRL·QE identity·TCB info의 signed origin이다.
PCS의 signed bytes를 운반하지만 자체 권위는 없다.

QGS가 Quote generation을 조율해도 signer는 TDQE다. PCS는 signed collateral의 권위 원천이고 PCCS는 cache/transport다. Verifier가 Result를 서명해도 secret을 공개하는 owner는 RP/KMS다.
구분 규칙

C-002 · N-002–N-008 · B-002/B-003/B-006 · 〔S-002,S-003,S-005〕
Source markers: 〔S-…〕 · Appendix 16

### Notes:

<!-- Slide number: 3 -->
공격 가능한 경로는 Evidence를 운반할 수 있어도 권한을 만들 수는 없다
03
host·network·QGS·PCCS·Attester input을 검증 전까지 신뢰하지 않는 위협 모델에서 시작한다.

공격자가 할 수 있는 일
신뢰하는 기반
보장하지 않는 것
drop · delay · replay · reorder · substitute · deny service
CPU/TDX Module·TDQE/PCK chain·PCS signatures·Verifier policy/key·RP/KMS policy/time·선택한 암호 구현·TD 안의 임시 private key custody
availability · code correctness · future behavior · 모든 side-channel · protected external I/O

untrusted path가 Quote를 재전송하거나 바꿔도 Verifier가 retained nonce·request·key binding을 다시 비교한다. 비교 실패, stale Evidence, 또는 검증 경로 장애에서는 secret release를 NO KEY로 종료한다. degraded mode가 필요하면 자산 공개가 없는 별도 정책을 미리 정한다.
경계의 의미

C-003 · B-001 · threat model · trusted crypto/key custody · 〔S-002,S-003,S-005,S-009〕
Source markers: 〔S-…〕 · Appendix 16

### Notes:

<!-- Slide number: 4 -->
nonce는 “이 Quote가 지금 이 요청을 위한 것인가”를 확인하는 일회용 기준이다
04
Verifier가 기대 문맥을 보관하고, RP/KMS가 그 문맥을 TD까지 전달해야 replay와 substitution을 거부할 수 있다.

RP/KMS
Verifier
TD

request ID · subject · audience

nonce

nonce + request context + digest-suite / key-binding request

Verifier 내부 one-time context
nonce · request ID · subject · audience · K/D suite

Verifier는 nonce와 full expected context를 내부 상태로 terminal event까지 보관한다. TD는 nonce·request ID·subject·audience·K를 D에 묶고, Verifier는 key bytes로 같은 D를 재계산한다. 재시도는 기존 record를 닫고 새 nonce로 시작한다.
읽는 문장

C-004 · E-003/E-004/E-005 · X-001/X-002/X-003 · retained state · 〔S-002,S-003,S-004〕
Source markers: 〔S-…〕 · Appendix 16

### Notes:

<!-- Slide number: 5 -->
QGS는 운반하고 TDQE가 서명한다
05
Quote generation path에서 transport 성공과 signing authority를 분리해야 host-side daemon을 과신하지 않는다.

B-002
untrusted QGS ↔ enclave signer

TD
QGS
TDQE
PCCS
TDREPORT: REPORTDATA에 D

same-platform TDREPORT + generation input

TDQE-signed TD Quote

Quote returns through guest path

cached collateral / quote configuration

TD는 TDREPORT를 QGS에 넘기지만, QGS가 받은 report에 신뢰를 더하지는 않는다. TDQE가 같은 platform report를 확인하고 Quote를 서명하며, Verifier는 나중에 그 Quote와 collateral을 별도로 검증한다.
읽는 문장

C-002/C-004 · E-006–E-011 · B-002 · N-004/N-005/N-006
Source markers: 〔S-…〕 · Appendix 16

### Notes:

<!-- Slide number: 6 -->
TDQE가 서명해 TD로 반환된 Quote와 key bytes는 RP/KMS를 거쳐 Verifier의 appraisal로 들어간다
06
이 transport route를 분명히 하면 QGS의 guest path와 Evidence delivery path를 혼동하지 않는다.

1
2
3
TD
RP/KMS
Verifier
E-012
E-013
exact TD Quote octets
canonical public-key bytes
request context
자신이 보낸 request와
받은 artifact를 묶어
Verifier에 전달
Quote·key·context를
retained nonce와 비교해
Evidence appraisal

TDQE가 TD Quote를 생성·서명해 QGS를 거쳐 TD로 돌려준다. TD는 canonical key bytes와 identical request context를 붙여 RP/KMS에 보내고, RP/KMS가 이를 Verifier에 전달한다. Verifier는 retained expected context와 비교해 Evidence가 이 request와 이 key를 위한 것인지 판단한다.
E-010→E-013

C-004 · E-010–E-013 · X-002/X-003/X-004 · B-004 · 〔S-002,S-003,S-004〕
Source markers: 〔S-…〕 · Appendix 16

### Notes:

<!-- Slide number: 7 -->
K, D, E는 “무엇을 확인했는가”를 세 종류의 bytes에 묶는다
07
아래 식은 symbolic invariant다. 배포 전에는 모든 byte-level choice를 profile로 고정해야 하며, 이 자체가 RFC wire format은 아니다.

K = Hash("tdx-ra/key/v1" || key_algorithm || canonical_key_bytes)

D = Hash("tdx-ra/context/v1" || canonical_encode(nonce, request_id, subject, audience, K))

E = Hash("tdx-ra/evidence/v1" || exact_TD_Quote_octets)

K
D
E
승인할 공개키의 digest
요청 문맥과 K의 digest
정확한 Quote 원문의 digest
protocol-canonical public-key bytes와 key algorithm을 묶어, 어느 키가 나중에 secret을 받을 수 있는지 정한다.
nonce·request ID·subject·audience·K를 묶어 fixed 64-byte REPORTDATA mapping에 넣는다.
Result가 어떤 transported Quote Evidence를 평가한 결과인지 RP/KMS가 확인하게 한다.

Verifier는 retained nonce와 받은 context·key bytes로 K와 D를 재계산해 REPORTDATA와 비교하고, exact Quote bytes로 E를 계산한다. 배포 profile은 hash/output length, 허용 key algorithm·canonical encoding, field order·length delimiting, domain tag/version, D의 64-byte REPORTDATA mapping을 확정해야 한다.
비교 규칙·한정자

C-006 · E-006/E-012/E-013/E-015 · X-003/X-004 · symbolic profile · 〔S-002,S-004,S-005,S-011〕
Source markers: 〔S-…〕 · Appendix 16

### Notes:

<!-- Slide number: 8 -->
Verifier Result는 평가의 서명된 기록이고, 비밀 공개 명령은 아니다
08
Result에는 profile·digest suite·평가 정책·E와 allow-only K가 들어가 RP/KMS가 무엇을 승인하는지 다시 확인할 수 있어야 한다.

Verifier가 확인
signed Result
RP/KMS가 확인
Quote와 collateral을 평가한다
어떤 정보가 넘어가는가
어떤 Result를 쓸 것인가
signature·chain·status·freshness, K/D/E, reference value와 appraisal policy를 확인한다. issued → allow_consumed | deny_consumed | expired 원자 전이가 성공한 뒤에만 terminal Result를 발행한다.
profile_version, digest_suite_id, verdict, issuer, subject, audience, request_id, issued_at, expiry, appraisal_policy_id/version, E를 서명하고 allow일 때만 K를 넣는다.
signature·authorized issuer·verdict·accepted profile/policy version·subject/audience/request·clock skew·E·allow-only K를 확인한다. 하나라도 다르면 release하지 않는다.

Verifier가 signed Result를 RP/KMS에 보낸다. RP/KMS가 Result signature·accepted profile/policy·time·E/K를 확인해도 그 자체는 secret release가 아니며, 다음 키 소유 증명(PoP)과 replay-state 전이가 별도로 성공해야 한다.
읽는 문장

C-004/C-006 · E-015 · B-005/B-006 · Result profile · 〔S-002,S-003,S-004,S-005〕
Source markers: 〔S-…〕 · Appendix 16

### Notes:

<!-- Slide number: 9 -->
비밀 공개는 키 소유 증명(PoP)과 일회용 state가 통과한 뒤 한 번만 수행한다
09
Result가 allow여도 RP/KMS는 approved K의 private key를 실제로 가진 TD인지 확인하고 replay를 막아야 한다.

1 · PoP
2 · state
3 · channel
RP/KMS가 challenge를 보낸다
한 요청을 원자적으로 소비한다
같은 approved K channel에만 보낸다
키 소유 증명(PoP)은 RP/KMS가 approved K에 대한 challenge를 TD에 보내고, TD가 임시 private key로 서명한 response를 돌려주는 검사다.
Result와 request가 unused일 때만 RP/KMS가 unused → release_committed로 전이한다. 이 전이에 이긴 요청만 release할 수 있다.
PoP와 atomic transition이 모두 성공한 allow path에서만 RP/KMS가 secret을 전달한다. Result 검증과 secret 전달은 서로 다른 행동이다.

ALLOW branch: Result/time/E/K + PoP + unused→release_committed 성공 → same approved-K channel → secret
NO KEY branch: deny | expiry | replay | invalid Result/collateral | failed PoP | terminal error

C-004/C-006 · E-016/E-017/E-018 · X-003 · B-006 · 〔S-002,S-003,S-004,S-005〕
Source markers: 〔S-…〕 · Appendix 16

### Notes:

<!-- Slide number: 10 -->
PCCS가 살아 있다는 사실이 collateral이 유효하다는 뜻은 아니다
10
PCS는 signed authority data의 원천이고 PCCS는 cache/transport이므로, Verifier는 받은 bytes 자체를 검증한다.

Intel PCS
PCCS
Verifier
서명된 authority data
cache / transport
received bytes를 검증
PCK Certificate, CRL, QE Identity, TCB Info의 signed origin이다.
cached signed bytes와 quote configuration을 전달한다. availability와 authority는 다른 성질이다.
signature·issuer chain·revocation status·expiry/freshness를 확인하고 그 결과를 Quote appraisal에 사용한다.

PCCS outage, nextUpdate 실패, revocation, TCB 변경은 운영 policy가 처리해야 한다. Verifier는 PCCS cache를 믿어서가 아니라 received collateral의 cryptographic validity와 freshness를 확인해서만 사용한다.
운영 결과

C-005 · E-008/E-009/E-014 · B-003 · N-007/N-008
Source markers: 〔S-…〕 · Appendix 16

### Notes:

<!-- Slide number: 11 -->
전체 Quote→Result 경로는 reported TD state를 확인하지만 workload의 모든 성질을 증명하지는 않는다
11
proof boundary를 분리해야 valid Quote와 signed Result를 code correctness나 container identity로 과대 해석하지 않는다.

이 경로로 알 수 있는 것
Quote만으로는 알 수 없는 것
Quote integrity와 accepted quoting credential 연결
code correctness 또는 vulnerability absence

reported TD measurement·attribute·TCB state
TD 안의 container/process 자동 identity

D가 retained context와 canonical key에 묶였는지
attestation 이후의 future-safe behavior

reference value와 비교 가능한지
retained·terminal challenge 없이 Evidence freshness

Result가 E·policy version·allow-only K를 가리키는지
별도 검사 없는 private-key possession·Result authenticity·최종 authorization

별도 Result·PoP·authorization 검사를 거친 release path
availability와 모든 side-channel·I/O·physical·supply-chain risk 제거

Quote/Result는 workload correctness·container identity를 증명하지 않는다. release 조건이면 workload Evidence와 runtime control을 추가하고, freshness·PoP·authorization은 각각 독립 검사한다.
설계 판단

C-007 · C-009 · B-007 · proves / does_not_prove · 〔S-002,S-003,S-009〕
Source markers: 〔S-…〕 · Appendix 16

### Notes:

<!-- Slide number: 12 -->
Intel-rats는 판단 구조를 배우는 학습 자료이지 운영 verifier 기준은 아니다
12
프로젝트는 도메인 판단 구조와 설계 검토 질문을 보이게 하지만 production implementation을 보증하지는 않는다.

취할 강점
RFC와 다른 부분
구현 한계
도메인 구조를 보이게 한다
표준 Background Check와 route가 다르다
운영 구현이 빠져 있다
TD·Guest Agent·Verifier·Key Broker·PCS/PCCS·policy owner를 하나의 release decision으로 연결해 design review 질문을 만든다.
RFC 9334 Background Check은 Attester→RP→Verifier다. Intel-rats는 Evidence 선등록 후 RP 조회를 쓰며 aggregate direct edge와 상세 Guest Agent route가 섞인다.
nonce·audience·expiry·workload Evidence가 first-class type이 아니고 concrete Quote/DCAP API/배포 코드/정책 언어가 없다. deny-without-key는 교육용 불변조건이지 runtime enforcement 보증이 아니다.

Intel-rats는 “누가 Evidence를 평가하고, 누가 release policy를 소유하며, 어떤 binding과 failure state가 explicit한가”를 묻는 학습 도구다. 실제 deployment는 RFC 흐름·구현 API·정책 언어·운영 enforcement를 별도로 확정해야 한다.
reader question

C-008 · caveats · project lens · 〔S-001,S-002,S-010〕
Source markers: 〔S-…〕 · Appendix 16

### Notes:

<!-- Slide number: 13 -->
TDX Quote를 container identity로 읽으면 증명 경계를 넘어선다
13
SGX와 TDX는 Evidence → appraisal → policy action 구조를 공유하지만, attested scope와 concrete mechanism은 다르다.

SGX
TDX
enclave identity 중심
whole Trust Domain / VM 경계 중심
SGX는 MRENCLAVE·MRSIGNER 같은 enclave identity를 중심으로 attestation을 읽는다. 그래도 code correctness나 future safety는 별도 문제다.
TDX Quote는 firmware·OS·workload를 포함할 수 있는 TD 전체 VM state를 보고한다. TD 안의 개별 container 신원은 자동으로 나오지 않는다.

컨테이너가 준 값을 REPORTDATA에 넣어도 컨테이너의 독립 identity가 증명되는 것은 아니다. protected identity가 container라면 workload-specific Evidence와 policy check를 별도로 설계한다.
scope limit

C-009 · C-007 · B-007 · SGX vs TDX
Source markers: 〔S-…〕 · Appendix 16

### Notes:

<!-- Slide number: 14 -->
첫 파일럿은 회수 가능한 단일 key-release path와 명확한 책임자에서 시작한다
14
출시 전에는 appraisal과 release의 책임자, collateral 운영, key binding, replay/expiry failure를 수치 기준으로 확정한다.

보안·플랫폼 책임자
보호 자산 서비스 책임자
reference values, TCB/freshness/binding appraisal policy, revocation/re-attestation 기준
Result-use/release policy, subject/audience/clock skew, fail-closed 운영 조건

플랫폼 운영
개발자·아키텍트
PCS/PCCS 갱신, collateral outage posture, revocation-to-deny SLO, audit/recovery
challenge state machine, K/D/E suite, Result/PoP, negative tests, key rotation
출시 gate: 단일 revocable key-release path는 다섯 조건이 모두 닫힌 뒤에만 연다.

① terminal 1회
② numeric SLO
③ policy audit
④ key rotation
⑤ 공개 key 0
allow·deny·expiry
요청은 한 번만 소비
outage·skew·revoke
re-attestation
version + approver
감사 가능
revoke·rollback
리허설
forged·replay·substitute
Verifier/PCCS failure

C-010 · N-001 · E-001/E-002 · developer/executive implications · 〔S-002,S-003,S-007,S-010,S-011〕
Source markers: 〔S-…〕 · Appendix 16

### Notes:

<!-- Slide number: 15 -->
Appendix: 10개 Point claim이 독자 문장과 어느 slide에서 만나는가
15
coverage는 ID footer가 아니라 실제 Korean assertion·narrative·proof limit으로 확인한다. 자세한 locator는 final/prose-trace.json과 structural-coverage-map.json에 남긴다.

Evidence 평가는 비밀 공개 권한이 아니다
K/D/E와 Result profile은 구현 전 version-fixed profile이 필요하다
slide 01
slide 07–09
C-001
C-006

보호·운반·서명·평가·공개는 다른 역할이다
Quote/Result는 security proof의 일부이지 모든 property의 증명은 아니다
slide 02, 05
slide 11
C-002
C-007

untrusted path는 권한을 만들 수 없고 NO KEY로 끝난다
Intel-rats는 학습 자료이며 운영 implementation 기준은 아니다
slide 03, 04
slide 12
C-003
C-008

request·Quote·Result·PoP·same-key release는 닫힌 경로다
TDX Quote는 TD/VM scope이지 container identity가 아니다
slide 04–09
slide 13
C-004
C-009

PCS authority와 PCCS cache는 다르다
단일 revocable pilot과 책임·SLO·negative gate가 먼저다
slide 10
slide 14
C-005
C-010

이 Appendix는 claim-level reader-visible trace다. model node/edge/boundary/context/state/proof/non-proof/implication/caveat/source marker의 exact location은 package JSON에서 재검증할 수 있다.
audit locator

C-001–C-010 · prose trace · complete structural coverage
Source markers: 〔S-…〕 · Appendix 16

### Notes:

<!-- Slide number: 16 -->
Appendix: canonical Point hash와 〔S-…〕 source marker를 독자에게 보이게 한다
16
slide footer의 〔S-…〕는 passed Point의 source_map stable reference다. 이 package에는 bibliography title registry가 없으므로, 존재하지 않는 서지를 추정해 쓰지 않는다.

Canonical Point  SHA-256  59bb8e0d71c321cc18cb4880e27dbbe7966511257a4d4c33e7e7a538fbc38891

C-001
S-002 · S-003 · S-007
C-006
S-002 · S-004 · S-005 · S-011

C-002
S-002 · S-003 · S-005 · S-007 · S-009
C-007
S-002 · S-003 · S-009

C-003
S-002 · S-003 · S-005 · S-009
C-008
S-001 · S-002 · S-010

C-004
S-002 · S-003 · S-004 · S-005 · S-006 · S-008 · S-010 · S-011
C-009
S-001 · S-002 · S-004 · S-010 · S-012

C-005
S-003 · S-005
C-010
S-002 · S-003 · S-007 · S-010 · S-011

근거를 다시 확인할 때는 source marker → claim → reader-visible slide 문장 → canonical Point를 역방향으로 추적한다. full source citation이 필요한 delivery에는 source registry를 canonical Point package에 추가한 뒤 deck을 재생성한다.
source audit rule

source_map · provenance · no invented bibliography
Source markers: 〔S-…〕 · Appendix 16

### Notes:
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
Sources: RFC 9334 · Intel DCAP / TDX documentation

### Notes:

<!-- Slide number: 2 -->
같은 경로에 있어도 같은 trust role은 아니다
02
역할을 분리하면 “누가 무엇을 만들고, 누가 무엇을 믿으며, 누가 행동을 결정하는지”가 보인다.

TD
QGS
TDQE
TDX가 보호하는 VM
host-side transport
Quoting Enclave
임시 키를 만들고 TDREPORT를 요청한다.
TDREPORT·Quote를 운반하지만 accepted Quote를 서명하지 못한다.
같은 플랫폼 TDREPORT를 확인하고 TD Quote에 서명한다.

Verifier
RP/KMS
PCS/PCCS
증거 평가자
공개 결정자
authority / cache
nonce를 보관하고 Evidence를 검증·평가해 Result를 서명한다.
Result를 확인하고 secret release policy를 집행한다.
PCS 서명은 검증하고 PCCS cache 자체는 권위로 믿지 않는다.

QGS가 Quote generation을 조율해도 signer는 TDQE다. Verifier가 Result를 서명해도 secret을 공개하는 owner는 RP/KMS다.
구분 규칙

C-002 · N-002–N-008 · B-002/B-003/B-006
Sources: RFC 9334 · Intel DCAP / TDX documentation

### Notes:

<!-- Slide number: 3 -->
공격 가능한 경로는 Evidence를 운반할 수 있어도 권한을 만들 수는 없다
03
host·network·QGS·PCCS·Attester input을 검증 전까지 신뢰하지 않는 위협 모델에서 시작한다.

공격자가 할 수 있는 일
신뢰하는 기반
보장하지 않는 것
drop · delay · replay · reorder · substitute · deny service
CPU/TDX Module · TDQE/PCK chain · PCS signatures · Verifier policy/key · RP/KMS policy/time
availability · code correctness · future behavior · 모든 side-channel · protected external I/O

untrusted path가 Quote를 재전송하거나 바꿔도, Verifier는 retained nonce·request·key binding을 다시 비교한다. 비교에 실패하거나 입력이 오래되면 policy는 fail closed 또는 명시된 제한 정책으로 처리한다.
경계의 의미

C-003 · B-001 · threat_model · availability limit
Sources: RFC 9334 · Intel DCAP / TDX documentation

### Notes:

<!-- Slide number: 4 -->
nonce는 “이 Quote가 지금 이 요청을 위한 것인가”를 확인하는 일회용 기준이다
04
Verifier가 기대 문맥을 보관하고, RP/KMS가 그 문맥을 TD까지 전달해야 replay와 substitution을 거부할 수 있다.

RP/KMS
Verifier
TD

request ID · subject · audience

nonce + retained expected context

nonce + request context + digest-suite request

Verifier가 nonce를 만들고 terminal state까지 보관한다. TD는 그 nonce와 request context를 D에 묶고, Verifier는 나중에 같은 값을 재계산해 이 Evidence가 다른 요청에서 온 것이 아닌지 확인한다.
읽는 문장

C-004 · E-003/E-004/E-005 · X-001/X-002 · request state
Sources: RFC 9334 · Intel DCAP / TDX documentation

### Notes:

<!-- Slide number: 5 -->
QGS는 운반하고 TDQE가 서명한다
05
Quote generation path에서 transport 성공과 signing authority를 분리해야 host-side daemon을 과신하지 않는다.

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
Sources: RFC 9334 · Intel DCAP / TDX documentation

### Notes:

<!-- Slide number: 6 -->
TD가 만든 Quote와 key bytes는 RP/KMS를 거쳐 Verifier의 appraisal로 들어간다
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

RP/KMS가 TD에서 받은 exact Quote, canonical key bytes, identical request context를 Verifier에 전달한다. Verifier는 보관한 expected context와 비교해 Evidence가 이 request와 이 key를 위한 것인지 판단한다.
E-012 → E-013

C-004 · E-012/E-013 · X-002/X-003/X-004 · B-004
Sources: RFC 9334 · Intel DCAP / TDX documentation

### Notes:

<!-- Slide number: 7 -->
K, D, E는 “무엇을 확인했는가”를 세 종류의 bytes에 묶는다
07
이 식은 RFC wire format이 아니라 deployment가 hash·encoding·field order를 확정해야 하는 symbolic profile이다.

K
D
E
canonical public-key bytes의 digest
nonce + request + subject + audience + K의 digest
exact TD Quote octets의 digest
어느 public key가 나중에 secret을 받을 수 있는지 묶는다.
TD가 REPORTDATA에 넣어 request context와 key를 TDREPORT에 묶는다.
Result가 어떤 Quote Evidence를 평가한 결과인지 RP/KMS가 확인하게 한다.

Verifier는 retained nonce와 받은 context·key bytes로 K와 D를 재계산해 REPORTDATA와 비교하고, exact Quote bytes로 E를 계산한다. 이 비교가 맞아야 Result의 verdict와 approved K가 같은 request/Evidence를 가리킨다.
비교 규칙

C-006 · E-006/E-012/E-013/E-015 · X-003/X-004 · symbolic profile
Sources: RFC 9334 · Intel DCAP / TDX documentation

### Notes:

<!-- Slide number: 8 -->
Verifier Result는 평가의 서명된 기록이고, 비밀 공개 명령은 아니다
08
Result에는 verdict뿐 아니라 request·policy version·E·allow-only K가 들어가 RP/KMS가 무엇을 승인하는지 다시 확인할 수 있어야 한다.

Verifier가 확인
signed Result
RP/KMS가 확인
Quote와 collateral을 평가한다
어떤 정보가 넘어가는가
어떤 Result를 쓸 것인가
Verifier는 signature·chain·status·freshness, K/D/E, reference value와 appraisal policy를 확인한다. terminal appraisal은 allow·deny·expiry 중 하나로 한 번만 소비된다.
verdict, issuer, subject, audience, request ID, issued_at/expiry, profile/policy version, E와 allow-only approved K를 signed 한다.
authorized issuer, verdict, policy version, subject/audience/request, clock skew, E, K를 확인한다. 하나라도 다르면 release하지 않는다.

Verifier가 signed Result를 RP/KMS에 보낸다. RP/KMS는 Result signature와 policy/time/E/K를 확인하지만, 그 확인 자체를 secret release로 취급하지 않고 다음 PoP·state transition 단계까지 진행한다.
읽는 문장

C-004/C-006 · E-015 · B-005/B-006 · Result profile
Sources: RFC 9334 · Intel DCAP / TDX documentation

### Notes:

<!-- Slide number: 9 -->
비밀 공개는 PoP와 일회용 state가 통과한 뒤 한 번만 수행한다
09
Result가 allow여도 RP/KMS는 approved K의 private key를 실제로 가진 TD인지 확인하고 replay를 막아야 한다.

1 · PoP
2 · state
3 · channel
RP/KMS가 challenge를 보낸다
한 요청을 원자적으로 소비한다
같은 approved K channel에만 보낸다
RP/KMS가 approved K에 대한 challenge를 TD에 보내고, TD는 임시 private key로 서명한 response를 돌려준다.
Result와 request가 unused일 때만 RP/KMS가 unused → release_committed로 전이한다. 이 전이에 이긴 요청만 release할 수 있다.
PoP와 atomic transition이 모두 성공한 allow path에서만 RP/KMS가 secret을 전달한다. 실패·replay·expiry는 NO KEY다.

RP/KMS가 Result를 확인한 뒤 TD와 PoP challenge/response를 교환한다. key possession과 one-time state transition이 모두 성공한 경우에만 RP/KMS가 E-018의 same approved K channel로 secret을 공개한다.
allow / no-key

C-004/C-006 · E-016/E-017/E-018 · X-003 · B-006
Sources: RFC 9334 · Intel DCAP / TDX documentation

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
Sources: RFC 9334 · Intel DCAP / TDX documentation

### Notes:

<!-- Slide number: 11 -->
Quote는 TD가 보고한 상태를 보여 주지만 workload의 모든 성질을 증명하지는 않는다
11
proof boundary를 분리해야 valid Quote를 code correctness나 container identity로 과대 해석하지 않는다.

이 경로로 알 수 있는 것
Quote만으로는 알 수 없는 것
Quote integrity와 accepted quoting credential 연결
code correctness 또는 vulnerability absence

reported TD measurement·attribute·TCB state
TD 안의 container/process 자동 identity

D가 retained context와 canonical key에 묶였는지
attestation 이후의 future-safe behavior

Result가 E·policy version·allow-only K를 가리키는지
availability와 모든 side-channel·I/O·physical·supply-chain risk 제거

Quote 검증은 workload correctness나 container identity를 증명하지 않는다. 그것이 release 조건이면 workload Evidence와 runtime control을 별도로 추가한다.
설계 판단

C-007 · C-009 · B-007 · proves / does_not_prove
Sources: RFC 9334 · Intel DCAP / TDX documentation

### Notes:

<!-- Slide number: 12 -->
Intel-rats는 판단 구조를 배우는 학습 자료이지 운영 verifier 기준은 아니다
12
프로젝트는 도메인 판단 구조와 설계 검토 질문을 보이게 하지만 production implementation을 보증하지는 않는다.

취할 강점
고쳐 읽을 부분
사용 결론
도메인 구조를 보이게 한다
표준 route와 다를 수 있다
학습과 설계 질문에는 사용한다
TD·Guest Agent·Verifier·Key Broker·PCS/PCCS·policy owner를 하나의 release decision으로 연결해 design review 질문을 만든다.
Background Check과 aggregate graph가 전달 패턴을 섞을 수 있다. nonce·audience·expiry·workload Evidence는 first-class type으로 보완해야 한다.
구현·security approval·runtime enforcement의 단독 근거로 쓰지 않는다. RFC 9334와 current Intel TDX/DCAP documentation으로 보완한다.

Intel-rats를 볼 때는 “누가 Evidence를 평가하고, 누가 release policy를 소유하며, 어떤 binding과 failure state가 explicit한가”를 질문한다. 답이 없는 부분은 실제 deployment 설계에서 추가해야 한다.
reader question

C-008 · caveats · project lens
Sources: RFC 9334 · Intel DCAP / TDX documentation

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
Sources: RFC 9334 · Intel DCAP / TDX documentation

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

첫 pilot은 가치가 높고 회수 가능한 단일 key-release path로 제한한다. forged Quote·nonce replay·key substitution·Verifier/PCCS failure에서 공개된 key는 0개여야 한다.
출시 gate

C-010 · N-001 · E-001/E-002 · developer/executive implications
Sources: RFC 9334 · Intel DCAP / TDX documentation

### Notes:

<!-- Slide number: 15 -->
Appendix: full Point claim · model · prose trace ledger
15
이 deck은 10 claims, 8 nodes, 18 edges, 7 boundaries와 context/state/proof/implication inventory를 canonical Point hash에 연결한다.

Point claim
Reader-visible meaning
Primary slide(s)

C-001
release-control thesis
01

C-002
actors / trust roles
02, 05, 10

C-003
threat and trust assumptions
03, 04

C-004
closed Background Check path
04–09

C-005
PCS/PCCS collateral path
10

C-006
K/D/E + Result profile
07–09

C-007
proof / non-proof boundary
11

C-008
Intel-rats strengths / corrections
12

C-009
SGX vs TDX scope
13

C-010
owners and pilot
14

Exact object-level location, qualifiers, proof limits, implications, sources, and all N/E/B/X IDs: final/structural-coverage-map.json + final/prose-trace.json

Canonical Point hash and complete coverage/prose trace.
Sources: RFC 9334 · Intel DCAP / TDX documentation

### Notes:
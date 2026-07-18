<!-- Slide number: 1 -->
유효한 Quote는 비밀 공개 권한이 아니다
01
TDQE가 서명한 Evidence를 Verifier가 평가하고, RP/KMS가 별도 공개 정책으로 마지막 행동을 결정한다.

1 · TD
2 · RP/KMS
3 · Verifier
TD는 Evidence를 준비한다
RP/KMS는 전달하고 결정한다
Verifier는 평가해 Result를 서명한다
TD는 임시 키와 요청 문맥의 D를 TDREPORT에 넣는다. QGS daemon은 운반하고 TDQE가 TD Quote를 생성·서명한다.
TD가 돌려준 Quote·key bytes·request를 Verifier에 보낸다. signed Result를 확인해도 아직 비밀을 바로 보내지 않는다.
Verifier는 Quote·collateral·K/D/E·보관 문맥을 평가하고 signed Result를 RP/KMS에 돌려준다.
Quote + key bytes + request
Evidence + K/D/E

Verifier-signed Result

Verifier가 Evidence를 평가해도 secret을 공개하지는 않는다. RP/KMS가 Result·시간·E/K·키 소유 증명을 다시 확인한 allow path에서만 같은 승인 키 channel로 secret을 전달한다.
읽는 문장

증명: reported TD state와 bound request/key를 policy로 평가할 수 있다.
비증명: code correctness · container identity · future safety · availability.

C-001 · C-004 · C-007 · E-012/E-013/E-015/E-018 · B-004/B-006 · 〔S-002,S-003〕
Source markers: 〔S-…〕 · Appendix 16

### Notes:

<!-- Slide number: 2 -->
비밀 공개는 여섯 단계가 모두 닫힐 때만 일어난다
02
처음 읽을 때는 K·D·E와 키 소유 증명(PoP)의 뜻을 먼저 잡고, request binding부터 same-key release까지 순서대로 읽는다.

K
승인할 공개키의 digest
D
요청 문맥과 K를 묶은 digest
E
정확한 Quote 원문의 digest
PoP
키 소유 증명(Proof of Possession)

01
02
03
04
05
06
요청 결합
D·TDREPORT
TDQE Quote
K/D/E 평가
signed Result
PoP → 공개
RP/KMS 요청
Verifier nonce 보관
TD가 D를
REPORTDATA에 묶음
QGS transport
TDQE가 서명
RP/KMS→Verifier
Evidence appraisal
verdict·E·K를
Verifier가 서명
키 소유 증명 뒤
same-K secret

allow + Result/time/E/K + PoP + unused→release_committed 성공 → same approved-K channel → secret
공개 branch

deny · expiry · replay · invalid Result/collateral · failed PoP · terminal error → NO KEY. 재시도는 기존 record를 닫고 새 nonce로 시작한다.
NO KEY branch

C-003/C-004/C-006 · E-003–E-018 · K/D/E/PoP local onboarding · 〔S-002,S-003〕
Source markers: 〔S-…〕 · Appendix 16

### Notes:
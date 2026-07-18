<!-- Slide number: 1 -->
유효한 Quote는 비밀 공개 권한이 아니다
01
원격 증명은 Evidence를 평가하는 사람과 비밀 공개를 결정하는 사람을 분리하는 release control이다.

1 · TD
2 · Verifier
3 · RP/KMS
TD가 무엇을 보낸다
Verifier가 무엇을 확인한다
RP/KMS가 공개를 결정한다
TD는 request context와 임시 키를 묶은 TDREPORT와 Quote를 만든다. QGS는 운반하고 TDQE가 Quote에 서명한다.
Verifier는 Quote·collateral·request·key를 함께 확인해 signed Result를 만든다. Result는 아직 공개 명령이 아니다.
RP/KMS는 Result·시간·E/K·key possession을 다시 확인하고, allow일 때만 같은 key channel에 secret을 보낸다.
Evidence + key + context
signed Result

Verifier가 Evidence를 평가해도 secret을 공개하지는 않는다. 공개 권한은 RP/KMS가 자신의 release policy로 Result를 확인한 뒤에만 행사한다.
읽는 문장

증명: reported TD state와 bound request/key를 policy로 평가할 수 있다.
비증명: code correctness · container identity · future safety · availability.

C-001 · C-004 · C-007 · B-004/B-006 · summary must-see
Sources: RFC 9334 · Intel DCAP / TDX documentation

### Notes:

<!-- Slide number: 2 -->
비밀은 “검증 성공” 뒤에도 두 번 더 확인한 뒤에만 공개된다
02
request binding → Quote → appraisal Result → PoP → same-key release의 순서를 한 개의 닫힌 path로 읽는다.

01
02
03
04
요청을 묶는다
Quote를 만든다
Evidence를 평가한다
Result를 사용한다
RP/KMS가 request ID·subject·audience를 보내고, Verifier는 nonce와 기대 문맥을 보관한다.
TD가 D를 REPORTDATA에 넣고, QGS가 TDREPORT를 TDQE로 운반해 signed Quote를 받는다.
RP/KMS가 Quote·key·동일 문맥을 Verifier에 보내면, Verifier가 K/D/E와 collateral을 확인한다.
RP/KMS가 signed Result·time·E/K·PoP를 확인한 뒤 allow일 때만 secret을 보낸다.

deny·replay·expiry·invalid collateral·failed PoP 중 하나라도 발생하면 RP/KMS는 NO KEY로 끝낸다. 재시도는 기존 상태를 재사용하지 않고 새 nonce로 시작한다.
실패 규칙

C-003/C-004/C-006 · E-003–E-018 · failure path
Sources: RFC 9334 · Intel DCAP / TDX documentation

### Notes:
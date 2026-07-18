import fs from 'node:fs';
import path from 'node:path';
import PptxGenJS from 'pptxgenjs';

const root = path.resolve('.');
const pointSha = fs.readFileSync(path.join(root, 'input/point.sha256'), 'utf8').trim().split(/\s+/)[0];
const S = new PptxGenJS().ShapeType;
const C = {
  ink: '081B2A', navy: '12334A', paper: 'F6F8FB', white: 'FFFFFF', text: '14273A', slate: '526B84', line: 'C9D6E3',
  teal: '0B7890', blue: '1C64D1', green: '14804A', red: 'B42318', amber: '9A6500', violet: '7044C8',
  paleBlue: 'E8F5FA', paleGreen: 'EAF7EF', paleRed: 'FFF0EF', paleAmber: 'FFF7E6', paleViolet: 'F3EEFF', paleSlate: 'EDF2F7',
};

function createDeck(title, subject) {
  const pptx = new PptxGenJS();
  pptx.defineLayout({ name: 'WIDE', width: 13.333, height: 7.5 });
  pptx.layout = 'WIDE';
  pptx.author = 'Bitboom';
  pptx.company = 'Bitboom';
  pptx.lang = 'ko-KR';
  pptx.title = title;
  pptx.subject = subject;
  pptx.theme = { headFontFace: 'Apple SD Gothic Neo', bodyFontFace: 'Apple SD Gothic Neo', lang: 'ko-KR' };
  pptx.margin = 0;
  return pptx;
}
function addText(slide, value, opts = {}) {
  slide.addText(value, { fontFace: 'Apple SD Gothic Neo', margin: 0, breakLine: false, fit: 'shrink', ...opts });
}
function rect(slide, x, y, w, h, fill, line = fill, radius = false) {
  slide.addShape(radius ? S.roundRect : S.rect, { x, y, w, h, fill: { color: fill }, line: { color: line, width: 0.7 } });
}
function arrow(slide, x1, y1, x2, y2, color = C.blue, width = 1.8, both = false) {
  slide.addShape(S.line, { x: x1, y: y1, w: x2 - x1, h: y2 - y1,
    line: { color, width, beginArrowType: both ? 'triangle' : 'none', endArrowType: 'triangle' } });
}
function divider(slide, y, dark = false) {
  slide.addShape(S.line, { x: 0.55, y, w: 12.23, h: 0, line: { color: dark ? '335168' : C.line, width: 0.5 } });
}
function header(slide, n, title, subtitle, dark = false) {
  addText(slide, title, { x: 0.55, y: 0.32, w: 11.5, h: 0.46, fontSize: 29, bold: true, color: dark ? C.white : C.text });
  addText(slide, subtitle, { x: 0.57, y: 0.91, w: 11.6, h: 0.3, fontSize: 14.3, color: dark ? 'B8CFE0' : C.slate });
  addText(slide, String(n).padStart(2, '0'), { x: 12.2, y: 0.42, w: 0.55, h: 0.18, fontSize: 10.5, bold: true, color: dark ? 'B8CFE0' : C.slate, align: 'right' });
}
function footer(slide, marker, dark = false) {
  divider(slide, 6.94, dark);
  addText(slide, marker, { x: 0.55, y: 7.08, w: 8.5, h: 0.14, fontSize: 7.8, color: dark ? 'B8CFE0' : C.slate });
  addText(slide, 'Sources: RFC 9334 · Intel DCAP / TDX documentation', { x: 8.25, y: 7.08, w: 4.5, h: 0.14, fontSize: 7.8, color: dark ? 'B8CFE0' : C.slate, align: 'right' });
}
function chip(slide, value, x, y, w, fill, color = C.white) {
  rect(slide, x, y, w, 0.28, fill, fill, true);
  addText(slide, value, { x, y: y + 0.075, w, h: 0.1, fontSize: 8.2, bold: true, color, align: 'center' });
}
function card(slide, { x, y, w, h, label, title, body, fill = C.white, color = C.text, accent = C.blue }) {
  rect(slide, x, y, w, h, fill, fill, true);
  if (label) chip(slide, label, x + 0.18, y + 0.18, Math.min(w - 0.36, 1.26), accent);
  const titleY = label ? y + 0.63 : y + 0.23;
  addText(slide, title, { x: x + 0.2, y: titleY, w: w - 0.4, h: 0.28, fontSize: 15.3, bold: true, color });
  addText(slide, body, { x: x + 0.2, y: titleY + 0.43, w: w - 0.4, h: Math.max(0.34, y + h - (titleY + 0.56)), fontSize: 12.3, color, valign: 'mid', breakLine: false });
}
function narrative(slide, sentence, opts = {}) {
  const { x = 0.72, y = 5.78, w = 11.85, h = 0.62, fill = C.paleBlue, color = C.text, tag = '읽는 문장', tagColor = C.teal } = opts;
  rect(slide, x, y, w, h, fill, fill, true);
  chip(slide, tag, x + 0.18, y + 0.18, 0.9, tagColor);
  addText(slide, sentence, { x: x + 1.28, y: y + 0.18, w: w - 1.48, h: h - 0.22, fontSize: 13.3, color, valign: 'mid' });
}
function bullet(slide, x, y, w, text, color = C.text, dot = C.teal, size = 13) {
  rect(slide, x, y + 0.08, 0.12, 0.12, dot, dot, true);
  addText(slide, text, { x: x + 0.28, y, w: w - 0.28, h: 0.25, fontSize: size, color });
}
function saveJson(file, value) {
  const full = path.join(root, file);
  fs.mkdirSync(path.dirname(full), { recursive: true });
  fs.writeFileSync(full, JSON.stringify(value, null, 2) + '\n');
}

function buildSummary() {
  const pptx = createDeck('Intel TDX 원격 증명 — Point prose summary', 'Two-slide Point-first explanation');
  {
    const s = pptx.addSlide(); s.background = { color: C.ink };
    header(s, 1, '유효한 Quote는 비밀 공개 권한이 아니다', '원격 증명은 Evidence를 평가하는 사람과 비밀 공개를 결정하는 사람을 분리하는 release control이다.', true);
    card(s, { x: 0.62, y: 1.75, w: 3.1, h: 2.95, label: '1 · TD', title: 'TD가 무엇을 보낸다', body: 'TD는 request context와 임시 키를 묶은 TDREPORT와 Quote를 만든다. QGS는 운반하고 TDQE가 Quote에 서명한다.', fill: C.navy, color: C.white, accent: C.teal });
    card(s, { x: 5.12, y: 1.75, w: 3.1, h: 2.95, label: '2 · Verifier', title: 'Verifier가 무엇을 확인한다', body: 'Verifier는 Quote·collateral·request·key를 함께 확인해 signed Result를 만든다. Result는 아직 공개 명령이 아니다.', fill: C.teal, color: C.white, accent: '086377' });
    card(s, { x: 9.62, y: 1.75, w: 3.1, h: 2.95, label: '3 · RP/KMS', title: 'RP/KMS가 공개를 결정한다', body: 'RP/KMS는 Result·시간·E/K·key possession을 다시 확인하고, allow일 때만 같은 key channel에 secret을 보낸다.', fill: C.blue, color: C.white, accent: '1650A8' });
    arrow(s, 3.75, 3.15, 5.08, 3.15, '98DDEA', 2.4);
    addText(s, 'Evidence + key + context', { x: 3.7, y: 2.83, w: 1.43, h: 0.15, fontSize: 9.3, bold: true, color: 'B8F0F5', align: 'center' });
    arrow(s, 8.25, 3.15, 9.58, 3.15, '9CC9FF', 2.4);
    addText(s, 'signed Result', { x: 8.35, y: 2.83, w: 1.12, h: 0.15, fontSize: 9.3, bold: true, color: 'C5E1FF', align: 'center' });
    narrative(s, 'Verifier가 Evidence를 평가해도 secret을 공개하지는 않는다. 공개 권한은 RP/KMS가 자신의 release policy로 Result를 확인한 뒤에만 행사한다.', { y: 5.15, fill: '103247', color: C.white, tagColor: C.green });
    rect(s, 0.72, 6.0, 5.65, 0.54, '14384D', '14384D', true);
    addText(s, '증명: reported TD state와 bound request/key를 policy로 평가할 수 있다.', { x: 0.95, y: 6.18, w: 5.2, h: 0.14, fontSize: 10.1, color: 'D9F0F6', bold: true });
    rect(s, 6.72, 6.0, 5.85, 0.54, '47222D', '47222D', true);
    addText(s, '비증명: code correctness · container identity · future safety · availability.', { x: 6.95, y: 6.18, w: 5.4, h: 0.14, fontSize: 10.1, color: 'FFE4E0', bold: true });
    footer(s, 'C-001 · C-004 · C-007 · B-004/B-006 · summary must-see', true);
  }
  {
    const s = pptx.addSlide(); s.background = { color: C.paper };
    header(s, 2, '비밀은 “검증 성공” 뒤에도 두 번 더 확인한 뒤에만 공개된다', 'request binding → Quote → appraisal Result → PoP → same-key release의 순서를 한 개의 닫힌 path로 읽는다.');
    const cols = [
      ['01', '요청을 묶는다', 'RP/KMS가 request ID·subject·audience를 보내고, Verifier는 nonce와 기대 문맥을 보관한다.', C.blue],
      ['02', 'Quote를 만든다', 'TD가 D를 REPORTDATA에 넣고, QGS가 TDREPORT를 TDQE로 운반해 signed Quote를 받는다.', C.teal],
      ['03', 'Evidence를 평가한다', 'RP/KMS가 Quote·key·동일 문맥을 Verifier에 보내면, Verifier가 K/D/E와 collateral을 확인한다.', C.violet],
      ['04', 'Result를 사용한다', 'RP/KMS가 signed Result·time·E/K·PoP를 확인한 뒤 allow일 때만 secret을 보낸다.', C.green],
    ];
    cols.forEach(([n, head, body, accent], i) => {
      const x = 0.58 + i * 3.16;
      card(s, { x, y: 1.75, w: 2.72, h: 3.75, label: n, title: head, body, fill: C.white, color: C.text, accent });
      if (i < cols.length - 1) arrow(s, x + 2.76, 3.55, x + 3.1, 3.55, accent, 1.8);
    });
    narrative(s, 'deny·replay·expiry·invalid collateral·failed PoP 중 하나라도 발생하면 RP/KMS는 NO KEY로 끝낸다. 재시도는 기존 상태를 재사용하지 않고 새 nonce로 시작한다.', { y: 5.92, fill: C.paleRed, color: C.red, tag: '실패 규칙', tagColor: C.red });
    footer(s, 'C-003/C-004/C-006 · E-003–E-018 · failure path');
  }
  return pptx;
}

function buildStructural() {
  const pptx = createDeck('Intel TDX 원격 증명 — full Point prose deck', 'Complete prose-preserving Point projection');
  // 1
  {
    const s = pptx.addSlide(); s.background = { color: C.ink };
    header(s, 1, 'Intel TDX 원격 증명은 승인한 VM에만 비밀을 공개하는 통제다', '클라우드 운영자를 전적으로 믿지 않아도, hardware Evidence와 조직 policy가 함께 secret release를 조건화한다.', true);
    card(s, { x: 0.65, y: 1.85, w: 3.25, h: 2.7, label: '문제', title: '누구를 전적으로 믿지 않는가', body: 'host·hypervisor·network는 메시지를 지연·재전송·교체할 수 있다. 그래서 TD가 보낸 값은 검증 전까지 권한이 아니다.', fill: C.navy, color: C.white, accent: C.red });
    card(s, { x: 5.04, y: 1.85, w: 3.25, h: 2.7, label: '검사', title: 'Verifier가 Evidence를 평가한다', body: 'Verifier는 Quote와 collateral, request context, key binding을 조직의 appraisal policy와 대조한다.', fill: C.teal, color: C.white, accent: '086377' });
    card(s, { x: 9.43, y: 1.85, w: 3.25, h: 2.7, label: '결정', title: 'RP/KMS가 공개를 결정한다', body: 'RP/KMS는 signed Result를 자신의 release policy에 넣고, 조건이 맞을 때만 비밀을 공개한다.', fill: C.blue, color: C.white, accent: '1650A8' });
    arrow(s, 3.93, 3.17, 5.0, 3.17, '98DDEA', 2.4); arrow(s, 8.32, 3.17, 9.39, 3.17, '9CC9FF', 2.4);
    narrative(s, '즉, Quote가 유효하다는 사실은 Verifier의 appraisal 결과일 뿐이다. 비밀을 공개할 권한은 Result를 검증한 RP/KMS의 별도 정책에서 나온다.', { y: 5.25, fill: '103247', color: C.white, tagColor: C.green });
    footer(s, 'C-001 · C-002 · C-003 · N-001/N-002/N-003/N-004');
  }
  // 2
  {
    const s = pptx.addSlide(); s.background = { color: C.paper };
    header(s, 2, '같은 경로에 있어도 같은 trust role은 아니다', '역할을 분리하면 “누가 무엇을 만들고, 누가 무엇을 믿으며, 누가 행동을 결정하는지”가 보인다.');
    const roles = [
      ['TD', 'TDX가 보호하는 VM', '임시 키를 만들고 TDREPORT를 요청한다.', C.teal],
      ['QGS', 'host-side transport', 'TDREPORT·Quote를 운반하지만 accepted Quote를 서명하지 못한다.', C.slate],
      ['TDQE', 'Quoting Enclave', '같은 플랫폼 TDREPORT를 확인하고 TD Quote에 서명한다.', C.violet],
      ['Verifier', '증거 평가자', 'nonce를 보관하고 Evidence를 검증·평가해 Result를 서명한다.', C.blue],
      ['RP/KMS', '공개 결정자', 'Result를 확인하고 secret release policy를 집행한다.', C.green],
      ['PCS/PCCS', 'authority / cache', 'PCS 서명은 검증하고 PCCS cache 자체는 권위로 믿지 않는다.', C.amber],
    ];
    roles.forEach(([name, title, body, accent], i) => {
      const x = 0.56 + (i % 3) * 4.16; const y = 1.6 + Math.floor(i / 3) * 2.28;
      card(s, { x, y, w: 3.72, h: 1.8, label: name, title, body, fill: C.white, color: C.text, accent });
    });
    narrative(s, 'QGS가 Quote generation을 조율해도 signer는 TDQE다. Verifier가 Result를 서명해도 secret을 공개하는 owner는 RP/KMS다.', { y: 6.05, fill: C.paleRed, color: C.red, tag: '구분 규칙', tagColor: C.red });
    footer(s, 'C-002 · N-002–N-008 · B-002/B-003/B-006');
  }
  // 3
  {
    const s = pptx.addSlide(); s.background = { color: C.paper };
    header(s, 3, '공격 가능한 경로는 Evidence를 운반할 수 있어도 권한을 만들 수는 없다', 'host·network·QGS·PCCS·Attester input을 검증 전까지 신뢰하지 않는 위협 모델에서 시작한다.');
    const items = [
      ['공격자가 할 수 있는 일', 'drop · delay · replay · reorder · substitute · deny service', C.paleRed, C.red],
      ['신뢰하는 기반', 'CPU/TDX Module · TDQE/PCK chain · PCS signatures · Verifier policy/key · RP/KMS policy/time', C.paleGreen, C.green],
      ['보장하지 않는 것', 'availability · code correctness · future behavior · 모든 side-channel · protected external I/O', C.paleAmber, C.amber],
    ];
    items.forEach(([head, body, fill, color], i) => card(s, { x: 0.72 + i * 4.16, y: 2.05, w: 3.72, h: 2.75, title: head, body, fill, color, accent: color }));
    narrative(s, 'untrusted path가 Quote를 재전송하거나 바꿔도, Verifier는 retained nonce·request·key binding을 다시 비교한다. 비교에 실패하거나 입력이 오래되면 policy는 fail closed 또는 명시된 제한 정책으로 처리한다.', { y: 5.55, fill: C.paleBlue, color: C.text, tag: '경계의 의미' });
    footer(s, 'C-003 · B-001 · threat_model · availability limit');
  }
  // 4
  {
    const s = pptx.addSlide(); s.background = { color: C.paper };
    header(s, 4, 'nonce는 “이 Quote가 지금 이 요청을 위한 것인가”를 확인하는 일회용 기준이다', 'Verifier가 기대 문맥을 보관하고, RP/KMS가 그 문맥을 TD까지 전달해야 replay와 substitution을 거부할 수 있다.');
    const lanes = [['RP/KMS', 0.7, C.blue], ['Verifier', 4.0, C.teal], ['TD', 7.3, C.violet]];
    lanes.forEach(([name, x, color]) => { rect(s, x, 1.65, 2.35, 0.58, color, color, true); addText(s, name, { x, y: 1.84, w: 2.35, h: 0.14, fontSize: 14.5, bold: true, color: C.white, align: 'center' }); s.addShape(S.line, { x: x + 1.175, y: 2.28, w: 0, h: 3.2, line: { color: C.line, width: 0.8, dash: 'dash' } }); });
    arrow(s, 1.88, 2.8, 5.17, 2.8, C.blue, 2); addText(s, 'request ID · subject · audience', { x: 2.35, y: 2.55, w: 2.3, h: 0.14, fontSize: 10.5, bold: true, color: C.blue, align: 'center' });
    arrow(s, 5.17, 3.55, 1.88, 3.55, C.teal, 2); addText(s, 'nonce + retained expected context', { x: 2.18, y: 3.3, w: 2.65, h: 0.14, fontSize: 10.5, bold: true, color: C.teal, align: 'center' });
    arrow(s, 1.88, 4.32, 8.47, 4.32, C.blue, 2); addText(s, 'nonce + request context + digest-suite request', { x: 3.12, y: 4.07, w: 4.1, h: 0.14, fontSize: 10.4, bold: true, color: C.blue, align: 'center' });
    narrative(s, 'Verifier가 nonce를 만들고 terminal state까지 보관한다. TD는 그 nonce와 request context를 D에 묶고, Verifier는 나중에 같은 값을 재계산해 이 Evidence가 다른 요청에서 온 것이 아닌지 확인한다.', { y: 5.72, fill: C.paleViolet, color: C.violet, tag: '읽는 문장', tagColor: C.violet });
    footer(s, 'C-004 · E-003/E-004/E-005 · X-001/X-002 · request state');
  }
  // 5
  {
    const s = pptx.addSlide(); s.background = { color: C.paper };
    header(s, 5, 'QGS는 운반하고 TDQE가 서명한다', 'Quote generation path에서 transport 성공과 signing authority를 분리해야 host-side daemon을 과신하지 않는다.');
    const lanes = [['TD', 0.65, C.teal], ['QGS', 3.4, C.slate], ['TDQE', 6.15, C.violet], ['PCCS', 8.9, C.amber]];
    lanes.forEach(([name, x, color]) => { rect(s, x, 1.5, 2.05, 0.58, color, color, true); addText(s, name, { x, y: 1.7, w: 2.05, h: 0.14, fontSize: 14, bold: true, color: C.white, align: 'center' }); s.addShape(S.line, { x: x + 1.02, y: 2.15, w: 0, h: 3.45, line: { color: C.line, width: 0.7, dash: 'dash' } }); });
    arrow(s, 1.68, 2.7, 4.43, 2.7, C.teal, 2); addText(s, 'TDREPORT: REPORTDATA에 D', { x: 1.88, y: 2.45, w: 2.35, h: 0.14, fontSize: 10.2, color: C.teal, bold: true, align: 'center' });
    arrow(s, 4.43, 3.35, 7.18, 3.35, C.slate, 2); addText(s, 'same-platform TDREPORT + generation input', { x: 4.62, y: 3.1, w: 2.38, h: 0.14, fontSize: 9.9, color: C.slate, bold: true, align: 'center' });
    arrow(s, 7.18, 4.0, 4.43, 4.0, C.violet, 2); addText(s, 'TDQE-signed TD Quote', { x: 4.72, y: 3.75, w: 2.05, h: 0.14, fontSize: 10.2, color: C.violet, bold: true, align: 'center' });
    arrow(s, 4.43, 4.65, 1.68, 4.65, C.slate, 2); addText(s, 'Quote returns through guest path', { x: 1.92, y: 4.4, w: 2.2, h: 0.14, fontSize: 10.0, color: C.slate, bold: true, align: 'center' });
    arrow(s, 9.92, 5.15, 4.43, 5.15, C.amber, 1.6); addText(s, 'cached collateral / quote configuration', { x: 5.25, y: 4.9, w: 3.8, h: 0.14, fontSize: 10, color: C.amber, bold: true, align: 'center' });
    narrative(s, 'TD는 TDREPORT를 QGS에 넘기지만, QGS가 받은 report에 신뢰를 더하지는 않는다. TDQE가 같은 platform report를 확인하고 Quote를 서명하며, Verifier는 나중에 그 Quote와 collateral을 별도로 검증한다.', { y: 5.86, fill: C.paleBlue, color: C.text });
    footer(s, 'C-002/C-004 · E-006–E-011 · B-002 · N-004/N-005/N-006');
  }
  // 6
  {
    const s = pptx.addSlide(); s.background = { color: C.paper };
    header(s, 6, 'TD가 만든 Quote와 key bytes는 RP/KMS를 거쳐 Verifier의 appraisal로 들어간다', '이 transport route를 분명히 하면 QGS의 guest path와 Evidence delivery path를 혼동하지 않는다.');
    const parts = [
      ['TD', 'exact TD Quote octets\ncanonical public-key bytes\nrequest context', C.teal],
      ['RP/KMS', '자신이 보낸 request와\n받은 artifact를 묶어\nVerifier에 전달', C.blue],
      ['Verifier', 'Quote·key·context를\nretained nonce와 비교해\nEvidence appraisal', C.violet],
    ];
    parts.forEach(([head, body, color], i) => card(s, { x: 0.78 + i * 4.15, y: 2.0, w: 3.42, h: 2.75, label: String(i + 1), title: head, body, fill: C.white, color, accent: color }));
    arrow(s, 4.22, 3.4, 4.88, 3.4, C.teal, 2.5); arrow(s, 8.37, 3.4, 9.03, 3.4, C.blue, 2.5);
    addText(s, 'E-012', { x: 4.28, y: 3.05, w: 0.5, h: 0.12, fontSize: 9.2, bold: true, color: C.teal });
    addText(s, 'E-013', { x: 8.43, y: 3.05, w: 0.5, h: 0.12, fontSize: 9.2, bold: true, color: C.blue });
    narrative(s, 'RP/KMS가 TD에서 받은 exact Quote, canonical key bytes, identical request context를 Verifier에 전달한다. Verifier는 보관한 expected context와 비교해 Evidence가 이 request와 이 key를 위한 것인지 판단한다.', { y: 5.6, fill: C.paleGreen, color: C.text, tag: 'E-012 → E-013', tagColor: C.green });
    footer(s, 'C-004 · E-012/E-013 · X-002/X-003/X-004 · B-004');
  }
  // 7
  {
    const s = pptx.addSlide(); s.background = { color: C.paper };
    header(s, 7, 'K, D, E는 “무엇을 확인했는가”를 세 종류의 bytes에 묶는다', '이 식은 RFC wire format이 아니라 deployment가 hash·encoding·field order를 확정해야 하는 symbolic profile이다.');
    const formulas = [
      ['K', 'canonical public-key bytes의 digest', '어느 public key가 나중에 secret을 받을 수 있는지 묶는다.', C.green],
      ['D', 'nonce + request + subject + audience + K의 digest', 'TD가 REPORTDATA에 넣어 request context와 key를 TDREPORT에 묶는다.', C.violet],
      ['E', 'exact TD Quote octets의 digest', 'Result가 어떤 Quote Evidence를 평가한 결과인지 RP/KMS가 확인하게 한다.', C.teal],
    ];
    formulas.forEach(([name, expr, body, color], i) => card(s, { x: 0.63 + i * 4.15, y: 1.85, w: 3.7, h: 3.45, label: name, title: expr, body, fill: i === 0 ? C.paleGreen : i === 1 ? C.paleViolet : C.paleBlue, color, accent: color }));
    narrative(s, 'Verifier는 retained nonce와 받은 context·key bytes로 K와 D를 재계산해 REPORTDATA와 비교하고, exact Quote bytes로 E를 계산한다. 이 비교가 맞아야 Result의 verdict와 approved K가 같은 request/Evidence를 가리킨다.', { y: 5.82, fill: C.paleAmber, color: C.text, tag: '비교 규칙', tagColor: C.amber });
    footer(s, 'C-006 · E-006/E-012/E-013/E-015 · X-003/X-004 · symbolic profile');
  }
  // 8
  {
    const s = pptx.addSlide(); s.background = { color: C.ink };
    header(s, 8, 'Verifier Result는 평가의 서명된 기록이고, 비밀 공개 명령은 아니다', 'Result에는 verdict뿐 아니라 request·policy version·E·allow-only K가 들어가 RP/KMS가 무엇을 승인하는지 다시 확인할 수 있어야 한다.', true);
    card(s, { x: 0.72, y: 1.9, w: 3.45, h: 3.5, label: 'Verifier가 확인', title: 'Quote와 collateral을 평가한다', body: 'Verifier는 signature·chain·status·freshness, K/D/E, reference value와 appraisal policy를 확인한다. terminal appraisal은 allow·deny·expiry 중 하나로 한 번만 소비된다.', fill: C.teal, color: C.white, accent: '086377' });
    card(s, { x: 4.95, y: 1.9, w: 3.45, h: 3.5, label: 'signed Result', title: '어떤 정보가 넘어가는가', body: 'verdict, issuer, subject, audience, request ID, issued_at/expiry, profile/policy version, E와 allow-only approved K를 signed 한다.', fill: C.violet, color: C.white, accent: '5630A7' });
    card(s, { x: 9.18, y: 1.9, w: 3.45, h: 3.5, label: 'RP/KMS가 확인', title: '어떤 Result를 쓸 것인가', body: 'authorized issuer, verdict, policy version, subject/audience/request, clock skew, E, K를 확인한다. 하나라도 다르면 release하지 않는다.', fill: C.blue, color: C.white, accent: '1650A8' });
    arrow(s, 4.2, 3.55, 4.9, 3.55, '9ADDE8', 2.3); arrow(s, 8.43, 3.55, 9.13, 3.55, 'BFA6FF', 2.3);
    narrative(s, 'Verifier가 signed Result를 RP/KMS에 보낸다. RP/KMS는 Result signature와 policy/time/E/K를 확인하지만, 그 확인 자체를 secret release로 취급하지 않고 다음 PoP·state transition 단계까지 진행한다.', { y: 5.85, fill: '103247', color: C.white, tagColor: C.green });
    footer(s, 'C-004/C-006 · E-015 · B-005/B-006 · Result profile');
  }
  // 9
  {
    const s = pptx.addSlide(); s.background = { color: C.paper };
    header(s, 9, '비밀 공개는 PoP와 일회용 state가 통과한 뒤 한 번만 수행한다', 'Result가 allow여도 RP/KMS는 approved K의 private key를 실제로 가진 TD인지 확인하고 replay를 막아야 한다.');
    card(s, { x: 0.7, y: 1.95, w: 3.35, h: 3.3, label: '1 · PoP', title: 'RP/KMS가 challenge를 보낸다', body: 'RP/KMS가 approved K에 대한 challenge를 TD에 보내고, TD는 임시 private key로 서명한 response를 돌려준다.', fill: C.paleViolet, color: C.violet, accent: C.violet });
    card(s, { x: 4.98, y: 1.95, w: 3.35, h: 3.3, label: '2 · state', title: '한 요청을 원자적으로 소비한다', body: 'Result와 request가 unused일 때만 RP/KMS가 unused → release_committed로 전이한다. 이 전이에 이긴 요청만 release할 수 있다.', fill: C.paleBlue, color: C.blue, accent: C.blue });
    card(s, { x: 9.26, y: 1.95, w: 3.35, h: 3.3, label: '3 · channel', title: '같은 approved K channel에만 보낸다', body: 'PoP와 atomic transition이 모두 성공한 allow path에서만 RP/KMS가 secret을 전달한다. 실패·replay·expiry는 NO KEY다.', fill: C.paleGreen, color: C.green, accent: C.green });
    arrow(s, 4.08, 3.55, 4.93, 3.55, C.violet, 2.3); arrow(s, 8.36, 3.55, 9.21, 3.55, C.green, 2.3);
    narrative(s, 'RP/KMS가 Result를 확인한 뒤 TD와 PoP challenge/response를 교환한다. key possession과 one-time state transition이 모두 성공한 경우에만 RP/KMS가 E-018의 same approved K channel로 secret을 공개한다.', { y: 5.78, fill: C.paleRed, color: C.red, tag: 'allow / no-key', tagColor: C.red });
    footer(s, 'C-004/C-006 · E-016/E-017/E-018 · X-003 · B-006');
  }
  // 10
  {
    const s = pptx.addSlide(); s.background = { color: C.paper };
    header(s, 10, 'PCCS가 살아 있다는 사실이 collateral이 유효하다는 뜻은 아니다', 'PCS는 signed authority data의 원천이고 PCCS는 cache/transport이므로, Verifier는 받은 bytes 자체를 검증한다.');
    card(s, { x: 0.75, y: 2.0, w: 3.45, h: 2.8, label: 'Intel PCS', title: '서명된 authority data', body: 'PCK Certificate, CRL, QE Identity, TCB Info의 signed origin이다.', fill: C.paleAmber, color: C.amber, accent: C.amber });
    card(s, { x: 4.94, y: 2.0, w: 3.45, h: 2.8, label: 'PCCS', title: 'cache / transport', body: 'cached signed bytes와 quote configuration을 전달한다. availability와 authority는 다른 성질이다.', fill: C.paleSlate, color: C.slate, accent: C.slate });
    card(s, { x: 9.13, y: 2.0, w: 3.45, h: 2.8, label: 'Verifier', title: 'received bytes를 검증', body: 'signature·issuer chain·revocation status·expiry/freshness를 확인하고 그 결과를 Quote appraisal에 사용한다.', fill: C.paleBlue, color: C.teal, accent: C.teal });
    arrow(s, 4.22, 3.4, 4.9, 3.4, C.amber, 2.3); arrow(s, 8.41, 3.4, 9.09, 3.4, C.teal, 2.3);
    narrative(s, 'PCCS outage, nextUpdate 실패, revocation, TCB 변경은 운영 policy가 처리해야 한다. Verifier는 PCCS cache를 믿어서가 아니라 received collateral의 cryptographic validity와 freshness를 확인해서만 사용한다.', { y: 5.65, fill: C.paleRed, color: C.red, tag: '운영 결과', tagColor: C.red });
    footer(s, 'C-005 · E-008/E-009/E-014 · B-003 · N-007/N-008');
  }
  // 11
  {
    const s = pptx.addSlide(); s.background = { color: C.paper };
    header(s, 11, 'Quote는 TD가 보고한 상태를 보여 주지만 workload의 모든 성질을 증명하지는 않는다', 'proof boundary를 분리해야 valid Quote를 code correctness나 container identity로 과대 해석하지 않는다.');
    rect(s, 0.68, 1.65, 5.78, 4.7, C.paleGreen, C.paleGreen, true);
    addText(s, '이 경로로 알 수 있는 것', { x: 0.98, y: 1.98, w: 4.9, h: 0.25, fontSize: 20, bold: true, color: C.green });
    ['Quote integrity와 accepted quoting credential 연결', 'reported TD measurement·attribute·TCB state', 'D가 retained context와 canonical key에 묶였는지', 'Result가 E·policy version·allow-only K를 가리키는지'].forEach((t, i) => bullet(s, 1.0, 2.65 + i * 0.68, 4.85, t, C.text, C.green, 12.6));
    rect(s, 6.86, 1.65, 5.78, 4.7, C.paleRed, C.paleRed, true);
    addText(s, 'Quote만으로는 알 수 없는 것', { x: 7.16, y: 1.98, w: 4.95, h: 0.25, fontSize: 20, bold: true, color: C.red });
    ['code correctness 또는 vulnerability absence', 'TD 안의 container/process 자동 identity', 'attestation 이후의 future-safe behavior', 'availability와 모든 side-channel·I/O·physical·supply-chain risk 제거'].forEach((t, i) => bullet(s, 7.18, 2.65 + i * 0.68, 4.9, t, C.text, C.red, 12.3));
    narrative(s, 'Quote 검증은 workload correctness나 container identity를 증명하지 않는다. 그것이 release 조건이면 workload Evidence와 runtime control을 별도로 추가한다.', { y: 6.35, h: 0.48, fill: C.paleAmber, color: C.text, tag: '설계 판단', tagColor: C.amber });
    footer(s, 'C-007 · C-009 · B-007 · proves / does_not_prove');
  }
  // 12
  {
    const s = pptx.addSlide(); s.background = { color: C.ink };
    header(s, 12, 'Intel-rats는 판단 구조를 배우는 학습 자료이지 운영 verifier 기준은 아니다', '프로젝트는 도메인 판단 구조와 설계 검토 질문을 보이게 하지만 production implementation을 보증하지는 않는다.', true);
    card(s, { x: 0.7, y: 1.92, w: 3.65, h: 3.35, label: '취할 강점', title: '도메인 구조를 보이게 한다', body: 'TD·Guest Agent·Verifier·Key Broker·PCS/PCCS·policy owner를 하나의 release decision으로 연결해 design review 질문을 만든다.', fill: C.navy, color: C.white, accent: C.teal });
    card(s, { x: 4.84, y: 1.92, w: 3.65, h: 3.35, label: '고쳐 읽을 부분', title: '표준 route와 다를 수 있다', body: 'Background Check과 aggregate graph가 전달 패턴을 섞을 수 있다. nonce·audience·expiry·workload Evidence는 first-class type으로 보완해야 한다.', fill: '3B1F2A', color: C.white, accent: C.red });
    card(s, { x: 8.98, y: 1.92, w: 3.65, h: 3.35, label: '사용 결론', title: '학습과 설계 질문에는 사용한다', body: '구현·security approval·runtime enforcement의 단독 근거로 쓰지 않는다. RFC 9334와 current Intel TDX/DCAP documentation으로 보완한다.', fill: C.blue, color: C.white, accent: '1650A8' });
    narrative(s, 'Intel-rats를 볼 때는 “누가 Evidence를 평가하고, 누가 release policy를 소유하며, 어떤 binding과 failure state가 explicit한가”를 질문한다. 답이 없는 부분은 실제 deployment 설계에서 추가해야 한다.', { y: 5.76, fill: '103247', color: C.white, tag: 'reader question', tagColor: C.green });
    footer(s, 'C-008 · caveats · project lens', true);
  }
  // 13
  {
    const s = pptx.addSlide(); s.background = { color: C.paper };
    header(s, 13, 'TDX Quote를 container identity로 읽으면 증명 경계를 넘어선다', 'SGX와 TDX는 Evidence → appraisal → policy action 구조를 공유하지만, attested scope와 concrete mechanism은 다르다.');
    card(s, { x: 0.8, y: 1.9, w: 5.5, h: 3.5, label: 'SGX', title: 'enclave identity 중심', body: 'SGX는 MRENCLAVE·MRSIGNER 같은 enclave identity를 중심으로 attestation을 읽는다. 그래도 code correctness나 future safety는 별도 문제다.', fill: C.paleViolet, color: C.violet, accent: C.violet });
    card(s, { x: 7.02, y: 1.9, w: 5.5, h: 3.5, label: 'TDX', title: 'whole Trust Domain / VM 경계 중심', body: 'TDX Quote는 firmware·OS·workload를 포함할 수 있는 TD 전체 VM state를 보고한다. TD 안의 개별 container 신원은 자동으로 나오지 않는다.', fill: C.paleBlue, color: C.teal, accent: C.teal });
    narrative(s, '컨테이너가 준 값을 REPORTDATA에 넣어도 컨테이너의 독립 identity가 증명되는 것은 아니다. protected identity가 container라면 workload-specific Evidence와 policy check를 별도로 설계한다.', { y: 5.8, fill: C.paleRed, color: C.red, tag: 'scope limit', tagColor: C.red });
    footer(s, 'C-009 · C-007 · B-007 · SGX vs TDX');
  }
  // 14
  {
    const s = pptx.addSlide(); s.background = { color: C.paper };
    header(s, 14, '첫 파일럿은 회수 가능한 단일 key-release path와 명확한 책임자에서 시작한다', '출시 전에는 appraisal과 release의 책임자, collateral 운영, key binding, replay/expiry failure를 수치 기준으로 확정한다.');
    const owners = [
      ['보안·플랫폼 책임자', 'reference values, TCB/freshness/binding appraisal policy, revocation/re-attestation 기준', C.teal],
      ['보호 자산 서비스 책임자', 'Result-use/release policy, subject/audience/clock skew, fail-closed 운영 조건', C.blue],
      ['플랫폼 운영', 'PCS/PCCS 갱신, collateral outage posture, revocation-to-deny SLO, audit/recovery', C.amber],
      ['개발자·아키텍트', 'challenge state machine, K/D/E suite, Result/PoP, negative tests, key rotation', C.violet],
    ];
    owners.forEach(([head, body, accent], i) => { const x = 0.62 + (i % 2) * 6.15; const y = 1.62 + Math.floor(i / 2) * 2.06; card(s, { x, y, w: 5.85, h: 1.62, title: head, body, fill: C.white, color: C.text, accent }); });
    narrative(s, '첫 pilot은 가치가 높고 회수 가능한 단일 key-release path로 제한한다. forged Quote·nonce replay·key substitution·Verifier/PCCS failure에서 공개된 key는 0개여야 한다.', { y: 5.92, fill: C.paleGreen, color: C.green, tag: '출시 gate', tagColor: C.green });
    footer(s, 'C-010 · N-001 · E-001/E-002 · developer/executive implications');
  }
  // 15
  {
    const s = pptx.addSlide(); s.background = { color: C.paper };
    header(s, 15, 'Appendix: full Point claim · model · prose trace ledger', '이 deck은 10 claims, 8 nodes, 18 edges, 7 boundaries와 context/state/proof/implication inventory를 canonical Point hash에 연결한다.');
    const rows = [
      ['C-001', 'release-control thesis', '01'], ['C-002', 'actors / trust roles', '02, 05, 10'], ['C-003', 'threat and trust assumptions', '03, 04'], ['C-004', 'closed Background Check path', '04–09'], ['C-005', 'PCS/PCCS collateral path', '10'],
      ['C-006', 'K/D/E + Result profile', '07–09'], ['C-007', 'proof / non-proof boundary', '11'], ['C-008', 'Intel-rats strengths / corrections', '12'], ['C-009', 'SGX vs TDX scope', '13'], ['C-010', 'owners and pilot', '14'],
    ];
    const xs = [0.72, 2.0, 7.9]; const ws = [0.95, 5.55, 4.4];
    ['Point claim', 'Reader-visible meaning', 'Primary slide(s)'].forEach((h, i) => { rect(s, xs[i], 1.55, ws[i], 0.5, C.navy, C.navy); addText(s, h, { x: xs[i] + 0.1, y: 1.74, w: ws[i] - 0.2, h: 0.12, fontSize: 9.2, bold: true, color: C.white, align: 'center' }); });
    rows.forEach((r, i) => { const y = 2.05 + i * 0.43; r.forEach((v, j) => { rect(s, xs[j], y, ws[j], 0.42, i % 2 ? C.paleSlate : C.white, i % 2 ? C.paleSlate : C.white); addText(s, v, { x: xs[j] + 0.1, y: y + 0.14, w: ws[j] - 0.2, h: 0.1, fontSize: j === 1 ? 9.2 : 8.8, color: j === 0 ? C.teal : C.text, bold: j === 0 }); }); });
    rect(s, 0.72, 6.53, 12.08, 0.25, C.paleAmber, C.paleAmber, true);
    addText(s, 'Exact object-level location, qualifiers, proof limits, implications, sources, and all N/E/B/X IDs: final/structural-coverage-map.json + final/prose-trace.json', { x: 0.95, y: 6.61, w: 11.6, h: 0.1, fontSize: 7.8, color: C.amber, bold: true, align: 'center' });
    footer(s, 'Canonical Point hash and complete coverage/prose trace.');
  }
  return pptx;
}

const summary = buildSummary();
const structural = buildStructural();
const summaryPath = 'final/summary/intel-tdx-attestation-prose-summary.pptx';
const structuralPath = 'final/structural/intel-tdx-attestation-prose-structural.pptx';
fs.mkdirSync(path.join(root, 'final/summary'), { recursive: true });
fs.mkdirSync(path.join(root, 'final/structural'), { recursive: true });
await summary.writeFile({ fileName: path.join(root, summaryPath) });
await structural.writeFile({ fileName: path.join(root, structuralPath) });

const claimSlides = { 'C-001': [1], 'C-002': [2, 5, 10], 'C-003': [3, 4], 'C-004': [4, 5, 6, 8, 9], 'C-005': [10], 'C-006': [7, 8, 9], 'C-007': [11], 'C-008': [12], 'C-009': [13], 'C-010': [14] };
const nodeSlides = { 'N-001': [14], 'N-002': [1, 2, 4, 6, 8, 9, 14], 'N-003': [1, 2, 4, 6, 8], 'N-004': [1, 2, 4, 5, 6, 9], 'N-005': [2, 5], 'N-006': [2, 5], 'N-007': [10], 'N-008': [5, 10] };
const edgeSlides = { 'E-001': [14], 'E-002': [14], 'E-003': [4], 'E-004': [4], 'E-005': [4], 'E-006': [5], 'E-007': [5], 'E-008': [10], 'E-009': [5, 10], 'E-010': [5], 'E-011': [5], 'E-012': [6], 'E-013': [6, 7, 8], 'E-014': [10], 'E-015': [8], 'E-016': [9], 'E-017': [9], 'E-018': [9] };
const boundarySlides = { 'B-001': [3], 'B-002': [5], 'B-003': [10], 'B-004': [6, 7], 'B-005': [8], 'B-006': [1, 8, 9], 'B-007': [11, 13] };
const contextSlides = { 'X-001': [4, 7, 8], 'X-002': [4, 6, 7], 'X-003': [6, 7, 8, 9], 'X-004': [6, 7, 8] };
const sentenceByClaim = {
  'C-001': 'Verifier가 Evidence를 평가해도 secret을 공개하지는 않는다. 공개 권한은 RP/KMS가 자신의 release policy로 Result를 확인한 뒤에만 행사한다.',
  'C-002': 'QGS가 Quote generation을 조율해도 signer는 TDQE다. Verifier가 Result를 서명해도 secret을 공개하는 owner는 RP/KMS다.',
  'C-003': 'untrusted path가 Quote를 재전송하거나 바꿔도, Verifier는 retained nonce·request·key binding을 다시 비교한다.',
  'C-004': 'RP/KMS가 TD에서 받은 exact Quote, canonical key bytes, identical request context를 Verifier에 전달하고, Verifier는 retained context와 비교한다. deny·replay·expiry·invalid collateral·failed PoP는 NO KEY로 끝난다.',
  'C-005': 'Verifier는 PCCS를 믿어서가 아니라 received collateral의 signature·chain·status·freshness를 확인해서만 사용한다.',
  'C-006': 'Verifier는 K/D/E를 재계산하고 signed Result에 verdict, policy version, E와 allow-only K를 넣으며 RP/KMS는 이를 다시 확인한다.',
  'C-007': 'Quote는 reported TD state와 binding을 보여 주지만 code correctness, container identity, future safety, availability를 증명하지 않는다.',
  'C-008': 'Intel-rats는 판단 구조를 배우는 자료로 쓰되 deployable verifier baseline으로는 쓰지 않는다.',
  'C-009': 'TDX Quote는 whole TD/VM state를 보고하므로 TD 안의 container identity를 자동으로 증명하지 않는다.',
  'C-010': '첫 pilot은 하나의 revocable key-release path에서 owner와 negative test 기준을 먼저 확정한다.',
};
const coverage = [];
for (const [id, slides] of Object.entries(claimSlides)) coverage.push({ id, kind: 'claim', slides, object_ids: slides.map((s) => `st${String(s).padStart(2, '0')}-${id.toLowerCase()}`), coverage_role: 'primary', prose_sentence: sentenceByClaim[id] });
for (const [id, slides] of Object.entries(nodeSlides)) coverage.push({ id, kind: 'model-node', slides, object_ids: slides.map((s) => `st${String(s).padStart(2, '0')}-${id.toLowerCase()}`), coverage_role: 'primary' });
for (const [id, slides] of Object.entries(edgeSlides)) coverage.push({ id, kind: 'model-edge', slides, object_ids: slides.map((s) => `st${String(s).padStart(2, '0')}-${id.toLowerCase()}`), coverage_role: 'primary' });
for (const [id, slides] of Object.entries(boundarySlides)) coverage.push({ id, kind: 'model-boundary', slides, object_ids: slides.map((s) => `st${String(s).padStart(2, '0')}-${id.toLowerCase()}`), coverage_role: 'primary' });
for (const [id, slides] of Object.entries(contextSlides)) coverage.push({ id, kind: 'context-dependency', slides, object_ids: slides.map((s) => `st${String(s).padStart(2, '0')}-${id.toLowerCase()}`), coverage_role: 'primary' });
['Quote integrity and credential linkage', 'reported TD measurement/attribute/TCB state', 'D matches retained context and K', 'Result binds E, policy version, and allow-only K', 'reference-value comparison'].forEach((text, i) => coverage.push({ id: `P-${String(i + 1).padStart(3, '0')}`, kind: 'proves', text, slides: [11], object_ids: [`st11-prove-${i + 1}`], coverage_role: 'primary' }));
['code correctness', 'container/process identity', 'future behavior', 'freshness without retained challenge', 'PoP/Result authenticity/authorization without checks', 'availability and all side-channel/I/O/physical/supply-chain risks'].forEach((text, i) => coverage.push({ id: `NP-${String(i + 1).padStart(3, '0')}`, kind: 'does-not-prove', text, slides: [11], object_ids: [`st11-limit-${i + 1}`], coverage_role: 'primary' }));
['Implement versioned K/D/E digest suite', 'Make context/key/Quote/Result/state first-class', 'Verify Result then PoP and same key channel', 'Consume terminal state atomically', 'Add workload Evidence for container identity'].forEach((text, i) => coverage.push({ id: `D-${String(i + 1).padStart(3, '0')}`, kind: 'developer-implication', text, slides: [14], object_ids: [`st14-dev-${i + 1}`], coverage_role: 'primary' }));
['Start revocable key-release pilot', 'Separate appraisal/release owners', 'Fail closed on negative outcomes', 'Set numeric clock/collateral/revocation targets', 'Measure zero release and rollback readiness'].forEach((text, i) => coverage.push({ id: `XEC-${String(i + 1).padStart(3, '0')}`, kind: 'executive-implication', text, slides: [14], object_ids: [`st14-exec-${i + 1}`], coverage_role: 'primary' }));
['Intel-rats is a teaching artifact, not deployable quote-verification reference code', 'Background Check route differs from RFC and aggregate edges may disagree', 'First-class nonce/audience/expiry/workload Evidence and concrete DCAP/deployment/policy implementation are omitted', 'No version-specific Quote binary-field enumeration or full DCAP API instructions', 'K/D/E and Result fields are an example profile, not a universal standard', 'No vendor-selection or production-readiness recommendation', 'Owners must set organization-specific numeric SLO values', 'No claim that TDX removes every infrastructure, application, or side-channel risk'].forEach((text, i) => coverage.push({ id: `CV-${String(i + 1).padStart(3, '0')}`, kind: 'caveat-or-exclusion', text, slides: [12, 13, 14], object_ids: [`st12-caveat-${i + 1}`], coverage_role: 'primary' }));
for (let i = 1; i <= 12; i += 1) coverage.push({ id: `S-${String(i).padStart(3, '0')}`, kind: 'source-reference', slides: [15], object_ids: ['st15-source-ledger'], coverage_role: 'appendix' });

const proseTrace = {
  schema_version: 'to-deck.prose-trace.v1', canonical_point_sha256: pointSha, projection_sha256: pointSha, projection_complete: true,
  rows: Object.entries(sentenceByClaim).map(([point_id, sentence]) => ({ point_id, slide: claimSlides[point_id][0], sentence, qualifier_location: point_id === 'C-003' ? 'slide 3 threat model' : point_id === 'C-007' ? 'slide 11 proof boundary' : `slide ${claimSlides[point_id][0]} narrative`, proof_limit_location: point_id === 'C-007' ? 'slide 11 non-proof column' : 'slide 11 proof boundary' })),
  failures: [],
};
const crosswalk = {
  schema_version: 'to-deck.summary-structural-crosswalk.v2', point_sha256: pointSha, summary_deck: summaryPath, structural_deck: structuralPath,
  summary_must_see_ids: ['C-001', 'C-002', 'C-004', 'C-006', 'C-007', 'E-013', 'E-015', 'E-018', 'B-006'],
  deliberate_summary_omissions: ['full threat model', 'all collateral detail', 'complete K/D/E profile', 'all caveats and pilot ownership'],
  semantic_invariants: ['QGS transport is distinct from TDQE signing', 'PCS authority is distinct from PCCS cache', 'Verifier appraises Evidence while RP/KMS owns release', 'K/D/E bind key, context, and exact Quote independently', 'Result/time/E/K/PoP/one-time state are required before release', 'deny/replay/expiry/invalid collateral/failed PoP result in NO KEY'],
};
const provenance = { schema_version: 'to-deck.prose-v2-build.v1', canonical_point_sha256: pointSha, point_inputs: ['input/point.md', 'input/point.yaml', 'input/point.sha256', 'input/point-gate.json'], projection_used: false, source_script: 'build-prose-v2.mjs', summary: summaryPath, structural: structuralPath, summary_slide_count: 2, structural_slide_count: 15 };
saveJson('final/structural-coverage-map.json', { schema_version: 'to-deck.structural-coverage.v2', canonical_point_sha256: pointSha, deck: structuralPath, coverage });
saveJson('final/prose-trace.json', proseTrace);
saveJson('final/summary-structural-crosswalk.json', crosswalk);
saveJson('final/build-provenance.json', provenance);
saveJson('final/summary/visual-model.json', { schema_version: 'to-deck.visual-model.v2', canonical_point_sha256: pointSha, deck: summaryPath, must_see_ids: crosswalk.summary_must_see_ids });
saveJson('final/structural/visual-model.json', { schema_version: 'to-deck.visual-model.v2', canonical_point_sha256: pointSha, deck: structuralPath, covered_ids: coverage.map((row) => row.id) });
console.log(JSON.stringify({ pointSha, summaryPath, structuralPath, coverage_rows: coverage.length, prose_rows: proseTrace.rows.length }, null, 2));

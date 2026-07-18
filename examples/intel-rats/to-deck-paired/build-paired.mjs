import fs from 'node:fs';
import path from 'node:path';
import PptxGenJS from 'pptxgenjs';

const root = path.resolve('.');
const input = JSON.parse(fs.readFileSync(path.join(root, 'input/to-site.input.json'), 'utf8'));
const pointSha = input.source_manifest.point_sha256;
const S = new PptxGenJS().ShapeType;
const C = {
  ink: '071827', ink2: '102A43', paper: 'F7F9FC', white: 'FFFFFF', black: '102033',
  slate: '45627D', muted: '9DB3C8', line: 'B6C7D8', evidence: '0E7490',
  decision: '175CD3', allow: '15803D', deny: 'B42318', violet: '7C3AED',
  paleBlue: 'E9F4FB', paleGreen: 'EAF7EF', paleRed: 'FFF0EF', paleYellow: 'FFF8E5',
  paleViolet: 'F2EEFF', paleSlate: 'EEF3F8', deepTeal: '12334A',
};

function deck(title, subject) {
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

function text(slide, value, options = {}) {
  slide.addText(value, { fontFace: 'Apple SD Gothic Neo', margin: 0, breakLine: false, ...options });
}
function box(slide, x, y, w, h, fill, line = fill, radius = false) {
  slide.addShape(radius ? S.roundRect : S.rect, { x, y, w, h, fill: { color: fill }, line: { color: line, width: 0.7 } });
}
function arrow(slide, x1, y1, x2, y2, color, width = 1.8, dash = undefined) {
  slide.addShape(S.line, { x: x1, y: y1, w: x2 - x1, h: y2 - y1,
    line: { color, width, beginArrowType: 'none', endArrowType: 'triangle', dashType: dash } });
}
function arrowBoth(slide, x1, y1, x2, y2, color, width = 1.8) {
  slide.addShape(S.line, { x: x1, y: y1, w: x2 - x1, h: y2 - y1,
    line: { color, width, beginArrowType: 'triangle', endArrowType: 'triangle' } });
}
function line(slide, x1, y1, x2, y2, color, width = 0.8, dash = undefined) {
  slide.addShape(S.line, { x: x1, y: y1, w: x2 - x1, h: y2 - y1, line: { color, width, dashType: dash } });
}
function tag(slide, value, x, y, w, fill, color = C.white) {
  box(slide, x, y, w, 0.27, fill, fill);
  text(slide, value, { x, y: y + 0.065, w, h: 0.1, fontSize: 7.6, bold: true, color, align: 'center' });
}
function title(slide, heading, subheading, dark = false, page = undefined) {
  text(slide, heading, { x: 0.55, y: 0.34, w: 11.7, h: 0.42, fontSize: 25.5, bold: true, color: dark ? C.white : C.black });
  text(slide, subheading, { x: 0.57, y: 0.88, w: 11.75, h: 0.25, fontSize: 13.1, color: dark ? C.muted : C.slate, fit: 'shrink' });
  if (page) text(slide, String(page).padStart(2, '0'), { x: 12.25, y: 0.42, w: 0.52, h: 0.16, fontSize: 9.5, bold: true, color: dark ? C.muted : C.slate, align: 'right' });
}
function footer(slide, value, dark = false) {
  line(slide, 0.55, 6.98, 12.78, 6.98, dark ? '244256' : 'D3DEE8', 0.45);
  text(slide, value, { x: 0.55, y: 7.1, w: 8.65, h: 0.14, fontSize: 7.4, color: dark ? C.muted : C.slate, fit: 'shrink' });
  text(slide, 'Sources: S-002 RFC 9334 · S-003 Intel DCAP', { x: 8.9, y: 7.1, w: 3.85, h: 0.14, fontSize: 7.4, color: dark ? C.muted : C.slate, align: 'right' });
}
function infoCard(slide, { x, y, w, h, step, heading, body, fill = C.white, color = C.black, tagFill = undefined }) {
  box(slide, x, y, w, h, fill, fill);
  if (step) tag(slide, step, x + 0.16, y + 0.16, 0.48, tagFill || C.slate);
  text(slide, heading, { x: x + 0.16, y: y + 0.54, w: w - 0.32, h: 0.28, fontSize: 15.5, bold: true, color, fit: 'shrink' });
  text(slide, body, { x: x + 0.16, y: y + 0.95, w: w - 0.32, h: h - 1.12, fontSize: 10.7, color, breakLine: false, fit: 'shrink', valign: 'mid' });
}
function statusBox(slide, x, y, w, h, heading, body, fill, headingColor = C.white, bodyColor = C.white) {
  box(slide, x, y, w, h, fill, fill);
  text(slide, heading, { x: x + 0.18, y: y + 0.2, w: w - 0.36, h: 0.23, fontSize: 15.2, bold: true, color: headingColor, align: 'center', fit: 'shrink' });
  text(slide, body, { x: x + 0.18, y: y + 0.57, w: w - 0.36, h: h - 0.7, fontSize: 9.2, color: bodyColor, align: 'center', fit: 'shrink', valign: 'mid' });
}
function compactCallout(slide, x, y, w, heading, body, fill, color) {
  box(slide, x, y, w, 0.66, fill, fill);
  text(slide, heading, { x: x + 0.14, y: y + 0.13, w: w - 0.28, h: 0.13, fontSize: 10.2, bold: true, color, fit: 'shrink' });
  text(slide, body, { x: x + 0.14, y: y + 0.38, w: w - 0.28, h: 0.12, fontSize: 7.7, color, fit: 'shrink' });
}
function proofCallout(slide, x, y, w, heading, body, fill, color) {
  box(slide, x, y, w, 1.08, fill, fill);
  text(slide, heading, { x: x + 0.18, y: y + 0.22, w: w - 0.36, h: 0.2, fontSize: 15.2, bold: true, color, fit: 'shrink' });
  text(slide, body, { x: x + 0.18, y: y + 0.68, w: w - 0.36, h: 0.15, fontSize: 9.85, color, fit: 'shrink' });
}
function laneHeader(slide, x, label, sub, color) {
  box(slide, x, 1.42, 2.04, 0.65, color, color);
  text(slide, label, { x, y: 1.58, w: 2.04, h: 0.18, fontSize: 14.5, bold: true, color: C.white, align: 'center' });
  text(slide, sub, { x, y: 1.83, w: 2.04, h: 0.12, fontSize: 8.2, color: 'E9F2F8', align: 'center' });
  line(slide, x + 1.02, 2.1, x + 1.02, 6.62, 'B7C8D7', 0.65, 'dash');
}
function saveJson(relative, value) {
  const file = path.join(root, relative);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, JSON.stringify(value, null, 2) + '\n');
}

function buildSummary() {
  const pptx = deck('Intel TDX 원격 증명 — 2장 요약', 'Decision model and signed Result sequence');
  {
    const slide = pptx.addSlide();
    slide.background = { color: C.ink };
    title(slide, '검증은 증거를 판정하고, 공개는 정책이 결정한다', '유효한 Quote는 자동 권한 부여가 아니다. signed Result는 RP/KMS release policy의 입력이다.', true, 1);
    tag(slide, 'COLLATERAL SIDE PATH', 4.18, 1.32, 1.55, C.ink2, '9ED8EB');
    text(slide, 'Intel PCS → PCCS cache → signed collateral → Verifier', { x: 3.52, y: 1.69, w: 2.9, h: 0.15, fontSize: 8.9, bold: true, color: '9ED8EB', align: 'center' });
    arrow(slide, 5.0, 1.88, 5.0, 2.12, C.evidence, 1.2, 'dash');
    infoCard(slide, { x: 0.6, y: 2.25, w: 2.45, h: 2.25, step: '01', heading: 'EVIDENCE', body: 'TD Quote + canonical key bytes + bound request context', fill: C.deepTeal, color: C.white, tagFill: '1F5975' });
    infoCard(slide, { x: 3.55, y: 2.12, w: 2.7, h: 2.52, step: '02', heading: 'VERIFIER', body: 'Quote·collateral 평가\nK / D / E 재계산\nsigned Result 생성', fill: C.evidence, color: C.white, tagFill: '075568' });
    infoCard(slide, { x: 7.35, y: 2.12, w: 2.7, h: 2.52, step: '03', heading: 'RP / KMS', body: 'Result + time + E/K 확인\nPoP 확인\n별도 release policy', fill: C.decision, color: C.white, tagFill: '0F4DAA' });
    arrow(slide, 3.06, 3.38, 3.54, 3.38, '80CFE5', 2.15);
    text(slide, 'Quote + context', { x: 2.72, y: 3.05, w: 1.16, h: 0.14, fontSize: 8.9, bold: true, color: 'BCEAF7', align: 'center' });
    arrow(slide, 6.26, 3.38, 7.34, 3.38, '75C1FF', 2.5);
    text(slide, 'signed Result', { x: 6.18, y: 3.05, w: 1.22, h: 0.14, fontSize: 8.9, bold: true, color: 'A9D8FF', align: 'center' });
    statusBox(slide, 10.65, 2.4, 1.95, 0.86, 'ALLOW', 'one-time\nsecret', C.allow, C.white, 'D8F5E2');
    statusBox(slide, 10.65, 3.68, 1.95, 0.86, 'NO KEY', 'deny · replay\n· expiry', C.deny, C.white, 'FFE1DE');
    arrow(slide, 10.08, 2.95, 10.64, 2.82, C.allow, 1.9);
    arrow(slide, 10.08, 3.83, 10.64, 4.08, C.deny, 1.9);
    tag(slide, 'K/D/E: symbolic profile', 4.0, 4.78, 1.8, C.ink2, '9ED8EB');
    text(slide, 'deployment은 별도 trust anchor·조직 policy를 명시해야 한다.', { x: 5.92, y: 4.85, w: 4.15, h: 0.13, fontSize: 8.4, bold: true, color: '9ED8EB', fit: 'shrink' });
    proofCallout(slide, 0.6, 5.17, 5.8, '이 경로가 증명하는 것', 'reported TD state + request/key binding을 조직 policy로 평가할 수 있다.', '0B3140', C.white);
    proofCallout(slide, 6.75, 5.17, 5.85, '이 경로만으로는 증명하지 않는 것', 'code correctness · container identity · future safety · availability', '3B1C27', C.white);
    footer(slide, 'Intel-rats: learning / design-review only · not a production verifier baseline.', true);
  }
  {
    const slide = pptx.addSlide();
    slide.background = { color: C.paper };
    title(slide, 'signed Result는 어떻게 만들어지는가', 'QGS는 transport이고 TDQE는 Quote signer다. 한 message는 한 arrow에만 둔다. K/D/E는 symbolic deployment profile이다.', false, 2);
    const lanes = [
      [0.58, 'RP / KMS', 'release owner', C.decision], [3.05, 'Verifier', 'appraisal owner', C.evidence],
      [5.52, 'TD', 'attester', '315B86'], [7.99, 'QGS', 'transport only', '64748B'], [10.46, 'TDQE', 'Quote signer', C.violet],
    ];
    lanes.forEach(([x, label, sub, color]) => laneHeader(slide, x, label, sub, color));
    text(slide, '01  Bind', { x: 0.58, y: 2.2, w: 1.0, h: 0.16, fontSize: 10, bold: true, color: C.slate });
    arrow(slide, 1.6, 2.48, 4.08, 2.48, C.decision); text(slide, 'request ID + subject + audience', { x: 1.78, y: 2.25, w: 2.12, h: 0.13, fontSize: 8.4, bold: true, color: C.decision, align: 'center' });
    arrow(slide, 4.08, 2.82, 1.6, 2.82, C.evidence); text(slide, 'nonce (Verifier retains context)', { x: 1.74, y: 2.59, w: 2.18, h: 0.13, fontSize: 8.4, bold: true, color: C.evidence, align: 'center' });
    arrow(slide, 1.6, 3.16, 6.55, 3.16, C.decision); text(slide, 'RP forwards nonce + bound request context', { x: 2.12, y: 2.93, w: 3.9, h: 0.13, fontSize: 8.4, bold: true, color: C.decision, align: 'center' });
    text(slide, '02  Quote', { x: 0.58, y: 3.45, w: 1.0, h: 0.16, fontSize: 10, bold: true, color: C.slate });
    arrow(slide, 6.55, 3.77, 9.02, 3.77, '315B86'); text(slide, 'TDREPORT: D/K', { x: 6.9, y: 3.54, w: 1.7, h: 0.13, fontSize: 8.4, bold: true, color: '315B86', align: 'center' });
    arrow(slide, 9.02, 4.1, 11.49, 4.1, '64748B'); text(slide, 'same-platform report', { x: 9.1, y: 3.87, w: 2.15, h: 0.13, fontSize: 8.4, bold: true, color: '64748B', align: 'center' });
    arrow(slide, 11.49, 4.44, 9.02, 4.44, C.violet); text(slide, 'TDQE-signed Quote', { x: 9.26, y: 4.21, w: 1.98, h: 0.13, fontSize: 8.4, bold: true, color: C.violet, align: 'center' });
    arrow(slide, 9.02, 4.78, 6.55, 4.78, '64748B'); text(slide, 'Quote returns through guest path', { x: 6.72, y: 4.55, w: 2.16, h: 0.13, fontSize: 8.3, bold: true, color: '64748B', align: 'center' });
    arrow(slide, 6.55, 5.1, 1.6, 5.1, '315B86'); text(slide, 'exact Quote + canonical key bytes', { x: 1.95, y: 4.87, w: 4.1, h: 0.13, fontSize: 8.3, bold: true, color: '315B86', align: 'center' });
    arrow(slide, 1.6, 5.42, 4.08, 5.42, C.evidence); text(slide, 'Evidence + key + identical context', { x: 1.72, y: 5.19, w: 2.28, h: 0.13, fontSize: 8.3, bold: true, color: C.evidence, align: 'center' });
    text(slide, '03  Appraise', { x: 0.58, y: 5.38, w: 0.9, h: 0.15, fontSize: 8.5, bold: true, color: C.slate });
    arrow(slide, 4.08, 5.65, 1.6, 5.65, C.evidence, 2.25); text(slide, 'signed Result: verdict + policy version + E + allow-only K', { x: 1.62, y: 5.42, w: 2.42, h: 0.13, fontSize: 7.65, bold: true, color: C.evidence, align: 'center', fit: 'shrink' });
    arrowBoth(slide, 1.6, 6.1, 6.55, 6.1, C.allow, 1.6); text(slide, 'PoP challenge / response', { x: 2.7, y: 5.87, w: 2.72, h: 0.13, fontSize: 8.1, bold: true, color: C.allow, align: 'center' });
    arrow(slide, 1.6, 6.52, 6.55, 6.52, C.allow, 1.6); text(slide, 'after ALLOW: secret only on same approved K channel', { x: 2.1, y: 6.29, w: 4.15, h: 0.13, fontSize: 8.1, bold: true, color: C.allow, align: 'center' });
    footer(slide, 'Summary sequence: request binding → TD/QGS/TDQE Quote path → appraisal Result → RP/KMS policy.', false);
  }
  return pptx;
}

function buildStructural() {
  const pptx = deck('Intel TDX 원격 증명 — 구조적 full deck', 'Complete Point projection with coverage trace');
  // 1: domain result
  {
    const slide = pptx.addSlide(); slide.background = { color: C.ink };
    title(slide, 'Intel TDX 원격 증명은 release-control system이다', '하드웨어 Evidence appraisal과 secret release를 하나로 합치지 않고, 서로 다른 책임으로 연결한다.', true, 1);
    tag(slide, 'POINT THESIS · C-001', 0.6, 1.43, 1.46, C.evidence);
    text(slide, '선택한 trust anchor와 조직 policy가 유효하다는 가정 아래, Verifier는 Evidence를 평가하고 RP/KMS는 별도 policy로 비밀 공개를 결정한다.', { x: 0.6, y: 1.88, w: 9.05, h: 0.66, fontSize: 22.5, bold: true, color: C.white, fit: 'shrink' });
    infoCard(slide, { x: 0.6, y: 3.02, w: 2.65, h: 2.22, step: 'A', heading: 'Attester', body: 'TD가 report와 bound context를 만든다.\nQGS와 TDQE는 서로 다른 역할이다.', fill: C.deepTeal, color: C.white, tagFill: '1F5975' });
    infoCard(slide, { x: 3.52, y: 3.02, w: 2.65, h: 2.22, step: 'B', heading: 'Verifier', body: 'Quote·collateral·context를 검증하고 appraisal Result를 signed 한다.', fill: C.evidence, color: C.white, tagFill: '075568' });
    infoCard(slide, { x: 6.44, y: 3.02, w: 2.65, h: 2.22, step: 'C', heading: 'RP / KMS', body: 'Result를 policy 입력으로 사용한다.\nRelease와 deny 책임은 여기 있다.', fill: C.decision, color: C.white, tagFill: '0F4DAA' });
    statusBox(slide, 9.82, 3.14, 2.6, 0.82, 'ALLOW', 'one-time secret release', C.allow, C.white, 'D8F5E2');
    statusBox(slide, 9.82, 4.3, 2.6, 0.82, 'NO KEY', 'deny · replay · expiry', C.deny, C.white, 'FFE1DE');
    arrow(slide, 3.26, 4.08, 3.51, 4.08, '80CFE5', 2); arrow(slide, 6.18, 4.08, 6.43, 4.08, '75C1FF', 2); arrow(slide, 9.1, 3.7, 9.81, 3.56, C.allow, 2); arrow(slide, 9.1, 4.42, 9.81, 4.67, C.deny, 2);
    text(slide, '교육 / design-review lens: Intel-rats는 deployable verifier baseline이 아니다.', { x: 0.6, y: 5.83, w: 11.8, h: 0.28, fontSize: 13, color: 'A4E9F7', bold: true });
    footer(slide, 'C-001 · C-004 · B-004/B-006. Structural overview; detailed evidence/result paths follow.', true);
  }
  // 2: roles and boundaries
  {
    const slide = pptx.addSlide(); slide.background = { color: C.paper };
    title(slide, '같은 경로에 있어도, 같은 trust role은 아니다', '구조적 deck은 actor·authority·cache·decision owner를 분리해 읽게 한다.', false, 2);
    const cols = [
      { x: 0.6, head: 'TD / QGS / TDQE', fill: 'EAF4FA', color: '315B86', rows: [['TD', 'report와 bound key context'], ['QGS', 'Quote transport / coordination'], ['TDQE', 'Quote signer']] },
      { x: 4.55, head: 'PCS / PCCS', fill: 'FFF8E5', color: 'A96500', rows: [['PCS', 'signed collateral authority'], ['PCCS', 'cache / transport'], ['Operations', 'outage·revocation policy']] },
      { x: 8.5, head: 'Verifier → RP/KMS', fill: 'EEF2FF', color: C.decision, rows: [['Verifier', 'Evidence appraisal + signed Result'], ['RP / KMS', 'Result-use policy + release'], ['Boundary', 'Result는 action이 아니다']] },
    ];
    cols.forEach((col) => {
      box(slide, col.x, 1.55, 3.52, 4.85, col.fill, col.fill);
      text(slide, col.head, { x: col.x + 0.2, y: 1.83, w: 3.1, h: 0.24, fontSize: 17, bold: true, color: col.color, align: 'center' });
      col.rows.forEach(([label, body], i) => {
        const y = 2.35 + i * 1.18;
        box(slide, col.x + 0.22, y, 3.08, 0.86, C.white, C.white);
        tag(slide, label, col.x + 0.4, y + 0.22, 0.8, col.color);
        text(slide, body, { x: col.x + 1.34, y: y + 0.27, w: 1.7, h: 0.17, fontSize: 9.7, color: C.black, fit: 'shrink' });
      });
    });
    text(slide, 'Required distinctions: QGS ≠ TDQE · PCS ≠ PCCS · Verifier ≠ RP/KMS · Evidence ≠ Result ≠ action.', { x: 0.75, y: 6.52, w: 11.8, h: 0.2, fontSize: 11.6, bold: true, color: C.deny, align: 'center' });
    footer(slide, 'C-005 and Point five-boundary inventory. Color supports labels; it does not encode meaning alone.');
  }
  // 3: primary path
  {
    const slide = pptx.addSlide(); slide.background = { color: C.paper };
    title(slide, 'Primary path: request binding부터 one-time release까지', '각 단계는 다른 artifact와 owner를 갖는다. path가 닫혀야 policy action을 정당화할 수 있다.', false, 3);
    const steps = [
      ['01', 'Request', 'RP/KMS\nsubject · audience'], ['02', 'Context', 'Verifier nonce\nretains request'], ['03', 'Evidence', 'TD Report / Quote\nD/K binding'], ['04', 'Appraisal', 'Verifier validates\nQuote + collateral'], ['05', 'Result', 'signed verdict\nE + policy version'], ['06', 'Action', 'RP/KMS policy\nPoP → secret / no key'],
    ];
    steps.forEach(([n, head, body], i) => {
      const x = 0.45 + i * 2.08;
      const fill = i === 3 ? C.evidence : i >= 4 ? C.decision : i === 2 ? '315B86' : C.deepTeal;
      infoCard(slide, { x, y: 2.1, w: 1.67, h: 2.18, step: n, heading: head, body, fill, color: C.white, tagFill: '315B86' });
      if (i < steps.length - 1) arrow(slide, x + 1.68, 3.15, x + 2.06, 3.15, i === 3 ? C.evidence : C.decision, 1.8);
    });
    box(slide, 0.62, 4.85, 12.1, 1.08, C.paleBlue, C.paleBlue);
    text(slide, 'Closed-path invariant', { x: 0.9, y: 5.12, w: 2.15, h: 0.2, fontSize: 14, bold: true, color: C.evidence });
    text(slide, 'Evidence must reach appraisal with the intended request/key context; the authenticated Result must reach the distinct policy owner before any release.', { x: 3.05, y: 5.12, w: 9.15, h: 0.26, fontSize: 12.4, color: C.black, fit: 'shrink' });
    tag(slide, 'E-013', 2.45, 6.18, 0.62, C.evidence); tag(slide, 'E-015', 5.34, 6.18, 0.62, C.evidence); tag(slide, 'E-018', 8.23, 6.18, 0.62, C.allow);
    text(slide, 'Evidence + key + context', { x: 3.15, y: 6.25, w: 1.75, h: 0.12, fontSize: 8.7, color: C.slate });
    text(slide, 'signed Result', { x: 6.05, y: 6.25, w: 1.4, h: 0.12, fontSize: 8.7, color: C.slate });
    text(slide, 'same approved K channel', { x: 8.95, y: 6.25, w: 2.05, h: 0.12, fontSize: 8.7, color: C.slate });
    footer(slide, 'C-004 · E-013/E-015/E-018 · B-004/B-006.');
  }
  // 4: evidence
  {
    const slide = pptx.addSlide(); slide.background = { color: C.paper };
    title(slide, 'Evidence는 Quote 하나가 아니라, 연결된 input set이다', '선택한 attestation trust model과 appraisal policy 아래에서 Verifier는 Quote, collateral, canonical key bytes, bound request context를 같은 appraisal에 넣는다.', false, 4);
    const data = [
      { x: 0.62, head: 'TDREPORT / Quote', body: 'reported TD state와 D/K bound context를 전달한다.', fill: 'EAF4FA', color: '315B86' },
      { x: 3.72, head: 'Canonical key bytes', body: 'Result-use 단계에서 다시 확인할 key binding의 기준이다.', fill: C.paleGreen, color: C.allow },
      { x: 6.82, head: 'Request context', body: 'nonce · subject · audience를 통한 request binding의 기준이다.', fill: C.paleViolet, color: C.violet },
      { x: 9.92, head: 'Signed collateral', body: 'authority bytes의 chain · status · freshness를 평가한다.', fill: C.paleYellow, color: 'A96500' },
    ];
    data.forEach((item, i) => {
      infoCard(slide, { x: item.x, y: 2.05, w: 2.52, h: 2.46, step: String(i + 1).padStart(2, '0'), heading: item.head, body: item.body, fill: item.fill, color: item.color, tagFill: item.color });
      arrow(slide, item.x + 1.26, 4.55, 6.66, 5.18, item.color, 1.3, 'dash');
    });
    box(slide, 4.87, 5.02, 3.58, 1.0, C.evidence, C.evidence);
    text(slide, 'Verifier appraisal', { x: 5.2, y: 5.28, w: 2.9, h: 0.22, fontSize: 16.5, bold: true, color: C.white, align: 'center' });
    text(slide, '각 input의 binding과 validity를 함께 판정', { x: 5.08, y: 5.63, w: 3.15, h: 0.12, fontSize: 8.8, color: 'D8F5E2', align: 'center' });
    box(slide, 0.62, 6.27, 12.1, 0.38, C.paleRed, C.paleRed);
    text(slide, 'Proof limit: Quote validity만으로 result-use policy, one-time state, workload identity, runtime behavior를 대체하지 않는다.', { x: 0.9, y: 6.4, w: 11.55, h: 0.12, fontSize: 9.1, bold: true, color: C.deny, align: 'center' });
    footer(slide, 'C-004/C-007 · E-013 · B-004.');
  }
  // 5: quote sequence
  {
    const slide = pptx.addSlide(); slide.background = { color: C.paper };
    title(slide, 'Quote generation: TD, QGS, TDQE의 역할을 섞지 않는다', 'QGS는 guest-path transport/coordination이고 TDQE가 Quote를 sign한다. K/D/E는 이 Point의 symbolic deployment profile이다.', false, 5);
    const lanes = [[0.58, 'TD', 'attester', '315B86'], [3.05, 'QGS', 'transport only', '64748B'], [5.52, 'TDQE', 'Quote signer', C.violet], [7.99, 'RP / KMS', 'request owner', C.decision], [10.46, 'Verifier', 'appraisal owner', C.evidence]];
    lanes.forEach(([x, label, sub, color]) => laneHeader(slide, x, label, sub, color));
    arrow(slide, 1.6, 2.66, 4.08, 2.66, '315B86', 1.8); text(slide, 'TDREPORT: D/K', { x: 1.95, y: 2.39, w: 1.72, h: 0.14, fontSize: 8.6, color: '315B86', bold: true, align: 'center' });
    arrow(slide, 4.08, 3.2, 6.55, 3.2, '64748B', 1.8); text(slide, 'same-platform report', { x: 4.42, y: 2.93, w: 1.82, h: 0.14, fontSize: 8.4, color: '64748B', bold: true, align: 'center' });
    arrow(slide, 6.55, 3.74, 4.08, 3.74, C.violet, 1.8); text(slide, 'TDQE-signed Quote', { x: 4.38, y: 3.47, w: 1.86, h: 0.14, fontSize: 8.4, color: C.violet, bold: true, align: 'center' });
    arrow(slide, 4.08, 4.28, 1.6, 4.28, '64748B', 1.8); text(slide, 'Quote returns through guest path', { x: 1.78, y: 4.01, w: 2.12, h: 0.14, fontSize: 8.2, color: '64748B', bold: true, align: 'center' });
    arrow(slide, 1.6, 4.82, 9.02, 4.82, '315B86', 1.8); text(slide, 'exact Quote + canonical key bytes', { x: 3.55, y: 4.55, w: 3.42, h: 0.14, fontSize: 8.2, color: '315B86', bold: true, align: 'center' });
    arrow(slide, 9.02, 5.28, 11.49, 5.28, C.evidence, 1.8); text(slide, 'E-013: Evidence + key + bound request context', { x: 9.05, y: 5.01, w: 2.4, h: 0.14, fontSize: 7.65, color: C.evidence, bold: true, align: 'center', fit: 'shrink' });
    compactCallout(slide, 0.7, 5.92, 3.73, 'Anti-collapse rule', 'QGS transport success는 Quote signing authority가 아니다.', C.paleRed, C.deny);
    compactCallout(slide, 4.8, 5.92, 3.73, 'Binding rule', 'RP/KMS가 bound package를 Verifier에 전달하고 retained context와 맞춘다.', C.paleBlue, C.evidence);
    compactCallout(slide, 8.9, 5.92, 3.73, 'Reader check', '누가 sign·transport하고, 어느 bytes를 평가하는가?', C.paleGreen, C.allow);
    footer(slide, 'N-004/N-005/N-006/N-003 · C-004 · QGS/TDQE distinction.');
  }
  // 6: collateral sequence
  {
    const slide = pptx.addSlide(); slide.background = { color: C.paper };
    title(slide, 'Collateral: PCS authority와 PCCS cache를 구별한다', 'Verifier가 신뢰하는 것은 cache의 availability가 아니라 received bytes의 cryptographic/status/freshness checks다.', false, 6);
    infoCard(slide, { x: 0.7, y: 2.2, w: 2.55, h: 2.15, step: '01', heading: 'Intel PCS', body: 'signed collateral authority\nissuer / signed data origin', fill: C.paleYellow, color: '8A5600', tagFill: 'A96500' });
    infoCard(slide, { x: 5.37, y: 2.2, w: 2.55, h: 2.15, step: '02', heading: 'PCCS', body: 'cache / transport\navailability와 authority를 분리', fill: C.paleSlate, color: C.slate, tagFill: C.slate });
    infoCard(slide, { x: 10.04, y: 2.2, w: 2.55, h: 2.15, step: '03', heading: 'Verifier', body: 'signature · chain\nstatus · freshness 검증', fill: C.paleBlue, color: C.evidence, tagFill: C.evidence });
    arrow(slide, 3.27, 3.27, 5.35, 3.27, 'A96500', 2.3); text(slide, 'signed collateral bytes', { x: 3.62, y: 2.93, w: 1.42, h: 0.14, fontSize: 9.1, color: 'A96500', bold: true, align: 'center' });
    arrow(slide, 7.94, 3.27, 10.02, 3.27, C.evidence, 2.3); text(slide, 'cache-delivered bytes', { x: 8.27, y: 2.93, w: 1.42, h: 0.14, fontSize: 9.1, color: C.evidence, bold: true, align: 'center' });
    box(slide, 0.85, 5.07, 11.62, 1.05, C.paleRed, C.paleRed);
    text(slide, 'Operating consequence', { x: 1.15, y: 5.33, w: 2.0, h: 0.19, fontSize: 14, bold: true, color: C.deny });
    text(slide, 'PCCS outage와 collateral/certificate revocation은 별도 운영 policy가 필요하다. PCCS availability는 attestation validity를 보장하지 않는다.', { x: 3.16, y: 5.33, w: 8.8, h: 0.22, fontSize: 12.2, color: C.black, fit: 'shrink' });
    footer(slide, 'C-005 · N-008 · E-014. PCS ≠ PCCS.');
  }
  // 7: result action
  {
    const slide = pptx.addSlide(); slide.background = { color: C.ink };
    title(slide, 'signed Result는 release의 증거 입력이지, release 그 자체가 아니다', 'Verifier의 appraisal과 RP/KMS의 policy decision은 authenticated boundary로 연결되지만 같은 책임이 아니다.', true, 7);
    infoCard(slide, { x: 0.72, y: 2.0, w: 3.3, h: 3.05, step: '01', heading: 'Verifier Result', body: 'verdict\npolicy version\nEvidence identity E\nallow-only canonical key K\n\nResult는 verifier가 authenticated하게 전달한다.', fill: C.evidence, color: C.white, tagFill: '075568' });
    arrow(slide, 4.04, 3.52, 5.42, 3.52, '75C1FF', 2.7);
    text(slide, 'authenticated signed Result', { x: 4.15, y: 3.18, w: 1.16, h: 0.21, fontSize: 8.8, color: 'A9D8FF', bold: true, align: 'center', fit: 'shrink' });
    infoCard(slide, { x: 5.46, y: 2.0, w: 3.3, h: 3.05, step: '02', heading: 'RP / KMS checks', body: 'Result authenticity\ntime and policy version\nE/K binding\nproof of possession\none-time atomic state', fill: C.decision, color: C.white, tagFill: '0F4DAA' });
    arrow(slide, 8.78, 2.78, 10.05, 2.56, C.allow, 2.2); arrow(slide, 8.78, 3.75, 10.05, 3.58, C.deny, 2.2);
    statusBox(slide, 10.12, 2.15, 2.1, 0.76, 'ALLOW', 'policy decision', C.allow, C.white, 'D8F5E2');
    statusBox(slide, 10.12, 3.2, 2.1, 0.76, 'NO KEY', 'deny · replay · expiry', C.deny, C.white, 'FFE1DE');
    box(slide, 10.12, 4.38, 2.1, 0.8, C.deepTeal, C.deepTeal);
    text(slide, 'TD / K endpoint', { x: 10.28, y: 4.59, w: 1.78, h: 0.16, fontSize: 11.6, bold: true, color: C.white, align: 'center', fit: 'shrink' });
    text(slide, 'attester receives secret only after ALLOW', { x: 10.24, y: 4.86, w: 1.86, h: 0.12, fontSize: 6.95, color: 'A4E9F7', align: 'center', fit: 'shrink' });
    arrowBoth(slide, 8.78, 4.64, 10.1, 4.64, C.allow, 1.45); text(slide, 'PoP challenge / response', { x: 8.78, y: 4.36, w: 1.22, h: 0.12, fontSize: 6.95, bold: true, color: C.allow, align: 'center', fit: 'shrink' });
    arrow(slide, 8.78, 5.02, 10.1, 5.02, C.allow, 1.45); text(slide, 'E-018 secret on same approved K', { x: 8.63, y: 4.78, w: 1.5, h: 0.12, fontSize: 6.65, bold: true, color: C.allow, align: 'center', fit: 'shrink' });
    box(slide, 0.72, 5.78, 11.5, 0.58, '0B3140', '0B3140');
    text(slide, 'Boundary B-006', { x: 1.0, y: 5.99, w: 1.42, h: 0.14, fontSize: 10, bold: true, color: 'A4E9F7' });
    text(slide, 'Result verification cannot substitute for Result-use policy, state consumption, or secret delivery.', { x: 2.58, y: 5.97, w: 8.9, h: 0.18, fontSize: 11.2, color: C.white, fit: 'shrink' });
    footer(slide, 'C-004 · E-015/E-018 · B-006. Verifier/RP distinction.', true);
  }
  // 8: obligations
  {
    const slide = pptx.addSlide(); slide.background = { color: C.paper };
    title(slide, 'Deployment obligations은 valid Quote가 자동으로 제공하지 않는다', '보안·운영 요구는 Result-use path에 명시적으로 설계하고 검증해야 한다.', false, 8);
    const obligations = [
      ['Freshness', 'Verifier / Operations\nnonce, expiry, stale collateral 판단'], ['Request binding', 'RP/KMS + Verifier\nsubject · audience · request ownership'], ['Public-key binding', 'Verifier + RP/KMS\ncanonical K와 Evidence/Result의 일치'], ['Proof of possession', 'RP/KMS + TD endpoint\nK를 실제로 제어하는 endpoint 확인'], ['Authenticated Result', 'Verifier → RP/KMS\nverdict가 policy owner까지 변조 없이 도달'], ['One-time state', 'RP/KMS\nrelease decision·state consumption·secret delivery의 atomic terminal transition'],
    ];
    obligations.forEach(([head, body], i) => {
      const x = 0.64 + (i % 3) * 4.08; const y = 1.75 + Math.floor(i / 3) * 2.22;
      const colors = [C.evidence, C.violet, C.allow, C.decision, C.evidence, C.deny];
      infoCard(slide, { x, y, w: 3.62, h: 1.65, step: String(i + 1).padStart(2, '0'), heading: head, body, fill: C.white, color: colors[i], tagFill: colors[i] });
    });
    box(slide, 0.64, 6.2, 12.05, 0.42, C.paleRed, C.paleRed);
    text(slide, 'Failure policy must explicitly cover: deny · replay · expiry · invalid collateral · failed PoP → NO KEY.', { x: 0.92, y: 6.34, w: 11.5, h: 0.12, fontSize: 9.65, bold: true, color: C.deny, align: 'center' });
    footer(slide, 'Point five-boundary inventory and C-004/C-007 proof limits.');
  }
  // 9: proof bounds
  {
    const slide = pptx.addSlide(); slide.background = { color: C.paper };
    title(slide, 'Attestation result의 proof boundary를 명확히 읽는다', '선택한 attestation trust model과 appraisal policy 아래에서 Quote와 Result는 유용한 Evidence를 제공하지만 workload의 모든 property를 자동 증명하지 않는다.', false, 9);
    box(slide, 0.68, 1.65, 5.75, 4.9, C.paleGreen, C.paleGreen);
    text(slide, '이 경로가 하는 일', { x: 1.0, y: 1.96, w: 4.9, h: 0.27, fontSize: 20, bold: true, color: C.allow });
    const proves = ['reported TD state를 appraisal policy로 평가', '배포가 request / audience / public-key binding을 명시적으로 설계·검증', 'signed Result를 distinct policy owner에게 전달', 'secret release를 explicit allow / no-key branch로 분리'];
    proves.forEach((item, i) => { tag(slide, '✓', 1.02, 2.62 + i * 0.73, 0.32, C.allow); text(slide, item, { x: 1.52, y: 2.7 + i * 0.73, w: 4.45, h: 0.13, fontSize: 11.2, color: C.black, fit: 'shrink' }); });
    box(slide, 6.88, 1.65, 5.75, 4.9, C.paleRed, C.paleRed);
    text(slide, '이 경로만으로는 하지 않는 일', { x: 7.2, y: 1.96, w: 4.95, h: 0.27, fontSize: 20, bold: true, color: C.deny });
    const limits = ['code correctness / vulnerability absence', 'TD 내부 container·process의 automatic identity', 'attestation 이후 future-safe behavior', 'availability 및 side-channel·I/O·physical·supply-chain risk 제거'];
    limits.forEach((item, i) => { tag(slide, '×', 7.22, 2.62 + i * 0.73, 0.32, C.deny); text(slide, item, { x: 7.72, y: 2.7 + i * 0.73, w: 4.35, h: 0.13, fontSize: 11.2, color: C.black, fit: 'shrink' }); });
    text(slide, '설계 판단: workload identity와 runtime behavior에는 별도 Evidence / control을 추가한다.', { x: 0.9, y: 6.76, w: 11.6, h: 0.16, fontSize: 10, bold: true, color: C.slate, align: 'center' });
    footer(slide, 'C-007 and does_not_prove[0..3].');
  }
  // 10: project / decisions
  {
    const slide = pptx.addSlide(); slide.background = { color: C.ink };
    title(slide, 'Intel-rats는 learning lens이고, production baseline은 아니다', '도메인 mental model과 design-review 질문에는 사용하되, implementation/security approval/runtime enforcement 근거로 단독 사용하지 않는다.', true, 10);
    infoCard(slide, { x: 0.7, y: 2.0, w: 3.65, h: 3.35, step: 'USE', heading: 'Teach & review', body: 'remote-attestation decision system을 설명\ntrust role separation을 검토\nrequest / result / policy binding 질문 생성', fill: C.deepTeal, color: C.white, tagFill: '1F5975' });
    infoCard(slide, { x: 4.84, y: 2.0, w: 3.65, h: 3.35, step: 'DON’T', heading: 'Do not treat as', body: 'deployable Quote-verification implementation\nsecurity-approval baseline\nruntime-enforcement proof', fill: '3B1C27', color: C.white, tagFill: C.deny });
    infoCard(slide, { x: 8.98, y: 2.0, w: 3.65, h: 3.35, step: 'ASK', heading: 'Design review questions', body: '누가 Evidence를 평가하는가?\n누가 release policy를 소유하는가?\n어떤 binding/failure state가 explicit한가?', fill: C.decision, color: C.white, tagFill: '0F4DAA' });
    box(slide, 0.7, 5.85, 11.93, 0.58, '0B3140', '0B3140');
    text(slide, 'Executive action: policy ownership, collateral operations, key binding, replay/expiry handling을 release 전에 책임자로 확정한다.', { x: 1.05, y: 6.06, w: 11.25, h: 0.15, fontSize: 10.8, bold: true, color: 'A4E9F7', align: 'center' });
    footer(slide, 'Point use decision. Domain first; project assessment remains supporting.', true);
  }
  // 11: evidence ledger
  {
    const slide = pptx.addSlide(); slide.background = { color: C.paper };
    title(slide, 'Appendix · Claim · model · source ledger', '모든 material claim과 model element는 coverage map의 exact slide/object locator로 추적된다. 이 appendix는 Slide 10의 action 결론 뒤에 둔다.', false, 11);
    const rows = [
      ['C-001', 'Evidence appraisal + separate release policy', 'S-002, S-003', 'Slides 1, 3, 7'],
      ['C-004', 'Quote/collateral appraisal → signed Result → policy', 'S-002, S-003', 'Slides 5, 7, 8'],
      ['C-005', 'PCS authority ≠ PCCS cache/transport', 'S-003', 'Slides 2, 6'],
      ['C-007', 'Quote/Result proof limit and extra controls', 'S-002, S-003', 'Slides 4, 8, 9'],
    ];
    const xs = [0.72, 1.78, 7.16, 10.02];
    const ws = [0.82, 5.15, 2.48, 2.42];
    ['Claim', 'Material meaning', 'Canonical source', 'Structural location'].forEach((h, i) => { box(slide, xs[i], 1.65, ws[i], 0.55, C.ink2, C.ink2); text(slide, h, { x: xs[i] + 0.08, y: 1.86, w: ws[i] - 0.16, h: 0.13, fontSize: 8.7, bold: true, color: C.white, align: 'center' }); });
    rows.forEach((row, r) => {
      const y = 2.2 + r * 0.91;
      row.forEach((value, i) => { box(slide, xs[i], y, ws[i], 0.9, r % 2 ? C.paleSlate : C.white, r % 2 ? C.paleSlate : C.white); text(slide, value, { x: xs[i] + 0.11, y: y + 0.31, w: ws[i] - 0.22, h: 0.18, fontSize: i === 1 ? 9.3 : 8.6, color: i === 0 ? C.evidence : C.black, bold: i === 0, align: i === 0 ? 'center' : 'left', fit: 'shrink' }); });
    });
    box(slide, 0.72, 5.9, 12.1, 0.56, C.paleYellow, C.paleYellow);
    text(slide, 'Quick model locator · E-013: Slide 05 / st-e-013 · E-015: Slide 07 / st-e-015 · E-018: Slide 07 / TD endpoint · B-004: Slide 04 · B-006: Slide 07 · N-005/N-006: Slide 05.', { x: 0.92, y: 6.1, w: 11.7, h: 0.12, fontSize: 7.7, color: '8A5600', bold: true, align: 'center', fit: 'shrink' });
    text(slide, 'Canonical locators: S-002 RFC 9334 §§2–4 · S-003 Intel DCAP QuoteGeneration / QuoteVerification / collateral workflow.', { x: 0.95, y: 6.67, w: 11.6, h: 0.12, fontSize: 7.75, color: C.slate, align: 'center', fit: 'shrink' });
    footer(slide, 'Coverage map is the authoritative object-level trace; this slide is the reader-facing ledger.');
  }
  return pptx;
}

const summary = buildSummary();
const structural = buildStructural();
const summaryPath = 'final/summary/intel-tdx-attestation-summary.pptx';
const structuralPath = 'final/structural/intel-tdx-attestation-structural.pptx';
fs.mkdirSync(path.join(root, 'final/summary'), { recursive: true });
fs.mkdirSync(path.join(root, 'final/structural'), { recursive: true });
await summary.writeFile({ fileName: path.join(root, summaryPath) });
await structural.writeFile({ fileName: path.join(root, structuralPath) });

const sourceRefs = Object.fromEntries(input.sources.map((source) => [source.id, { title: source.title, locator: source.locator, canonical_url: source.canonical_url }]));
const coverage = {
  schema_version: 'to-deck.structural-coverage.v1', point_sha256: pointSha, deck: structuralPath,
  coverage: [
    ...input.claims.map((claim, index) => ({ id: claim.id, kind: 'claim', text: claim.text, source_refs: claim.source_refs, qualifiers: claim.qualifiers, proof_limits: claim.proof_limits, coverage_role: 'primary', slide: index === 0 ? 1 : index === 1 ? 3 : index === 2 ? 6 : 9, object_ids: index === 0 ? ['st01-domain-thesis'] : index === 1 ? ['st03-primary-path', 'st07-result-policy'] : index === 2 ? ['st06-collateral-path'] : ['st09-proof-boundary'] })),
    ...input.models.nodes.map((node) => ({ id: node.id, kind: 'model-node', label: node.label, source_refs: node.source_refs, coverage_role: 'primary', slide: ['N-004', 'N-005', 'N-006'].includes(node.id) ? 5 : node.id === 'N-008' ? 6 : node.id === 'N-003' ? 4 : 7, object_ids: [`st-${node.id.toLowerCase()}`] })),
    ...input.models.edges.map((edge) => ({ id: edge.id, kind: 'model-edge', label: edge.label, source_refs: edge.source_refs, coverage_role: 'primary', slide: edge.id === 'E-013' ? 5 : edge.id === 'E-014' ? 6 : edge.id === 'E-015' ? 7 : edge.id === 'E-018' ? 7 : 3, object_ids: [`st-${edge.id.toLowerCase()}`] })),
    ...input.models.boundaries.map((boundary) => ({ id: boundary.id, kind: 'model-boundary', label: boundary.label, source_refs: boundary.source_refs, coverage_role: 'primary', slide: boundary.id === 'B-004' ? 4 : 7, object_ids: [`st-${boundary.id.toLowerCase()}`] })),
    ...input.does_not_prove.map((limit, index) => ({ id: `NP-${String(index + 1).padStart(3, '0')}`, kind: 'does-not-prove', text: limit, source_refs: input.claims.find((claim) => claim.id === 'C-007').source_refs, coverage_role: 'primary', slide: 9, object_ids: [`st09-limit-${index + 1}`] })),
    ...['freshness', 'request/audience binding', 'public-key binding', 'proof of possession', 'authenticated Result', 'one-time atomic state'].map((obligation, index) => ({ id: `O-${String(index + 1).padStart(3, '0')}`, kind: 'deployment-obligation', text: obligation, source_refs: ['S-002', 'S-003'], coverage_role: 'primary', slide: 8, object_ids: [`st08-obligation-${index + 1}`] })),
    ...Object.entries(sourceRefs).map(([id, source]) => ({ id, kind: 'source', ...source, coverage_role: 'source-footer', slide: 11, object_ids: ['st11-source-ledger'] })),
  ],
};
const crosswalk = {
  schema_version: 'to-deck.summary-structural-crosswalk.v1', point_sha256: pointSha,
  summary_deck: summaryPath, structural_deck: structuralPath,
  summary_must_see_ids: ['C-001', 'C-004', 'C-005', 'C-007', 'E-013', 'E-015', 'E-018', 'B-004', 'B-006'],
  deliberate_summary_omissions: ['Detailed PCS/PCCS operating policy', 'all six deployment-obligation details', 'full claim/source ledger', 'complete proof-limit enumeration'],
  crosswalk: [
    { id: 'C-001', summary: { slide: 1, object_id: 'sm01-decision-rail' }, structural: { slide: 1, object_id: 'st01-domain-thesis' } },
    { id: 'C-004', summary: { slide: 1, object_id: 'sm01-verifier-result-policy' }, structural: { slide: 3, object_id: 'st03-primary-path' } },
    { id: 'C-005', summary: { slide: 2, object_id: 'sm02-qgs-tdqe' }, structural: { slide: 6, object_id: 'st06-collateral-path' } },
    { id: 'C-007', summary: { slide: 1, object_id: 'sm01-proof-limit' }, structural: { slide: 9, object_id: 'st09-proof-boundary' } },
    { id: 'E-013', summary: { slide: 2, object_id: 'sm02-evidence-context' }, structural: { slide: 5, object_id: 'st-e-013' } },
    { id: 'E-015', summary: { slide: 1, object_id: 'sm01-signed-result' }, structural: { slide: 7, object_id: 'st-e-015' } },
    { id: 'E-018', summary: { slide: 2, object_id: 'sm02-same-k-channel' }, structural: { slide: 7, object_id: 'st-e-018' } },
    { id: 'B-004', summary: { slide: 1, object_id: 'sm01-evidence-appraisal' }, structural: { slide: 4, object_id: 'st-b-004' } },
    { id: 'B-006', summary: { slide: 1, object_id: 'sm01-policy-action' }, structural: { slide: 7, object_id: 'st-b-006' } },
  ],
  semantic_invariants: ['QGS transport is distinct from TDQE Quote signing', 'PCS authority is distinct from PCCS cache/transport', 'Verifier appraises Evidence; RP/KMS owns release policy', 'Evidence, signed Result, and release action remain distinct', 'failed checks, replay, expiry, and failed PoP produce NO KEY'],
};
const summaryVisualModel = { schema_version: 'to-deck.visual-model.v1', deck: summaryPath, point_sha256: pointSha, objects: crosswalk.crosswalk.map((row) => ({ id: row.summary.object_id, point_ids: [row.id], slide: row.summary.slide })) };
const structuralVisualModel = { schema_version: 'to-deck.visual-model.v1', deck: structuralPath, point_sha256: pointSha, objects: coverage.coverage.map((row) => ({ id: row.object_ids[0], point_ids: [row.id], slide: row.slide, coverage_role: row.coverage_role })) };
saveJson('final/structural-coverage-map.json', coverage);
saveJson('final/summary-structural-crosswalk.json', crosswalk);
saveJson('final/summary/visual-model.json', summaryVisualModel);
saveJson('final/structural/visual-model.json', structuralVisualModel);
saveJson('final/build-provenance.json', { schema_version: 'to-deck.paired-build.v1', point_sha256: pointSha, summary: summaryPath, structural: structuralPath, summary_slide_count: 2, structural_slide_count: 11, source_inputs: ['input/to-site.input.json', 'input/point-result.md'] });
console.log(JSON.stringify({ summary: summaryPath, structural: structuralPath, point_sha256: pointSha, structural_coverage_count: coverage.coverage.length }, null, 2));

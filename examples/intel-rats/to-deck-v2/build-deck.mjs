import fs from 'node:fs';
import path from 'node:path';
import PptxGenJS from 'pptxgenjs';

const pptx = new PptxGenJS();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = 'Bitboom';
pptx.company = 'Bitboom';
pptx.subject = 'Intel TDX remote attestation decision model and signed Result sequence';
pptx.title = 'Intel TDX 원격 증명 — 결정 모델과 sequence';
pptx.lang = 'ko-KR';
pptx.theme = {
  headFontFace: 'Apple SD Gothic Neo',
  bodyFontFace: 'Apple SD Gothic Neo',
  lang: 'ko-KR',
};
pptx.defineLayout({ name: 'WIDE', width: 13.333, height: 7.5 });
pptx.layout = 'WIDE';
pptx.margin = 0;
pptx.layout = 'WIDE';
pptx.subject = 'Decision-first technical briefing';

const S = pptx.ShapeType;
const C = {
  ink: '071827',
  ink2: '102A43',
  panel: '0E2236',
  paper: 'F7F9FC',
  slate: '45627D',
  muted: '9DB3C8',
  line: 'B6C7D8',
  evidence: '0E7490',
  decision: '175CD3',
  allow: '15803D',
  deny: 'B42318',
  white: 'FFFFFF',
  black: '102033',
  paleBlue: 'E9F4FB',
  paleGreen: 'EAF7EF',
  paleRed: 'FFF0EF',
  paleYellow: 'FFF8E5',
};

function text(slide, value, options) {
  slide.addText(value, { fontFace: 'Apple SD Gothic Neo', margin: 0, breakLine: false, ...options });
}

function rect(slide, x, y, w, h, fill, line = fill) {
  slide.addShape(S.rect, { x, y, w, h, fill: { color: fill }, line: { color: line, width: 0.7 } });
}

function arrow(slide, x1, y1, x2, y2, color, width = 1.8, dash = undefined) {
  slide.addShape(S.line, {
    x: x1,
    y: y1,
    w: x2 - x1,
    h: y2 - y1,
    line: { color, width, beginArrowType: 'none', endArrowType: 'triangle', dashType: dash },
  });
}

function label(slide, value, x, y, w, color = C.muted) {
  text(slide, value, { x, y, w, h: 0.22, fontSize: 9.5, color, bold: true, align: 'center', valign: 'mid' });
}

function stageCard(slide, { x, y, w, h, step, title, body, tint, color = C.white }) {
  rect(slide, x, y, w, h, tint, tint);
  text(slide, step, { x: x + 0.16, y: y + 0.14, w: 0.36, h: 0.2, fontSize: 10, bold: true, color });
  text(slide, title, { x: x + 0.16, y: y + 0.42, w: w - 0.32, h: 0.34, fontSize: 18, bold: true, color, valign: 'mid' });
  text(slide, body, { x: x + 0.16, y: y + 0.84, w: w - 0.32, h: h - 1.0, fontSize: 12.5, color, breakLine: false, valign: 'mid', fit: 'shrink' });
}

function footer(slide, textValue, dark = true) {
  text(slide, textValue, { x: 0.55, y: 7.08, w: 12.2, h: 0.16, fontSize: 7.5, color: dark ? C.muted : C.slate, align: 'left' });
  text(slide, 'Intel-rats는 교육용 lens이며 배포형 Quote verifier가 아니다.', { x: 7.0, y: 7.08, w: 5.75, h: 0.16, fontSize: 7.5, color: dark ? C.muted : C.slate, align: 'right' });
}

// Slide 1 — decision model
{
  const slide = pptx.addSlide();
  slide.background = { color: C.ink };
  text(slide, '검증은 증거를 판정하고, 공개는 정책이 결정한다', {
    x: 0.55, y: 0.35, w: 12.1, h: 0.45, fontSize: 27, bold: true, color: C.white,
  });
  text(slide, '유효한 Quote는 자동 권한 부여가 아니다. signed Result는 RP/KMS release policy의 입력이다.', {
    x: 0.57, y: 0.92, w: 11.9, h: 0.3, fontSize: 14.5, color: C.muted,
  });

  // Collateral is a side input instead of a competing main rail.
  rect(slide, 3.12, 1.34, 3.15, 0.38, C.ink2, C.ink2);
  text(slide, 'Intel PCS  →  PCCS cache  →  signed collateral', {
    x: 3.28, y: 1.425, w: 2.82, h: 0.14, fontSize: 9.5, color: '9ED8EB', align: 'center', bold: true,
  });
  arrow(slide, 5.3, 1.72, 5.3, 1.98, C.evidence, 1.2, 'dash');
  label(slide, 'PCCS는 authority가 아니라 cache / transport', 3.05, 1.73, 4.45, '9ED8EB');

  stageCard(slide, {
    x: 0.6, y: 2.1, w: 2.4, h: 2.25, step: '01', title: 'EVIDENCE',
    body: 'TD Quote + canonical key bytes + bound request context', tint: '12334A',
  });
  stageCard(slide, {
    x: 3.45, y: 1.98, w: 2.65, h: 2.55, step: '02', title: 'VERIFIER',
    body: 'Quote·collateral 평가\nK / D / E 재계산\nsigned Result 생성', tint: C.evidence,
  });
  stageCard(slide, {
    x: 7.15, y: 1.98, w: 2.65, h: 2.55, step: '03', title: 'RP / KMS',
    body: 'Result + time + E/K 확인\nPoP 확인\n별도 release policy', tint: C.decision,
  });

  arrow(slide, 3.02, 3.22, 3.44, 3.22, '80CFE5', 2.2);
  label(slide, 'Quote + context', 2.78, 2.88, 0.95, 'BCEAF7');
  arrow(slide, 6.12, 3.22, 7.14, 3.22, '75C1FF', 2.6);
  label(slide, 'signed Result', 6.05, 2.88, 1.18, 'A9D8FF');

  rect(slide, 10.35, 2.25, 2.25, 0.82, C.allow, C.allow);
  text(slide, 'ALLOW', { x: 10.6, y: 2.45, w: 0.95, h: 0.2, fontSize: 18, bold: true, color: C.white, align: 'center' });
  text(slide, 'one-time secret', { x: 10.55, y: 2.76, w: 1.15, h: 0.13, fontSize: 8.5, color: 'D8F5E2', align: 'center' });
  rect(slide, 10.35, 3.5, 2.25, 0.82, C.deny, C.deny);
  text(slide, 'NO KEY', { x: 10.55, y: 3.7, w: 1.2, h: 0.2, fontSize: 18, bold: true, color: C.white, align: 'center' });
  text(slide, 'deny · replay · expiry', { x: 10.45, y: 4.01, w: 1.42, h: 0.13, fontSize: 8.5, color: 'FFE1DE', align: 'center' });
  arrow(slide, 9.82, 2.82, 10.34, 2.66, C.allow, 2.0);
  arrow(slide, 9.82, 3.7, 10.34, 3.9, C.deny, 2.0);

  rect(slide, 0.6, 5.1, 5.82, 1.18, '0B3140', '0B3140');
  text(slide, '이 경로가 증명하는 것', { x: 0.86, y: 5.36, w: 2.05, h: 0.22, fontSize: 14, bold: true, color: 'A4E9F7' });
  text(slide, 'reported TD state + request/key binding을\n조직 policy로 평가할 수 있다.', { x: 0.86, y: 5.69, w: 4.9, h: 0.32, fontSize: 13, color: C.white, fit: 'shrink' });
  rect(slide, 6.62, 5.1, 5.98, 1.18, '3B1C27', '3B1C27');
  text(slide, '이 경로만으로는 증명하지 않는 것', { x: 6.88, y: 5.36, w: 3.25, h: 0.22, fontSize: 14, bold: true, color: 'FFC1B8' });
  text(slide, 'code correctness · container identity · future safety · availability', { x: 6.88, y: 5.75, w: 5.3, h: 0.16, fontSize: 12.5, color: C.white, fit: 'shrink' });
  footer(slide, 'Sources: RFC 9334; Intel SGX Data Center Attestation Primitives.  Decision model from passed Intel-rats Point.');
}

// Slide 2 — protocol sequence
{
  const slide = pptx.addSlide();
  slide.background = { color: C.paper };
  text(slide, 'signed Result는 어떻게 만들어지는가', {
    x: 0.55, y: 0.33, w: 8.4, h: 0.42, fontSize: 26, bold: true, color: C.black,
  });
  text(slide, 'actor는 한 번만 놓고, 각 화살표에는 하나의 artifact/message만 둔다.', {
    x: 0.57, y: 0.88, w: 8.8, h: 0.25, fontSize: 14, color: C.slate,
  });

  const lanes = [
    { x: 0.58, label: 'RP / KMS', sub: 'release owner', color: C.decision },
    { x: 3.05, label: 'Verifier', sub: 'appraisal owner', color: C.evidence },
    { x: 5.52, label: 'TD', sub: 'attester', color: '315B86' },
    { x: 7.99, label: 'QGS', sub: 'transport only', color: '64748B' },
    { x: 10.46, label: 'TDQE', sub: 'Quote signer', color: '7C3AED' },
  ];
  for (const lane of lanes) {
    rect(slide, lane.x, 1.42, 2.05, 0.65, lane.color, lane.color);
    text(slide, lane.label, { x: lane.x, y: 1.58, w: 2.05, h: 0.18, fontSize: 15, bold: true, color: C.white, align: 'center' });
    text(slide, lane.sub, { x: lane.x, y: 1.83, w: 2.05, h: 0.12, fontSize: 8.5, color: 'E9F2F8', align: 'center' });
    slide.addShape(S.line, { x: lane.x + 1.025, y: 2.1, w: 0, h: 4.0, line: { color: 'B7C8D7', width: 0.7, dash: 'dash' } });
  }

  text(slide, '01  Bind', { x: 0.58, y: 2.2, w: 1.0, h: 0.16, fontSize: 10, bold: true, color: C.slate });
  arrow(slide, 1.6, 2.5, 4.08, 2.5, C.decision, 1.8);
  label(slide, 'request ID + subject + audience', 1.75, 2.26, 2.2, C.decision);
  arrow(slide, 4.08, 2.83, 1.6, 2.83, C.evidence, 1.8);
  label(slide, 'nonce (Verifier retains context)', 1.72, 2.59, 2.24, C.evidence);
  arrow(slide, 1.6, 3.16, 6.55, 3.16, C.decision, 1.8);
  label(slide, 'RP forwards nonce + bound request context', 2.18, 2.92, 3.85, C.decision);

  text(slide, '02  Quote', { x: 0.58, y: 3.45, w: 1.0, h: 0.16, fontSize: 10, bold: true, color: C.slate });
  arrow(slide, 6.55, 3.78, 9.02, 3.78, '315B86', 1.8);
  label(slide, 'TDREPORT: D/K', 6.92, 3.54, 1.65, '315B86');
  arrow(slide, 9.02, 4.12, 11.49, 4.12, '64748B', 1.8);
  label(slide, 'same-platform report', 9.1, 3.88, 2.18, '64748B');
  arrow(slide, 11.49, 4.46, 9.02, 4.46, '7C3AED', 1.8);
  label(slide, 'TDQE-signed Quote', 9.25, 4.22, 2.0, '7C3AED');
  arrow(slide, 9.02, 4.8, 6.55, 4.8, '64748B', 1.8);
  label(slide, 'Quote returns through guest path', 6.72, 4.56, 2.18, '64748B');
  arrow(slide, 6.55, 5.12, 1.6, 5.12, '315B86', 1.8);
  label(slide, 'exact Quote + canonical key bytes', 1.95, 4.88, 4.1, '315B86');
  arrow(slide, 1.6, 5.44, 4.08, 5.44, C.evidence, 1.8);
  label(slide, 'Evidence + key + identical context', 1.72, 5.2, 2.28, C.evidence);

  text(slide, '03  Appraise', { x: 0.58, y: 5.67, w: 0.9, h: 0.16, fontSize: 8.5, bold: true, color: C.slate, fit: 'shrink' });
  rect(slide, 8.55, 5.47, 3.95, 0.39, C.paleBlue, C.paleBlue);
  text(slide, 'Collateral side path: Intel PCS → PCCS → Verifier validates signature / status / freshness', { x: 8.7, y: 5.59, w: 3.62, h: 0.1, fontSize: 7.9, color: C.evidence, bold: true, align: 'center', fit: 'shrink' });
  arrow(slide, 4.08, 5.93, 1.6, 5.93, C.evidence, 2.3);
  label(slide, 'signed Result: verdict + policy version + E + allow-only K', 1.64, 5.68, 2.38, C.evidence);
  arrow(slide, 1.6, 6.31, 6.55, 6.31, C.allow, 1.8);
  label(slide, 'PoP challenge / response → secret only on same approved K channel', 2.05, 6.06, 4.15, C.allow);
  rect(slide, 10.45, 6.03, 2.05, 0.5, C.paleRed, C.paleRed);
  text(slide, 'DENY / REPLAY / EXPIRY → NO KEY', { x: 10.59, y: 6.2, w: 1.76, h: 0.1, fontSize: 8.4, bold: true, color: C.deny, align: 'center', fit: 'shrink' });

  footer(slide, 'Main sequence: passed Intel-rats Point C-004/C-005/C-006.  PCCS is a collateral cache, not the signing authority.', false);
}

const output = path.resolve('final/intel-tdx-attestation-v2.pptx');
fs.mkdirSync(path.dirname(output), { recursive: true });
await pptx.writeFile({ fileName: output });
console.log(output);

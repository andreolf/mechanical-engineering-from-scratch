// Compiles content/lessons/**/*.md into site/public/lessons/<phase>.json (HTML with KaTeX pre-rendered,
// highlighted code, exercises, quizzes) and copies code files to site/public/code/ for download.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { marked } from 'marked';
import katex from 'katex';
import hljs from 'highlight.js/lib/core';
import python from 'highlight.js/lib/languages/python';
hljs.registerLanguage('python', python);

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '../..');
const CONTENT = path.join(ROOT, 'content/lessons');
const TESTS = path.join(ROOT, 'content/tests');
const OUT = path.join(ROOT, 'site/public/lessons');
const CODE_OUT = path.join(ROOT, 'site/public/code');
const curriculum = JSON.parse(fs.readFileSync(path.join(ROOT, 'curriculum/curriculum.json'), 'utf8'));
const syllabus = new Map(curriculum.phases.flatMap((p) => p.lessons.map((l) => [l.id, { ...l, phase: p.id }])));

marked.setOptions({ gfm: true, breaks: false });
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const slug = (s) => s.toLowerCase().replace(/<[^>]+>/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

function tex(src, display, where) {
  try {
    return katex.renderToString(src, { displayMode: display, throwOnError: true, strict: 'ignore', output: 'html' });
  } catch (e) { throw new Error(`KaTeX error in ${where}: ${e.message}\n  in: ${src}`); }
}

// Markdown with $inline$ and $$display$$ math. Code spans are protected from math parsing.
function md(text, where, inline = false) {
  const keep = [];
  const hold = (html) => `@@K${keep.push(html) - 1}@@`;
  let t = text.replace(/`[^`\n]+`/g, (m) => hold(marked.parseInline(m)));
  t = t.replace(/\$\$([\s\S]+?)\$\$/g, (_, m) => `\n\n@@D${keep.push(`<div class="math-display" tabindex="0">${tex(m.trim(), true, where)}</div>`) - 1}@@\n\n`);
  t = t.replace(/(^|[^\\$])\$([^$\n]+?)\$/g, (_, pre, m) => pre + hold(tex(m, false, where)));
  t = t.replace(/\\\$/g, '$');
  // typography: apostrophes and double quotes become curly (skipped when a chunk carries raw HTML)
  t = t.replace(/(\w)'(\w)/g, '$1\u2019$2');
  if (!/<[a-z]/i.test(t)) t = t.replace(/"([^"\n]+)"/g, '\u201c$1\u201d');
  t = t.replace(/\.\.\./g, '\u2026');
  let html = inline ? marked.parseInline(t) : marked.parse(t);
  html = html.replace(/<p>\s*@@D(\d+)@@\s*<\/p>/g, (_, i) => keep[+i]);
  html = html.replace(/@@[KD](\d+)@@/g, (_, i) => keep[+i]);
  return html;
}

function codePanel(info, code, ctx) {
  const file = (info.match(/file=([\w.\-]+)/) || [])[1] || `${ctx.id.replace('.', '_')}_snippet.py`;
  const lang = info.split(/\s+/)[0] || 'python';
  const hl = lang === 'python' ? hljs.highlight(code, { language: 'python' }).value : esc(code);
  let url = null;
  if (/file=/.test(info)) {
    const name = `${ctx.id.replace('.', '-')}-${file}`;
    fs.writeFileSync(path.join(CODE_OUT, name), code.endsWith('\n') ? code : code + '\n');
    url = `code/${name}`;
    ctx.code.push({ file, url });
  }
  const lines = code.split('\n').length;
  return `<figure class="code" data-lines="${lines}"><figcaption><span class="code-file">${esc(file)}</span><span class="code-actions"><button type="button" class="btn-small" data-copy-code>Copy</button>${url ? `<a class="btn-small" href="${url}" download="${esc(file)}">Download</a>` : ''}</span></figcaption><pre tabindex="0"><code class="language-${lang}">${hl}</code></pre></figure>`;
}

function renderQuiz(json, ctx) {
  let items;
  try { items = JSON.parse(json); } catch (e) { throw new Error(`Bad quiz JSON in ${ctx.id}: ${e.message}`); }
  return items.map((q, i) => {
    const out = { type: q.type, q: md(q.q, `${ctx.id} quiz ${i}`, true), explain: md(q.explain || '', `${ctx.id} quiz ${i}`, true) };
    if (q.type === 'mc') {
      if (!Array.isArray(q.options) || q.answer == null || q.answer >= q.options.length) throw new Error(`MC quiz ${ctx.id}#${i} malformed`);
      out.options = q.options.map((o) => md(String(o), `${ctx.id} quiz ${i}`, true));
      out.answer = q.answer;
    } else if (q.type === 'num') {
      if (typeof q.answer !== 'number') throw new Error(`Numeric quiz ${ctx.id}#${i} needs numeric answer`);
      Object.assign(out, { answer: q.answer, tol: q.tol ?? 0.02, unit: q.unit || '', py: q.py || null });
    } else throw new Error(`Unknown quiz type ${q.type} in ${ctx.id}`);
    return out;
  });
}

function compile(src, file) {
  const fm = src.match(/^---\n([\s\S]*?)\n---\n/);
  if (!fm) throw new Error(`${file}: missing front matter`);
  const meta = Object.fromEntries(fm[1].split('\n').filter(Boolean).map((l) => { const i = l.indexOf(':'); return [l.slice(0, i).trim(), l.slice(i + 1).trim()]; }));
  const ctx = { id: meta.id, code: [], quiz: [] };
  if (!syllabus.has(ctx.id)) throw new Error(`${file}: id ${ctx.id} not in curriculum`);
  let body = src.slice(fm[0].length);
  // 1) fenced code blocks
  const blocks = [];
  body = body.replace(/^```([^\n]*)\n([\s\S]*?)\n```\s*$/gm, (_, info, code) => {
    if (info.trim() === 'quiz') { ctx.quiz.push(...renderQuiz(code, ctx)); return ''; }
    return `\n@@B${blocks.push(codePanel(info.trim(), code, ctx)) - 1}@@\n`;
  });
  // 2) containers
  const sections = [];
  const renderChunk = (text) => {
    let html = md(text, file);
    html = html.replace(/<p>@@B(\d+)@@<\/p>/g, (_, i) => blocks[+i]).replace(/@@B(\d+)@@/g, (_, i) => blocks[+i]);
    html = html.replace(/<h2>(.*?)<\/h2>/g, (_, h) => { const id = slug(h); sections.push({ id, title: h.replace(/<[^>]+>/g, '') }); return `<h2 id="${id}">${h}</h2>`; });
    return html;
  };
  let exN = 0;
  const parts = body.split(/^:::(\w+)([^\n]*)\n([\s\S]*?)^:::\s*$/m);
  let html = '';
  for (let i = 0; i < parts.length; i += 4) {
    html += renderChunk(parts[i]);
    if (i + 1 >= parts.length) break;
    const [kind, argRaw, inner] = [parts[i + 1], parts[i + 2].trim(), parts[i + 3]];
    if (kind === 'example') html += `<section class="example"><h3><span class="tag">Worked example</span>${md(argRaw, file, true)}</h3>${renderChunk(inner)}</section>`;
    else if (kind === 'note') html += `<aside class="note">${argRaw ? `<p class="note-title">${md(argRaw, file, true)}</p>` : ''}${renderChunk(inner)}</aside>`;
    else if (kind === 'exercise') {
      exN++;
      const [prob, sol] = inner.split(/^---solution---\s*$/m);
      if (!sol) throw new Error(`${file}: exercise without ---solution---`);
      html += `<section class="exercise"><h3><span class="tag">Exercise ${exN}</span>${md(argRaw, file, true)}</h3>${renderChunk(prob)}<details class="solution"><summary>Show step-by-step solution</summary>${renderChunk(sol)}</details></section>`;
    } else if (kind === 'figure') {
      const [art, cap = ''] = inner.split(/^Caption:\s*/m);
      html += `<figure class="fig">${art.trim()}<figcaption>${md(cap.trim(), file, true)}</figcaption></figure>`;
    } else if (kind === 'widget') {
      const [name, ...rest] = argRaw.split(/\s+/);
      html += `<figure class="fig widget-fig"><div class="widget" data-widget="${esc(name)}" data-args="${esc(rest.join(' '))}"></div><figcaption>${md(inner.trim(), file, true)}</figcaption></figure>`;
    } else throw new Error(`${file}: unknown container ${kind}`);
  }
  if (ctx.quiz.length < 3) throw new Error(`${file}: needs at least 3 quiz questions`);
  if (!exN) throw new Error(`${file}: needs at least one exercise`);
  if (!ctx.code.length) throw new Error(`${file}: needs a downloadable code file`);
  if (!/class="example"/.test(html)) throw new Error(`${file}: needs a worked example`);
  const words = src.replace(/```[\s\S]*?```/g, '').split(/\s+/).length;
  return { id: ctx.id, title: meta.title || syllabus.get(ctx.id).title, minutes: +meta.minutes || Math.round(words / 160) + 10, html, sections, quiz: ctx.quiz, code: ctx.code, words };
}

fs.mkdirSync(OUT, { recursive: true });
fs.rmSync(CODE_OUT, { recursive: true, force: true });
fs.mkdirSync(CODE_OUT, { recursive: true });
const byPhase = {};
const files = fs.existsSync(CONTENT) ? fs.readdirSync(CONTENT, { recursive: true }).filter((f) => f.endsWith('.md')).sort() : [];
for (const f of files) {
  const l = compile(fs.readFileSync(path.join(CONTENT, f), 'utf8'), f);
  const ph = syllabus.get(l.id).phase;
  (byPhase[ph] ||= { phase: ph, lessons: {}, tests: [] }).lessons[l.id] = l;
}
for (const ph of Object.keys(byPhase)) {
  const tf = path.join(TESTS, `${ph}.json`);
  if (fs.existsSync(tf)) byPhase[ph].tests = renderQuiz(fs.readFileSync(tf, 'utf8'), { id: `test-${ph}` });
  fs.writeFileSync(path.join(OUT, `${ph}.json`), JSON.stringify(byPhase[ph]));
}
const index = { generated: new Date().toISOString(), written: Object.values(byPhase).flatMap((p) => Object.keys(p.lessons)).sort(),
  phases: Object.fromEntries(Object.entries(byPhase).map(([k, v]) => [k, { written: Object.keys(v.lessons).length, tests: v.tests.length }])) };
fs.writeFileSync(path.join(OUT, 'index.json'), JSON.stringify(index, null, 1));
console.log(`lessons: ${index.written.length} written across ${Object.keys(byPhase).length} phase(s)`);

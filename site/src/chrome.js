// Shared navigation and footer, rendered into both pages so they stay identical.
import { load, level } from './store.js';

export const REPO = 'https://github.com/andreolf/mechanical-engineering-from-scratch';
export const MARK = `<svg class="brand-mark" viewBox="0 0 32 32" aria-hidden="true"><rect x="3" y="5" width="5" height="22" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M3 9l5-4M3 14l5-4M3 19l5-4M3 24l5-4" stroke="currentColor" stroke-width="1.1"/><path d="M8 13h21v4H8z" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M8 15c7 0 14 1.2 21 4.6" fill="none" stroke="#eeff41" stroke-width="2"/></svg>`;

export function renderNav(page) {
  const host = document.getElementById('site-nav');
  if (!host) return;
  const home = page === 'home' ? '' : 'index.html';
  const s = load();
  host.className = 'nav';
  host.innerHTML = `<div class="wrap">
    <a class="brand" href="${home || './'}" aria-label="Mechanical Engineering from Scratch, home">${MARK}<span>ME from Scratch</span><small>free course</small></a>
    <nav class="nav-links" aria-label="Main">
      <a href="learn.html#/course" ${page === 'course' ? 'aria-current="page"' : ''}>Course</a>
      <a class="hide-s" href="${home}#labs">Labs</a>
      <a class="hide-xs" href="learn.html#/progress" ${page === 'progress' ? 'aria-current="page"' : ''}>Progress</a>
      <a class="xp-link" href="learn.html#/progress" aria-label="${s.xp} experience points, level ${level(s.xp).level}. Your progress"><span class="xp-chip"><i aria-hidden="true"></i><span class="num" data-xp>${s.xp}</span> XP</span></a>
    </nav></div>`;
}

export function refreshXp() {
  const s = load();
  document.querySelectorAll('[data-xp]').forEach((e) => (e.textContent = s.xp));
}

export function renderFooter(page) {
  const host = document.getElementById('site-footer');
  if (!host) return;
  const home = page === 'home' ? '' : 'index.html';
  host.className = 'footer';
  host.innerHTML = `<div class="wrap">
    <div class="footer-grid">
      <div class="footer-about">
        <a class="brand" href="${home || './'}">${MARK}<span>Mechanical Engineering from Scratch</span></a>
        <p>A free course from Analysis 1 to your own finite-element and CFD solvers. In every lesson you derive the model, code it, and test it.</p>
        <p>Made by Francesco Andreoli, mechanical engineering alumnus of ETH Zurich.</p>
      </div>
      <div><h2>Course</h2><ul>
        <li><a href="learn.html#/00.01">Start with lesson 00.01</a></li>
        <li><a href="learn.html#/course">All phases and lessons</a></li>
        <li><a href="learn.html#/progress">Your progress</a></li>
        <li><a href="learn.html#/verify">Verify a certificate</a></li></ul></div>
      <div><h2>Labs</h2><ul>
        <li><a href="${home}#lab-truss">Break the bridge</a></li>
        <li><a href="${home}#lab-flywheel">Spinning flywheel</a></li>
        <li><a href="${home}#lab-pipe">Choke the pipe</a></li>
        <li><a href="https://andreolf.github.io/coconut-lab/" rel="noopener">Coconut eddy</a></li>
        <li><a href="https://andreolf.github.io/subak-lab/" rel="noopener">Subak terraces</a></li></ul></div>
      <div><h2>Project</h2><ul>
        <li><a href="${REPO}" rel="noopener">Source on GitHub</a></li>
        <li><a href="${REPO}/issues" rel="noopener">Report a mistake</a></li>
        <li><a href="${REPO}/blob/main/LICENSE" rel="noopener">MIT license</a></li></ul></div>
      <div data-testid="more-courses"><h2>More courses</h2><ul>
        <li><a href="https://andreolf.github.io/ai-safety-from-scratch/" rel="noopener">AI Safety from Scratch</a></li>
        <li><a href="https://andreolf.github.io/security-from-scratch/" rel="noopener">Security from Scratch</a></li></ul></div>
      <div><h2>Francesco</h2><ul>
        <li><a href="https://x.com/francescoswiss" rel="noopener">X @francescoswiss</a></li>
        <li><a href="https://www.youtube.com/@swissintech" rel="noopener">YouTube @swissintech</a></li>
        <li><a href="https://github.com/andreolf" rel="noopener">GitHub @andreolf</a></li></ul></div>
    </div>
    <div class="footer-legal">
      <p>Free and open source under the MIT license. No accounts and no tracking: your progress is stored in this browser only.</p>
      <p>Certificates are free certificates of completion, not accredited qualifications. This project is not affiliated with or endorsed by ETH Zurich; ETH course names are given for orientation only.</p>
      <p>Simulations are simplified teaching models. Don't use them to design real structures.</p>
    </div>
  </div>`;
}

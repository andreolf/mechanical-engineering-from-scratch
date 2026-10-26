(function(){let e=document.createElement(`link`).relList;if(e&&e.supports&&e.supports(`modulepreload`))return;for(let e of document.querySelectorAll(`link[rel="modulepreload"]`))n(e);new MutationObserver(e=>{for(let t of e)if(t.type===`childList`)for(let e of t.addedNodes)e.tagName===`LINK`&&e.rel===`modulepreload`&&n(e)}).observe(document,{childList:!0,subtree:!0});function t(e){let t={};return e.integrity&&(t.integrity=e.integrity),e.referrerPolicy&&(t.referrerPolicy=e.referrerPolicy),t.credentials=e.crossOrigin===`use-credentials`?`include`:e.crossOrigin===`anonymous`?`omit`:`same-origin`,t}function n(e){if(e.ep)return;e.ep=!0;let n=t(e);fetch(e.href,n)}})();var e=`mefs.v2`,t=`mefs.progress.v1`,n={lesson:50,quizCorrect:10,test:200},r=.8,i=(e=new Date)=>new Date(e.getTime()-e.getTimezoneOffset()*6e4).toISOString().slice(0,10);function a(){return{v:2,lessons:{},tests:{},xp:0,days:[],name:``,certs:{}}}function o(){let n;try{n=JSON.parse(localStorage.getItem(e)||`null`)}catch{n=null}if(!n||n.v!==2){n=a();try{let e=JSON.parse(localStorage.getItem(t)||`[]`);for(let t of e)n.lessons[t]={done:!0,at:i()}}catch{}}return n}function s(t){try{localStorage.setItem(e,JSON.stringify(t))}catch{}}function c(e){let t=i();e.days.includes(t)||e.days.push(t)}function l(e,t,r=!0){let a=e.lessons[t]||={};r&&!a.done&&(a.done=!0,a.at=i(),e.xp+=n.lesson,c(e)),!r&&a.done&&(a.done=!1,e.xp=Math.max(0,e.xp-n.lesson)),s(e)}function u(e,t,r,i){let a=e.lessons[t]||={},o=a.quizBest||0;a.quizBest=Math.max(o,r),a.quizTotal=i,a.quizAttempts=(a.quizAttempts||0)+1,e.xp+=n.quizCorrect*Math.max(0,r-o),c(e),s(e)}function d(e,t,r,a){let o=e.tests[t]||={best:0,attempts:0};o.attempts++;let l=r/a,u=l>=.8&&!o.passedAt;return o.best=Math.max(o.best,l),u&&(o.passedAt=i(),e.xp+=n.test),c(e),s(e),u}function f(e){let t=new Set(e.days),n=0,r=new Date;for(t.has(i(r))||r.setDate(r.getDate()-1);t.has(i(r));)n++,r.setDate(r.getDate()-1);let a=0,o=0,s=null;for(let e of[...t].sort()){let t=new Date(e+`T12:00:00`);o=s&&(t-s)/864e5<1.5?o+1:1,a=Math.max(a,o),s=t}return{current:n,best:a}}function p(e){let t=0;for(;250*(t+1)*(t+2)/2<=e;)t++;let n=250*t*(t+1)/2,r=250*(t+1)*(t+2)/2;return{level:t+1,into:e-n,span:r-n}}function m(e,t){return t.filter(t=>e.lessons[t]?.done).length}var h=e=>String(e).replace(/[&<>"']/g,e=>({"&":`&amp;`,"<":`&lt;`,">":`&gt;`,'"':`&quot;`,"'":`&#39;`})[e]);function g(e,t,n,{linkBase:r=`learn.html`}={}){let i=o(),a=new Set(n.written||[]);e.innerHTML=`
    <div class="map-tools">
      <label class="search"><span class="sr-only">Search lessons</span>
        <input id="lesson-search" type="search" name="lesson-search" autocomplete="off" spellcheck="false" placeholder="Search lessons, for example Bernoulli…" /></label>
      <p class="map-stats small muted num" id="progress-stats"><span data-k="done">${m(i,t.phases.flatMap(e=>e.lessons.map(e=>e.id)))}</span> of ${t.lessonCount} lessons done</p>
    </div>
    <p id="search-count" class="small muted" aria-live="polite"></p>
    <ol class="phases">${t.phases.map(e=>{let t=e.lessons.map(e=>e.id),n=t.filter(e=>a.has(e)).length,o=m(i,t),s=n===t.length?`Full lessons`:n?`${n} of ${t.length} written`:`Outline`;return`<li class="phase" id="phase-${e.id}" data-phase="${e.id}">
        <button type="button" class="phase-head" aria-expanded="false" aria-controls="phase-body-${e.id}">
          <span class="phase-num num">${e.id}</span>
          <span class="phase-title"><strong>${h(e.title)}</strong><span class="phase-sub">${h(e.de)}</span></span>
          <span class="phase-meta"><span class="pill ${n===t.length?`pill-on`:n?`pill-part`:``}">${s}</span><span class="phase-count num">${o?`${o}/${t.length} done`:`${t.length} lessons`}</span></span>
          <span class="chev" aria-hidden="true"></span>
        </button>
        <div class="phase-body" id="phase-body-${e.id}" hidden>
          <p class="phase-summary">${h(e.summary)}</p>
          <p class="phase-eth small muted">Mirrors: ${h(e.eth)}${e.ethNamed?``:` (generic description)`}. Anchors: ${h(e.anchor)}.</p>
          <ol class="lesson-list">${e.lessons.map(e=>`
            <li class="lesson-item" data-id="${e.id}" data-text="${h((e.id+` `+e.title+` `+e.goal+` `+e.tool+` `+e.lab+` `+e.math).toLowerCase())}">
              <a href="${r}#/${e.id}"><span class="lid num">${e.id}</span><span class="lt">${h(e.title)}</span>
              <span class="ls">${i.lessons[e.id]?.done?`<span class="dot dot-done" title="Done"></span><span class="sr-only">Done</span>`:a.has(e.id)?`<span class="tag-full">Full lesson</span>`:`<span class="tag-outline">Outline</span>`}</span></a>
            </li>`).join(``)}
          </ol>
          ${n?`<p class="phase-actions"><a class="btn-small" href="${r}#/test/${e.id}">Phase ${e.id} test</a></p>`:``}
        </div>
      </li>`}).join(``)}
    </ol>`;let s=(e,t)=>{e.classList.toggle(`open`,t),e.querySelector(`.phase-head`).setAttribute(`aria-expanded`,String(t)),e.querySelector(`.phase-body`).hidden=!t};e.addEventListener(`click`,e=>{let t=e.target.closest(`.phase-head`);if(t){let e=t.closest(`.phase`);s(e,!e.classList.contains(`open`))}});let c=e.querySelector(`#lesson-search`),l=e.querySelector(`#search-count`),u;c.addEventListener(`input`,()=>{clearTimeout(u),u=setTimeout(()=>{let t=c.value.trim().toLowerCase(),n=0;e.querySelectorAll(`.phase`).forEach(e=>{let r=0;e.querySelectorAll(`.lesson-item`).forEach(e=>{let n=!t||e.dataset.text.includes(t);e.hidden=!n,n&&r++}),n+=t?r:0,e.hidden=!!t&&r===0,s(e,!!t&&r>0)}),l.textContent=t?`${n} ${n===1?`lesson matches`:`lessons match`} “${c.value.trim()}”`:``},120)})}var _=`https://github.com/andreolf/mechanical-engineering-from-scratch`,v=`<svg class="brand-mark" viewBox="0 0 32 32" aria-hidden="true"><rect x="3" y="5" width="5" height="22" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M3 9l5-4M3 14l5-4M3 19l5-4M3 24l5-4" stroke="currentColor" stroke-width="1.1"/><path d="M8 13h21v4H8z" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M8 15c7 0 14 1.2 21 4.6" fill="none" stroke="#eeff41" stroke-width="2"/></svg>`;function y(e){let t=document.getElementById(`site-nav`);if(!t)return;let n=e===`home`?``:`index.html`,r=o();t.className=`nav`,t.innerHTML=`<div class="wrap">
    <a class="brand" href="${n||`./`}" aria-label="Mechanical Engineering from Scratch, home">${v}<span>ME from Scratch</span><small>free course</small></a>
    <nav class="nav-links" aria-label="Main">
      <a href="learn.html#/course" ${e===`course`?`aria-current="page"`:``}>Course</a>
      <a class="hide-s" href="${n}#labs">Labs</a>
      <a class="hide-xs" href="learn.html#/progress" ${e===`progress`?`aria-current="page"`:``}>Progress</a>
      <a class="xp-link" href="learn.html#/progress" aria-label="${r.xp} experience points, level ${p(r.xp).level}. Your progress"><span class="xp-chip"><i aria-hidden="true"></i><span class="num" data-xp>${r.xp}</span> XP</span></a>
    </nav></div>`}function b(){let e=o();document.querySelectorAll(`[data-xp]`).forEach(t=>t.textContent=e.xp)}function x(e){let t=document.getElementById(`site-footer`);if(!t)return;let n=e===`home`?``:`index.html`;t.className=`footer`,t.innerHTML=`<div class="wrap">
    <div class="footer-grid">
      <div class="footer-about">
        <a class="brand" href="${n||`./`}">${v}<span>Mechanical Engineering from Scratch</span></a>
        <p>A free course from Analysis 1 to your own finite-element and CFD solvers. In every lesson you derive the model, code it, and test it.</p>
        <p>Made by Francesco Andreoli, mechanical engineering alumnus of ETH Zurich.</p>
      </div>
      <div><h2>Course</h2><ul>
        <li><a href="learn.html#/00.01">Start with lesson 00.01</a></li>
        <li><a href="learn.html#/course">All phases and lessons</a></li>
        <li><a href="learn.html#/progress">Your progress</a></li>
        <li><a href="learn.html#/verify">Verify a certificate</a></li></ul></div>
      <div><h2>Labs</h2><ul>
        <li><a href="${n}#lab-truss">Break the bridge</a></li>
        <li><a href="${n}#lab-flywheel">Spinning flywheel</a></li>
        <li><a href="${n}#lab-pipe">Choke the pipe</a></li>
        <li><a href="https://andreolf.github.io/coconut-lab/" rel="noopener">Coconut eddy</a></li>
        <li><a href="https://andreolf.github.io/subak-lab/" rel="noopener">Subak terraces</a></li></ul></div>
      <div><h2>Project</h2><ul>
        <li><a href="${_}" rel="noopener">Source on GitHub</a></li>
        <li><a href="${_}/issues" rel="noopener">Report a mistake</a></li>
        <li><a href="${_}/blob/main/LICENSE" rel="noopener">MIT license</a></li></ul></div>
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
  </div>`}export{r as a,p as c,d,s as f,i as h,g as i,o as l,f as m,x as n,n as o,l as p,y as r,m as s,b as t,u};
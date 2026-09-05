'use strict';
document.documentElement.classList.add('js');
const root = document.documentElement;
const main = document.querySelector('#main');
const pages = [...document.querySelectorAll('.folio-page')];
const navLinks = [...document.querySelectorAll('.section-nav a')];
const edgeTurns = [...document.querySelectorAll('[data-page-turn]')];
const viewToggle = document.querySelector('[data-view-toggle]');
const pageStatus = document.querySelector('.page-status');
const wide = matchMedia('(min-width: 960px) and (min-height: 620px)');
const legacySections = {'#about':'#background','#experience':'#background','#research':'#background','#skills':'#background'};
let current = 0;
let continuous = false;
let isPaged = false;

function updateReadingHint() {
  const page = pages[current];
  const moreBelow = isPaged && page.scrollHeight - page.clientHeight - page.scrollTop > 15;
  document.querySelector('.keyboard-hint').textContent = moreBelow ? 'Scroll to read more ↓' : 'Click the page edges to turn';
}

function hashTarget() {
  const hash = legacySections[location.hash] || location.hash;
  try { return hash ? document.getElementById(decodeURIComponent(hash.slice(1))) : null; }
  catch { return null; }
}
function updateNavigation() {
  navLinks.forEach((link, i) => {
    if (i === current) link.setAttribute('aria-current', 'location');
    else link.removeAttribute('aria-current');
  });
  edgeTurns.forEach(button => {
    const direction = Number(button.dataset.pageTurn);
    button.disabled = current + direction < 0 || current + direction >= pages.length;
  });
  pageStatus.textContent = String(current + 1).padStart(2,'0') + ' / ' + String(pages.length).padStart(2,'0');
  pageStatus.setAttribute('aria-label', 'Page ' + (current + 1) + ' of ' + pages.length + ': ' + pages[current].querySelector('h2').textContent);
  updateReadingHint();
}
function updatePages() {
  root.style.setProperty('--page-index', current);
  pages.forEach((page, i) => {
    const inactive = isPaged && i !== current;
    page.inert = inactive;
    if (inactive) page.setAttribute('aria-hidden','true');
    else page.removeAttribute('aria-hidden');
  });
  main.scrollLeft = 0;
  main.scrollTop = 0;
  updateNavigation();
}
function goTo(index, {push = false, focus = false, reset = false} = {}) {
  if (index < 0 || index >= pages.length) return;
  current = index;
  updatePages();
  if (push && location.hash !== '#' + pages[current].id) {
    history.pushState(null, '', '#' + pages[current].id);
  }
  if (isPaged) {
    if (reset) pages[current].scrollTop = 0;
    if (focus) pages[current].querySelector('h2').focus({preventScroll:true});
  } else if (push) {
    pages[current].scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth', block:'start'});
  }
}
function syncMode(scrollToCurrent = false) {
  isPaged = wide.matches && !continuous;
  root.classList.toggle('paged', isPaged);
  viewToggle.textContent = isPaged ? 'Continuous view' : 'Paged view';
  viewToggle.setAttribute('aria-pressed', String(continuous));
  viewToggle.setAttribute('aria-label', isPaged ? 'Switch to continuous reading' : 'Switch to paged reading');
  updatePages();
  if (!isPaged && scrollToCurrent) pages[current].scrollIntoView({behavior:'instant',block:'start'});
}
function readLocation(focus = false) {
  const target = hashTarget();
  const page = target?.closest('.folio-page');
  goTo(page ? pages.indexOf(page) : 0, {focus});
  if (target && target !== page && page) {
    target.closest('details')?.setAttribute('open','');
    if (isPaged) page.scrollTop = Math.max(0, target.offsetTop - page.offsetTop - 30);
  }
  if (legacySections[location.hash]) history.replaceState(null,'',legacySections[location.hash]);
}
navLinks.forEach((link, i) => link.addEventListener('click', event => {
  if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
  event.preventDefault();
  goTo(i, {push:true,focus:isPaged,reset:true});
}));
edgeTurns.forEach(button => button.addEventListener('click', () => {
  goTo(current + Number(button.dataset.pageTurn), {push:true,focus:true,reset:true});
}));
viewToggle.addEventListener('click', () => {
  continuous = !continuous;
  syncMode(true);
});
wide.addEventListener('change', () => syncMode(true));
window.addEventListener('popstate', () => readLocation(isPaged));
window.addEventListener('hashchange', () => readLocation(isPaged));
document.addEventListener('keydown', event => {
  if (!isPaged || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
  if (event.target.closest('input,textarea,select,pre,summary,[contenteditable="true"]') || window.getSelection()?.type === 'Range') return;
  if (event.key === 'ArrowRight' && current < pages.length-1) {
    event.preventDefault(); goTo(current + 1,{push:true,focus:true,reset:true});
  } else if (event.key === 'ArrowLeft' && current > 0) {
    event.preventDefault(); goTo(current - 1,{push:true,focus:true,reset:true});
  }
});
main.addEventListener('scroll', () => {
  if (isPaged && (main.scrollLeft || main.scrollTop)) {
    main.scrollLeft = 0; main.scrollTop = 0;
  }
});
if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver(entries => {
    if (isPaged) return;
    const visible = entries.filter(entry => entry.isIntersecting).sort((a,b)=>a.boundingClientRect.top-b.boundingClientRect.top);
    if (visible.length) { current = pages.indexOf(visible[0].target); updateNavigation(); }
  }, {rootMargin:'0px 0px -65% 0px',threshold:0});
  pages.forEach(page => observer.observe(page));
}
document.querySelector('.skip-link').addEventListener('click', event => {
  if (isPaged) { event.preventDefault(); pages[current].querySelector('h2').focus({preventScroll:true}); }
});
document.querySelectorAll('[data-copy]').forEach(button => {
  button.addEventListener('click', async () => {
    const text = document.getElementById(button.dataset.copy);
    const status = button.parentElement.querySelector('.copy-status');
    try {
      if (!navigator.clipboard?.writeText) throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(text.textContent);
      status.textContent = 'Copied.';
    } catch {
      const range = document.createRange(); range.selectNodeContents(text);
      const selection = window.getSelection(); selection.removeAllRanges(); selection.addRange(range);
      status.textContent = 'Text selected. Press Ctrl+C or ⌘C to copy.';
    }
  });
});
document.querySelector('[data-print]').addEventListener('click', () => window.print());
pages.forEach(page => page.addEventListener('scroll', updateReadingHint, {passive:true}));
document.querySelectorAll('details').forEach(detail => detail.addEventListener('toggle', updateReadingHint));
window.addEventListener('beforeprint', () => pages.forEach(page => {page.inert = false;page.removeAttribute('aria-hidden');}));
window.addEventListener('afterprint', updatePages);
readLocation();
syncMode();
window.addEventListener('load', () => {if (isPaged) readLocation();});

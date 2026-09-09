'use strict';
document.documentElement.classList.add('js');

const legacySections = {'#about':'#background','#experience':'#background','#skills':'#research'};
if (legacySections[window.location.hash]) {
  history.replaceState(null, '', legacySections[window.location.hash]);
}

document.querySelectorAll('[data-copy]').forEach(button => {
  button.addEventListener('click', async () => {
    const text = document.getElementById(button.dataset.copy);
    const status = button.parentElement.querySelector('.copy-status');
    try {
      if (!navigator.clipboard?.writeText) throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(text.textContent);
      status.textContent = 'Copied.';
    } catch {
      const range = document.createRange();
      range.selectNodeContents(text);
      const selection = window.getSelection();
      selection.removeAllRanges();
      selection.addRange(range);
      status.textContent = 'Text selected. Press Ctrl+C or ⌘C to copy.';
    }
  });
});

document.querySelector('[data-print]').addEventListener('click', () => window.print());

const messageForm = document.querySelector('[data-message-form]');
if (messageForm) {
  messageForm.addEventListener('submit', () => {
    const button = messageForm.querySelector('button[type="submit"]');
    button.disabled = true;
    document.querySelector('[data-message-status]').textContent = 'Sending your anonymous message…';
  });
  if (new URLSearchParams(window.location.search).get('message') === 'sent') {
    document.querySelector('[data-message-status]').textContent = 'Thank you — your anonymous message has been sent.';
  }
}

const pages = [...document.querySelectorAll('main > section')];
const navLinks = [...document.querySelectorAll('.section-nav a')];
const pageStatus = document.querySelector('[data-page-status]');
const pageHint = document.querySelector('[data-page-hint]');
const main = document.querySelector('#main');
const layout = document.querySelector('.site-layout');
let current = Math.max(0, pages.findIndex(page => '#' + page.id === window.location.hash));

document.body.classList.add('paged-site');
pages.forEach(page => page.querySelector('h2')?.setAttribute('tabindex', '-1'));

function showPage(index, {push = false, focus = false, scroll = false} = {}) {
  current = (index + pages.length) % pages.length;
  pages.forEach((page, pageIndex) => {
    const inactive = pageIndex !== current;
    page.hidden = inactive;
    page.inert = inactive;
  });
  navLinks.forEach((link, linkIndex) => {
    if (linkIndex === current) link.setAttribute('aria-current', 'location');
    else link.removeAttribute('aria-current');
  });
  pageStatus.textContent = String(current + 1).padStart(2, '0') + ' / ' + String(pages.length).padStart(2, '0');
  pageHint.textContent = current === pages.length - 1 ? 'Click anywhere to return to Background' : 'Click anywhere on the page to continue';
  if (push && window.location.hash !== '#' + pages[current].id) {
    history.pushState(null, '', '#' + pages[current].id);
  }
  if (scroll) window.scrollTo(0, layout.offsetTop);
  if (focus) pages[current].querySelector('h2')?.focus({preventScroll: true});
}

navLinks.forEach((link, index) => link.addEventListener('click', event => {
  event.preventDefault();
  showPage(index, {push: true, focus: true, scroll: true});
}));

main.addEventListener('click', event => {
  if (!(event.target instanceof Element) || event.defaultPrevented || event.button !== 0) return;
  if (event.target.closest('a,button,input,textarea,select,summary,form,pre,code,[contenteditable="true"]')) return;
  if (window.getSelection()?.type === 'Range') return;
  showPage(current + 1, {push: true, focus: true, scroll: true});
});

document.addEventListener('keydown', event => {
  if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
  if (event.target instanceof Element && event.target.closest('input,textarea,select,summary,form,pre,code,[contenteditable="true"]')) return;
  if (event.key === 'ArrowRight' || event.key === 'PageDown') {
    event.preventDefault();
    showPage(current + 1, {push: true, focus: true, scroll: true});
  } else if (event.key === 'ArrowLeft' || event.key === 'PageUp') {
    event.preventDefault();
    showPage(current - 1, {push: true, focus: true, scroll: true});
  }
});

function showLocation() {
  const index = pages.findIndex(page => '#' + page.id === window.location.hash);
  if (index >= 0) showPage(index, {focus: true, scroll: true});
}
window.addEventListener('popstate', showLocation);
window.addEventListener('hashchange', showLocation);
window.addEventListener('beforeprint', () => pages.forEach(page => {
  page.hidden = false;
  page.inert = false;
}));
window.addEventListener('afterprint', () => showPage(current));

showPage(current);

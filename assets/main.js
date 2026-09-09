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

const navLinks = [...document.querySelectorAll('.section-nav a')];
function selectSection(id) {
  navLinks.forEach(link => {
    if (link.hash === '#' + id) link.setAttribute('aria-current', 'location');
    else link.removeAttribute('aria-current');
  });
}
navLinks.forEach(link => link.addEventListener('click', () => selectSection(link.hash.slice(1))));

if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver(entries => {
    const visible = entries
      .filter(entry => entry.isIntersecting)
      .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
    if (visible.length) selectSection(visible[0].target.id);
  }, {rootMargin: '-10% 0px -68% 0px', threshold: 0});
  document.querySelectorAll('main > section').forEach(section => observer.observe(section));
}

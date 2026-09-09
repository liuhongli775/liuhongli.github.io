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
  messageForm.addEventListener('submit', event => {
    event.preventDefault();
    const data = new FormData(messageForm);
    const name = String(data.get('name') || '').trim();
    const email = String(data.get('email') || '').trim();
    const message = String(data.get('message') || '').trim();
    const subject = `Website message from ${name}`;
    const body = `Name: ${name}\nReply-to: ${email}\n\n${message}`;
    document.querySelector('[data-message-status]').textContent = 'Opening your email application…';
    window.location.href = `mailto:${messageForm.dataset.recipient}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
  });
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

'use strict';
const legacyHashes = {
  '#home': '#about',
  '#background': '#about',
  '#themes': '#interests',
  '#computational': '#research',
  '#notes': '#reading',
  '#publications': '#research',
  '#materials': '#about',
  '#beyond': '#hobbies',
  '#contact': '#message',
  '#message': '#message'
};
if (legacyHashes[window.location.hash]) {
  history.replaceState(null, '', legacyHashes[window.location.hash]);
}

const messageForm = document.querySelector('[data-message-form]');
if (messageForm) {
  messageForm.addEventListener('submit', () => {
    const button = messageForm.querySelector('button[type="submit"]');
    button.disabled = true;
    document.querySelector('[data-message-status]').textContent = 'Sending your message…';
  });
  if (new URLSearchParams(window.location.search).get('message') === 'sent') {
    document.querySelector('[data-message-status]').textContent = 'Thank you — your message has been sent.';
  }
}

const navLinks = [...document.querySelectorAll('.top-nav nav a[href^="#"]')];
function selectSection(id) {
  navLinks.forEach(link => {
    if (link.hash === '#' + id) link.setAttribute('aria-current', 'location');
    else link.removeAttribute('aria-current');
  });
}
navLinks.forEach(link => link.addEventListener('click', () => selectSection(link.hash.slice(1))));

if ('IntersectionObserver' in window) {
  const sections = navLinks.map(link => document.querySelector(link.hash)).filter(Boolean);
  const observer = new IntersectionObserver(entries => {
    const visible = entries
      .filter(entry => entry.isIntersecting)
      .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
    if (visible.length) selectSection(visible[0].target.id);
  }, {rootMargin: '-18% 0px -68% 0px', threshold: 0});
  sections.forEach(section => observer.observe(section));
}
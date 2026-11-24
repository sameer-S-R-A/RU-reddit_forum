const toggle = document.querySelector('.menu-toggle');
toggle.addEventListener('click', () => {
  const open = document.body.classList.toggle('menu-open');
  toggle.setAttribute('aria-expanded', String(open));
});
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && document.body.classList.contains('menu-open')) toggle.click();
});
document.addEventListener('click', async event => {
  const share = event.target.closest('[data-share]');
  if (!share) return;
  const url = new URL(share.dataset.share, location.origin).href;
  try {
    await navigator.clipboard.writeText(url);
    share.querySelector('span').textContent = 'Link copied';
  } catch {
    window.prompt('Copy post link', url);
  }
});
const composer = document.querySelector('[data-composer]');
if (composer) {
  function showFields() {
    const type = composer.elements.post_type.value;
    composer.querySelectorAll('[data-kind]').forEach(row => {
      row.hidden = row.dataset.kind !== type;
      row.querySelector('input').disabled = row.hidden;
    });
  }
  composer.addEventListener('change', showFields);
  showFields();
}

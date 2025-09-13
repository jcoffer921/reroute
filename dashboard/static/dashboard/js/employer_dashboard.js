// Minimal JS to load applicants into a modal
(function () {
  const qs = (s, r = document) => r.querySelector(s);
  const qsa = (s, r = document) => Array.from(r.querySelectorAll(s));

  const modal = qs('#modalRoot');
  const backdrop = qs('#modalBackdrop');
  const body = qs('#modalBody');
  const closeBtn = modal ? modal.querySelector('.modal-close') : null;

  function openModal(html) {
    if (!modal || !backdrop) return;
    body.innerHTML = html || '';
    backdrop.classList.remove('hidden');
    modal.classList.remove('hidden');
  }

  function closeModal() {
    if (!modal || !backdrop) return;
    modal.classList.add('hidden');
    backdrop.classList.add('hidden');
    body.innerHTML = '';
  }

  if (closeBtn) closeBtn.addEventListener('click', closeModal);
  if (backdrop) backdrop.addEventListener('click', closeModal);

  qsa('.view-applicants').forEach(btn => {
    btn.addEventListener('click', async () => {
      const url = btn.getAttribute('data-url');
      if (!url) return;
      try {
        body.textContent = 'Loading…';
        openModal();
        const resp = await fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
        const html = await resp.text();
        body.innerHTML = html;
      } catch (e) {
        body.textContent = 'Failed to load applicants.';
      }
    });
  });
})();


// Click-to-edit: avatar and hero background modals (owner view)
(function(){
  const root = document.querySelector('.employer-public');
  if (!root) return;

  // Elements
  const heroBg = root.querySelector('.hero-bg');
  const heroLogo = root.querySelector('.hero .hero-logo');
  const bgModal = document.getElementById('bgModal');
  const bgInput = document.getElementById('bgFileInput');
  const bgPreview = document.getElementById('bgPreview');

  const openBg = () => { if (bgModal) bgModal.style.display = 'block'; };
  const closeBg = () => { if (bgModal) bgModal.style.display = 'none'; };

  // Open background modal when clicking the hero background
  if (heroBg && bgModal) {
    heroBg.style.cursor = 'pointer';
    heroBg.addEventListener('click', (e) => {
      // Avoid triggering when clicking inside overlaid content
      if (e.target.closest('.hero-content')) return;
      openBg();
    });
  }
  // Also open via explicit button
  document.querySelectorAll('[data-open-bg]').forEach(el => el.addEventListener('click', openBg));

  // Close background modal on outside click
  if (bgModal) {
    bgModal.addEventListener('click', (e) => {
      if (e.target === bgModal) closeBg();
    });
    const closeBtn = bgModal.querySelector('[data-close-bg]');
    if (closeBtn) closeBtn.addEventListener('click', closeBg);
  }

  // Preview background selection
  if (bgInput && bgPreview) {
    bgInput.addEventListener('change', () => {
      const file = bgInput.files && bgInput.files[0];
      if (!file) { bgPreview.style.display = 'none'; return; }
      const url = URL.createObjectURL(file);
      bgPreview.src = url;
      bgPreview.style.display = 'block';
    });
  }

  // Open existing profile picture modal on avatar click if present
  const picModal = document.getElementById('profilePicModal');
  const profilePicFormInput = document.getElementById('modalPicInput');
  if (heroLogo && picModal) {
    heroLogo.style.cursor = 'pointer';
    heroLogo.addEventListener('click', () => {
      picModal.style.display = 'block';
      // Trigger file picker immediately for convenience
      if (profilePicFormInput) profilePicFormInput.click();
    });
    document.querySelectorAll('[data-open-avatar]').forEach(el => el.addEventListener('click', () => {
      picModal.style.display = 'block';
      if (profilePicFormInput) profilePicFormInput.click();
    }));
    // Close when clicking outside inner dialog
    picModal.addEventListener('click', (e) => {
      if (e.target === picModal) { picModal.style.display = 'none'; }
    });
    const closeAvatar = document.querySelector('[data-close-avatar]');
    if (closeAvatar) closeAvatar.addEventListener('click', () => { picModal.style.display = 'none'; });
  }
})();

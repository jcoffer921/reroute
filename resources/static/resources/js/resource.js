// Hero 2 video controls: background playback + modal playback
(function(){
  const bgVideo = document.getElementById('hero2BgVideo');
  const playBtn = document.getElementById('hero2Play');
  const modal = document.getElementById('hero2Modal');
  const modalVideo = document.getElementById('hero2ModalVideo');
  const closeBtn = document.getElementById('hero2Close');

  if (!playBtn || !modal || !modalVideo) return;

  const openModal = () => {
    try { if (bgVideo) bgVideo.pause(); } catch(_){}
    modal.removeAttribute('hidden');
    document.body.style.overflow = 'hidden';
    try {
      modalVideo.muted = false;
      modalVideo.controls = true;
      const p = modalVideo.play();
      if (p && typeof p.then === 'function') { p.catch(()=>{}); }
    } catch(_){}
  };

  const closeModal = () => {
    try { modalVideo.pause(); } catch(_){}
    modal.setAttribute('hidden', '');
    document.body.style.overflow = '';
    try {
      if (bgVideo) {
        bgVideo.muted = true;
        const p = bgVideo.play();
        if (p && typeof p.then === 'function') { p.catch(()=>{}); }
      }
    } catch(_){}
  };

  playBtn.addEventListener('click', openModal);
  closeBtn && closeBtn.addEventListener('click', closeModal);
  modal.addEventListener('click', (e) => {
    if (e.target && e.target.hasAttribute('data-hero2-close')) {
      closeModal();
    }
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !modal.hasAttribute('hidden')) closeModal();
  });
})();

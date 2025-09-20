// Subtle parallax + fade on hero background
(function() {
  const hero = document.querySelector('.employer-public .hero');
  const bg = document.querySelector('.employer-public .hero-bg');
  if (!hero || !bg) return;

  const onScroll = () => {
    const rect = hero.getBoundingClientRect();
    const h = rect.height || hero.offsetHeight || 1;
    const scrolled = Math.min(Math.max(-rect.top, 0), h);
    const progress = scrolled / h; // 0 -> 1
    // Move the bg slightly (parallax) and reduce opacity a touch
    const translate = progress * 20; // px
    const opacity = 1 - progress * 0.35; // fade to ~0.65
    bg.style.transform = `translateY(${translate}px)`;
    bg.style.opacity = String(opacity);
  };

  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll);
  onScroll();
})();


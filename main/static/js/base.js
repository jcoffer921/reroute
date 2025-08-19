/* -------------------------------------------------------
 * Mobile menu controller (matches base.html + your CSS)
 * - HTML calls: onclick="toggleMobileMenu()"
 * - Drawer element: #mobileMenu
 * - Visible class: .show  (you already use .mobile-menu.show { left: 0; })
 * ----------------------------------------------------- */
(function () {
  const menu = document.getElementById('mobileMenu');        // slide-in drawer
  const hamburger = document.querySelector('.hamburger');     // ☰ button in navbar
  if (!menu || !hamburger) return;                            // graceful exit if markup changes

  // Open/close helpers (lock body scroll on open)
  function openMenu() {
    menu.classList.add('show');                               // <-- aligns with your CSS
    menu.setAttribute('aria-hidden', 'false');                // a11y: announce state
    document.body.classList.add('no-scroll');                 // prevent background scrolling
    hamburger.setAttribute('aria-expanded', 'true');
    // Optional: focus first link for better keyboard UX
    const firstLink = menu.querySelector('.mobile-nav-links a, button');
    if (firstLink) firstLink.focus({ preventScroll: true });
  }
  function closeMenu() {
    menu.classList.remove('show');
    menu.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('no-scroll');
    hamburger.setAttribute('aria-expanded', 'false');
    // Return focus to hamburger for accessibility
    hamburger.focus({ preventScroll: true });
  }

  // Expose the global used by base.html
  window.toggleMobileMenu = function () {
    const isOpen = menu.classList.contains('show');
    if (isOpen) closeMenu(); else openMenu();
  };

  // Also wire direct events so it works even if inline onclick is removed later
  const activate = (e) => {
    // Prevent double-trigger on touch devices
    if (e.type === 'touchstart') e.preventDefault();
    window.toggleMobileMenu();
  };
  hamburger.addEventListener('click', activate, { passive: true });
  hamburger.addEventListener('touchstart', activate, { passive: false });

  // Close on any link/button tap inside the drawer (e.g., Logout)
  menu.addEventListener('click', (e) => {
    if (e.target.closest('a') || e.target.closest('button')) closeMenu();
  });

  // Close on Escape
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && menu.classList.contains('show')) closeMenu();
  });

  // Defensive: if resized to desktop, ensure the drawer is closed
  let resizeTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      if (window.innerWidth >= 769 && menu.classList.contains('show')) {
        closeMenu();
      }
    }, 120);
  });
})();

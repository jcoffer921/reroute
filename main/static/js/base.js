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

/* ---------------------------------------------
 * Right-side profile dropdown (desktop only)
 * - Expects:
 *   - Button  : #userMenuButton (contains <span id="arrow-icon">▼</span>)
 *   - Dropdown: #userDropdown
 * - Works alongside the mobile drawer code
 * ------------------------------------------- */
(function () {
  const btn  = document.getElementById('userMenuButton'); // initials button
  const menu = document.getElementById('userDropdown');   // dropdown panel
  const arrow = document.getElementById('arrow-icon');    // ▼ / ▲ indicator

  // Bail gracefully if elements aren’t present (e.g., logged out pages)
  if (!btn || !menu) return;

  // --- Helpers: open/close with ARIA + arrow updates
  function openMenu() {
    menu.classList.add('open');
    btn.setAttribute('aria-expanded', 'true');
    if (arrow) arrow.textContent = '▲';
  }
  function closeMenu() {
    menu.classList.remove('open');
    btn.setAttribute('aria-expanded', 'false');
    if (arrow) arrow.textContent = '▼';
  }
  function toggleMenu() {
    const isOpen = menu.classList.contains('open');
    if (isOpen) closeMenu(); else openMenu();
  }

  // --- Toggle on click / Enter / Space
  btn.addEventListener('click', (e) => {
    e.stopPropagation();
    toggleMenu();
  });
  btn.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      toggleMenu();
    }
  });

  // --- Close when clicking anywhere outside
  document.addEventListener('click', (e) => {
    if (!menu.contains(e.target) && !btn.contains(e.target)) closeMenu();
  });

  // --- Close on Esc
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeMenu();
  });

  // --- Close when a link or button inside the dropdown is used (e.g., Sign out)
  menu.addEventListener('click', (e) => {
    if (e.target.closest('a') || e.target.closest('button')) closeMenu();
  });

  // Defensive: if viewport shrinks to mobile (where this menu is hidden), ensure closed
  window.addEventListener('resize', () => {
    if (window.innerWidth <= 768) closeMenu();
  });
})();

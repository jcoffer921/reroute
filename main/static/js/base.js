/* =============================================================================
 * ReRoute Base JS
 * - Mobile drawer (hamburger) using #mobileMenu + .show
 * - Right-side profile dropdown (desktop) using #userMenuButton + #userDropdown
 * - Accessibility: ARIA updates, Esc to close, click-outside handling
 * ============================================================================= */

(() => {
  const DESKTOP_MIN = 769; // Keep aligned with your CSS breakpoint

  // Mini helpers
  const qs = (sel, root = document) => root.querySelector(sel);
  const on = (el, ev, fn, opts) => el && el.addEventListener(ev, fn, opts);

  /* -------------------------- MOBILE DRAWER -------------------------- */
  const mobileMenu   = qs('#mobileMenu');       // <div id="mobileMenu" class="mobile-menu">
  const hamburgerBtn = qs('.hamburger');        // <button class="hamburger" onclick="toggleMobileMenu()">

  function openMobileMenu() {
    mobileMenu.classList.add('show');           // your CSS uses .mobile-menu.show { left:0; }
    mobileMenu.setAttribute('aria-hidden', 'false');
    document.body.classList.add('no-scroll');   // prevent background scroll
    hamburgerBtn?.setAttribute('aria-expanded', 'true');

    // (Optional) focus the first link inside the drawer for a11y
    const firstLink = mobileMenu.querySelector('.mobile-nav-links a, a, button');
    firstLink?.focus({ preventScroll: true });
  }
  function closeMobileMenu() {
    mobileMenu.classList.remove('show');
    mobileMenu.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('no-scroll');
    hamburgerBtn?.setAttribute('aria-expanded', 'false');
    hamburgerBtn?.focus({ preventScroll: true });
  }

  // Keep your inline HTML onclick working
  window.toggleMobileMenu = function toggleMobileMenu() {
    if (!mobileMenu) return;
    mobileMenu.classList.contains('show') ? closeMobileMenu() : openMobileMenu();
  };

  if (mobileMenu && hamburgerBtn) {
    on(hamburgerBtn, 'click', () => window.toggleMobileMenu(), { passive: true });

    // Close when clicking any link/button inside the drawer
    on(mobileMenu, 'click', (e) => {
      if (e.target.closest('a') || e.target.closest('button')) closeMobileMenu();
    });

    // Close on Escape
    on(document, 'keydown', (e) => {
      if (e.key === 'Escape' && mobileMenu.classList.contains('show')) closeMobileMenu();
    });

    // Auto-close if resized to desktop
    let resizeTimer;
    on(window, 'resize', () => {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(() => {
        if (window.innerWidth >= DESKTOP_MIN && mobileMenu.classList.contains('show')) {
          closeMobileMenu();
        }
      }, 120);
    });
  }

  /* -------------------- RIGHT-SIDE PROFILE DROPDOWN ------------------- */
  // Desktop only — your CSS hides .user-profile-right on mobile
  const profileBtn   = qs('#userMenuButton');   // initials button
  const profilePanel = qs('#userDropdown');     // dropdown panel
  const arrowIcon    = qs('#arrow-icon');       // ▼ / ▲

  function openProfile() {
    profilePanel.classList.add('show');         // your CSS uses .user-dropdown.show { display:block; }
    profileBtn.setAttribute('aria-expanded', 'true');
    if (arrowIcon) arrowIcon.textContent = '▲';
  }
  function closeProfile() {
    profilePanel.classList.remove('show');
    profileBtn.setAttribute('aria-expanded', 'false');
    if (arrowIcon) arrowIcon.textContent = '▼';
  }
  function toggleProfile() {
    profilePanel.classList.contains('show') ? closeProfile() : openProfile();
  }

  if (profileBtn && profilePanel) {
    on(profileBtn, 'click', (e) => { e.stopPropagation(); toggleProfile(); }, { passive: true });
    on(profileBtn, 'keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggleProfile(); }
    });

    // Close on outside click or Esc
    on(document, 'click', (e) => {
      if (!profilePanel.contains(e.target) && !profileBtn.contains(e.target)) closeProfile();
    });
    on(document, 'keydown', (e) => { if (e.key === 'Escape') closeProfile(); });

    // Close after choosing any link/button inside
    on(profilePanel, 'click', (e) => {
      if (e.target.closest('a') || e.target.closest('button')) closeProfile();
    });

    // Ensure closed when shrinking to mobile
    on(window, 'resize', () => { if (window.innerWidth < DESKTOP_MIN) closeProfile(); });
  }
})();

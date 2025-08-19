/* =============================================================================
 * ReRoute Base JS
 * - Mobile drawer (hamburger) using #mobileMenu + .show
 * - Right-side profile dropdown (desktop) using #userMenuButton + #userDropdown
 * - Accessibility: ARIA updates, Esc to close, click-outside handling
 * ============================================================================= */

(() => {
  // ---------------------------------------------------------------------------
  // Config
  // ---------------------------------------------------------------------------
  const DESKTOP_MIN = 769; // Keep in sync with your CSS breakpoints

  // ---------------------------------------------------------------------------
  // Helpers
  // ---------------------------------------------------------------------------
  const qs = (sel, root = document) => root.querySelector(sel);
  const on = (el, ev, fn, opts) => el && el.addEventListener(ev, fn, opts);

  // ---------------------------------------------------------------------------
  // MOBILE DRAWER (Hamburger)
  // HTML:
  //   <button class="hamburger" onclick="toggleMobileMenu()" ...>☰</button>
  //   <div id="mobileMenu" class="mobile-menu" aria-hidden="true"> ... </div>
  // CSS:
  //   .mobile-menu { left:-100%; }
  //   .mobile-menu.show { left:0; }
  // ---------------------------------------------------------------------------
  const mobileMenu   = qs('#mobileMenu');
  const hamburgerBtn = qs('.hamburger');

  function openMobileMenu() {
    mobileMenu.classList.add('show');
    mobileMenu.setAttribute('aria-hidden', 'false');
    document.body.classList.add('no-scroll');       // lock background scroll
    hamburgerBtn?.setAttribute('aria-expanded', 'true');

    // Optionally focus first actionable element for accessibility
    const firstLink = qs('.mobile-nav-links a, .mobile-menu a, .mobile-menu button', mobileMenu);
    firstLink?.focus({ preventScroll: true });
  }

  function closeMobileMenu() {
    mobileMenu.classList.remove('show');
    mobileMenu.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('no-scroll');
    hamburgerBtn?.setAttribute('aria-expanded', 'false');
    hamburgerBtn?.focus({ preventScroll: true });
  }

  // Expose global for inline HTML onclick (keeps your template unchanged)
  window.toggleMobileMenu = function toggleMobileMenu() {
    if (!mobileMenu) return;
    mobileMenu.classList.contains('show') ? closeMobileMenu() : openMobileMenu();
  };

  // Bind events only if elements exist
  if (mobileMenu && hamburgerBtn) {
    // Click / touch to open
    on(hamburgerBtn, 'click', () => window.toggleMobileMenu(), { passive: true });

    // Close when tapping any link/button inside the drawer (e.g., logout)
    on(mobileMenu, 'click', (e) => {
      if (e.target.closest('a') || e.target.closest('button')) closeMobileMenu();
    });

    // Close on Escape
    on(document, 'keydown', (e) => {
      if (e.key === 'Escape' && mobileMenu.classList.contains('show')) closeMobileMenu();
    });

    // If resized to desktop, ensure the drawer is closed
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

  // ---------------------------------------------------------------------------
  // DESKTOP PROFILE DROPDOWN (Right side)
  // HTML:
  //   <button id="userMenuButton" aria-expanded="false" aria-controls="userDropdown">AB <span id="arrow-icon">▼</span></button>
  //   <div id="userDropdown" class="user-dropdown" role="menu" ...>...</div>
  // CSS:
  //   .user-dropdown { display:none; }
  //   .user-dropdown.show { display:block; }
  // NOTE:
  //   On mobile (<768px) you intentionally hide .user-profile-right in CSS. Good.
  //   These links should also exist in the mobile drawer.
  // ---------------------------------------------------------------------------
  const profileBtn   = qs('#userMenuButton');
  const profilePanel = qs('#userDropdown');
  const arrowIcon    = qs('#arrow-icon');

  function openProfile() {
    profilePanel.classList.add('show');            // matches your CSS
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
    // Toggle via click / keyboard
    on(profileBtn, 'click', (e) => { e.stopPropagation(); toggleProfile(); }, { passive: true });
    on(profileBtn, 'keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        toggleProfile();
      }
    });

    // Close when clicking outside
    on(document, 'click', (e) => {
      if (!profilePanel.contains(e.target) && !profileBtn.contains(e.target)) closeProfile();
    });

    // Close on Escape
    on(document, 'keydown', (e) => { if (e.key === 'Escape') closeProfile(); });

    // Close after action inside dropdown (e.g., Sign out)
    on(profilePanel, 'click', (e) => {
      if (e.target.closest('a') || e.target.closest('button')) closeProfile();
    });

    // Defensive: if we shrink to mobile (area hidden), ensure closed
    on(window, 'resize', () => { if (window.innerWidth < DESKTOP_MIN) closeProfile(); });
  }
})();

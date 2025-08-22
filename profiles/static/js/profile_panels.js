/* =============================================================================
 * profile_panels.js
 * Slide-in editor logic for the Profile page (owner view).
 *
 * This file is tailored to your current HTML:
 *  - Edit buttons (openers by ID):
 *      #editSlideTrigger           → #slideEditor
 *      #editEmploymentTrigger      → #employmentSlideEditor
 *      #editEmergencyTrigger       → #emergencySlidePanel
 *      #editDemographicsTrigger    → #demographicsSlidePanel
 *      #editSkillsTrigger          → #skillsSlidePanel
 *
 *  - Forms inside panels (by ID or by panel selector):
 *      #personalSlideForm                  (Personal)
 *      #employmentSlideForm                (Employment)
 *      #emergencySlidePanel form           (Emergency — no form ID)
 *      #demographicsSlidePanel form        (Demographics — no form ID)
 *      #skillsSlideForm                    (Skills)
 *
 *  - Expected backend JSON shape on success:
 *      { ok: true, updated: { ...fields... } }
 *
 * UX Notes:
 *  - Adds/removes .open on panels and body.no-scroll to lock the page.
 *  - Shows a button spinner if your Save button contains:
 *        <span class="btn-text">Save</span><span class="spinner" style="display:none"></span>
 *  - If the response is NOT JSON/ok, falls back to full-page redirect (PRG safe).
 *
 * Accessibility:
 *  - Focuses the first control when a panel opens.
 *  - ESC closes any open panel.
 * ============================================================================= */

document.addEventListener('DOMContentLoaded', () => {
  /* ---------- Utilities ---------- */

  // Safe query helpers
  const qs  = (s, r=document) => r.querySelector(s);
  const qsa = (s, r=document) => Array.from(r.querySelectorAll(s));

  // CSRF cookie (Django standard)
  const getCookie = (name) => {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return decodeURIComponent(parts.pop().split(';').shift());
    return null;
  };
  const csrftoken = getCookie('csrftoken') || '';

  // Panel open/close
  function openPanel(selOrEl) {
    const panel = typeof selOrEl === 'string' ? qs(selOrEl) : selOrEl;
    if (!panel) return;
    panel.classList.add('open');                 // CSS also supports .visible, but we standardize on .open
    document.body.classList.add('no-scroll');    // prevent background scroll while open
    // Focus the first focusable control inside
    const first = panel.querySelector('input, select, textarea, button');
    if (first) first.focus({ preventScroll: true });
  }

  function closePanel(selOrEl) {
    const panel = typeof selOrEl === 'string' ? qs(selOrEl) : selOrEl;
    if (!panel) return;
    panel.classList.remove('open');
    document.body.classList.remove('no-scroll');
  }

  // Expose for any legacy inline onclick="closePanel('...')"
  window.closePanel = (idOrSel) => closePanel(
    idOrSel.startsWith('#') ? idOrSel : `#${idOrSel}`
  );

  // Close on ESC
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') qsa('.slide-panel.open').forEach(closePanel);
  });

  // Wire simple openers by ID (your current HTML uses these)
  const openers = [
    ['#editSlideTrigger',        '#slideEditor'],
    ['#editEmploymentTrigger',   '#employmentSlideEditor'],
    ['#editEmergencyTrigger',    '#emergencySlidePanel'],
    ['#editDemographicsTrigger', '#demographicsSlidePanel'],
    ['#editSkillsTrigger',       '#skillsSlidePanel'],
  ];
  openers.forEach(([btnSel, panelSel]) => {
    const btn = qs(btnSel);
    if (btn) btn.addEventListener('click', (e) => { e.preventDefault(); openPanel(panelSel); });
  });

  /* ---------- Toggle groups in Employment (buttons set hidden input values) ---------- */
  // HTML pattern:
  // <div class="btn-toggle-group" data-name="authorized_us">
  //   <button type="button" data-value="yes">Yes</button>
  //   <button type="button" data-value="no">No</button>
  // </div>
  // <input type="hidden" name="authorized_us" value="{{ profile.work_in_us }}">
  qsa('.btn-toggle-group').forEach(group => {
    const fieldName = group.getAttribute('data-name'); // name of the hidden input to store selection
    if (!fieldName) return;
    // Find the sibling hidden input by name
    const hidden = group.parentElement.querySelector(`input[type="hidden"][name="${fieldName}"]`)
                 || group.querySelector(`input[type="hidden"][name="${fieldName}"]`);
    group.querySelectorAll('button[data-value]').forEach(btn => {
      btn.addEventListener('click', () => {
        // Visual "active" state
        group.querySelectorAll('button').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        // Persist the value
        if (hidden) hidden.value = btn.getAttribute('data-value');
      });
    });
  });

  /* ---------- Generic AJAX submit handler for a form ---------- */
  async function submitPanelForm(form, { onSuccess } = {}) {
    // If the form has no action, abort
    if (!form || !form.action) return;

    // Button spinner UX (optional – only if present)
    const btn     = form.querySelector('button[type="submit"]');
    const spinner = btn ? btn.querySelector('.spinner') : null;
    const label   = btn ? btn.querySelector('.btn-text') : null;
    if (btn) btn.disabled = true;
    if (spinner && label) { spinner.style.display = 'inline-block'; label.style.display = 'none'; }

    try {
      const resp = await fetch(form.action, {
        method: 'POST',
        headers: { 'X-CSRFToken': csrftoken, 'X-Requested-With': 'XMLHttpRequest' },
        body: new FormData(form),
      });

      // Try to parse JSON. If it fails, we’ll assume non-AJAX fallback (redirect).
      let data = {};
      try { data = await resp.json(); } catch (_) { data = {}; }

      // Not JSON or not ok → let server handle PRG; hard redirect to profile.
      if (!resp.ok || data.ok !== true) {
        window.location.href = '/profile/';     // PRG fallback keeps things consistent
        return;
      }

      // Patch page with returned fields
      if (typeof onSuccess === 'function') onSuccess(data.updated || {}, data);

      // Close panel if this form is inside one
      const panel = form.closest('.slide-panel');
      if (panel) closePanel(panel);

      // Toast if you have one
      if (typeof window.showToast === 'function') window.showToast('Saved');
    } catch (err) {
      alert('Network error. Please try again.');
    } finally {
      if (spinner && label) { spinner.style.display = 'none'; label.style.display = 'inline'; }
      if (btn) btn.disabled = false;
    }
  }

  /* ---------- Wire each form (matches your current HTML) ---------- */

  // PERSONAL (#personalSlideForm)
  (function wirePersonal() {
    const form = qs('#personalSlideForm');
    if (!form) return;

    form.addEventListener('submit', (e) => {
      e.preventDefault();
      submitPanelForm(form, {
        onSuccess: (u) => {
          // Update full name display(s)
          qsa('[data-profile-full-name]').forEach(el => el.textContent = (u.full_name || '').trim());
          // Update labeled grid values
          const map = {
            'First Name:': u.firstname,
            'Last Name:':  u.lastname,
            'Email:':      u.personal_email,
            'Phone:':      u.phone_number,
            'Location:':   [u.city, u.state].filter(Boolean).join(', '),
          };
          qsa('.info-grid .info-item').forEach(item => {
            const label = item.querySelector('strong')?.textContent?.trim();
            const span  = item.querySelector('span');
            if (label && span && (label in map)) span.textContent = map[label] || '';
          });
        }
      });
    });
  })();

  // EMPLOYMENT (#employmentSlideForm)
  (function wireEmployment() {
    const form = qs('#employmentSlideForm');
    if (!form) return;

    form.addEventListener('submit', (e) => {
      e.preventDefault();
      submitPanelForm(form, {
        onSuccess: (u) => {
          const map = {
            'Work in US:':         u.work_in_us,
            'Sponsorship Needed:': u.sponsorship_needed,
            'Disability:':         u.disability,
            'LGBTQ+:':             u.lgbtq,
            'Gender:':             u.gender,
            'Veteran:':            u.veteran_status,
          };
          qsa('.info-grid .info-item').forEach(item => {
            const label = item.querySelector('strong')?.textContent?.trim();
            const span  = item.querySelector('span');
            if (label && span && (label in map)) span.textContent = map[label] || '';
          });
        }
      });
    });
  })();

  // EMERGENCY (#emergencySlidePanel form) — no form ID in your HTML, target first form inside the panel
  (function wireEmergency() {
    const form = qs('#emergencySlidePanel form');
    if (!form) return;

    form.addEventListener('submit', (e) => {
      e.preventDefault();
      submitPanelForm(form, {
        onSuccess: (u) => {
          const map = {
            'First Name:':   u.emergency_contact_firstname,
            'Last Name:':    u.emergency_contact_lastname,
            'Relationship:': u.emergency_contact_relationship,
            'Phone:':        u.emergency_contact_phone,
            'Email:':        u.emergency_contact_email,
          };
          qsa('.info-grid .info-item').forEach(item => {
            const label = item.querySelector('strong')?.textContent?.trim();
            const span  = item.querySelector('span');
            if (label && span && (label in map)) span.textContent = map[label] || '';
          });
        }
      });
    });
  })();

  // DEMOGRAPHICS (#demographicsSlidePanel form) — no form ID in your HTML, target first form inside the panel
  (function wireDemographics() {
    const form = qs('#demographicsSlidePanel form');
    if (!form) return;

    form.addEventListener('submit', (e) => {
      e.preventDefault();
      submitPanelForm(form, {
        onSuccess: (u) => {
          const map = {
            'Gender:':                 u.gender,
            'Ethnicity:':              u.ethnicity,
            'Veteran Status:':         u.veteran_status,
            'Disability Explanation:': u.disability_explanation,
            'Veteran Explanation:':    u.veteran_explanation,
          };
          qsa('.info-grid .info-item').forEach(item => {
            const label = item.querySelector('strong')?.textContent?.trim();
            const span  = item.querySelector('span');
            if (label && span && (label in map)) span.textContent = map[label] || '';
          });
        }
      });
    });
  })();

  // SKILLS (#skillsSlideForm)
  (function wireSkills() {
    const form = qs('#skillsSlideForm');
    if (!form) return;

    form.addEventListener('submit', (e) => {
      e.preventDefault();
      submitPanelForm(form, {
        onSuccess: (u) => {
          const ul = qs('.skill-list');
          if (ul && Array.isArray(u.skills)) {
            ul.innerHTML = u.skills.map(s => `<li class="skill-item">${s}</li>`).join('');
          }
        }
      });
    });
  })();

  /* ---------- Bio toggles (your template calls these) ---------- */

  // Show/hide truncated vs full bio text
  window.toggleBio = function toggleBio() {
    const short = qs('#bioPreview');
    const full  = qs('#fullBio');
    if (!short || !full) return;
    const showingFull = full.style.display === 'block';
    full.style.display  = showingFull ? 'none'  : 'block';
    short.style.display = showingFull ? 'block' : 'none';
  };

  // Show/hide the Bio edit form
  window.toggleBioEdit = function toggleBioEdit() {
    const form  = qs('#editBioForm');
    const short = qs('#bioPreview');
    const full  = qs('#fullBio');
    if (!form) return;
    const showing = form.style.display === 'block';
    form.style.display  = showing ? 'none' : 'block';
    // Hide the previews when editing; restore short preview when closing
    if (!showing) { if (short) short.style.display = 'none'; if (full) full.style.display = 'none'; }
    else          { if (short) short.style.display = 'block'; }
  };
});

// profile_panels.js — generic slide-in form handler for Profile edits
// Works with Django: returns JSON on success, shows inline errors on failure.

document.addEventListener('DOMContentLoaded', () => {
  // --- CSRF from cookie (Django standard) ---
  const getCookie = (name) => {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return decodeURIComponent(parts.pop().split(';').shift());
    return null;
  };
  const csrftoken = getCookie('csrftoken');

  // Reusable binder
  function wirePanelForm(formSelector, { onSuccess, onError } = {}) {
    const form = document.querySelector(formSelector);
    if (!form) return;

    const errorsBox = form.querySelector('[data-errors]');

    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      // Clear previous errors
      if (errorsBox) { errorsBox.hidden = true; errorsBox.innerHTML = ''; }

      try {
        const resp = await fetch(form.action, {
          method: 'POST',
          headers: { 'X-CSRFToken': csrftoken || '', 'X-Requested-With': 'XMLHttpRequest' },
          body: new FormData(form),
        });

        const data = await resp.json().catch(() => ({}));

        if (!resp.ok || !data.ok) {
          const errs = (data && data.errors) || { form: 'Please fix the errors and try again.' };
          if (errorsBox) {
            errorsBox.hidden = false;
            errorsBox.innerHTML = Object.values(errs).map(msg => `<div class="error">${msg}</div>`).join('');
          }
          if (onError) onError(errs);
          return;
        }

        if (onSuccess) onSuccess(data.updated || {}, data);

        // Optional: close panel using selector stored on the form
        const panelSel = form.getAttribute('data-panel');
        if (panelSel && typeof window.closeSlidePanel === 'function') window.closeSlidePanel(panelSel);

        if (typeof window.showToast === 'function') window.showToast('Saved');
      } catch (err) {
        if (errorsBox) {
          errorsBox.hidden = false;
          errorsBox.innerHTML = '<div class="error">Network error. Please try again.</div>';
        }
      }
    });
  }

  // ---------------- Wire each panel below ----------------

  // Demographics
  wirePanelForm('#demographicsForm', {
    onSuccess: (u) => {
      const pill = document.querySelector('[data-demographics-pill]');
      if (pill) pill.textContent = u.pill_text || '';
      const g = document.querySelector('[data-demographics-gender]');
      const e = document.querySelector('[data-demographics-ethnicity]');
      const r = document.querySelector('[data-demographics-race]');
      if (g) g.textContent = u.gender || '';
      if (e) e.textContent = u.ethnicity || '';
      if (r) r.textContent = u.race || '';
    },
  });

  // Employment / Status
  wirePanelForm('#employmentForm', {
    onSuccess: (u) => {
      Object.entries(u).forEach(([key, val]) => {
        const el = document.querySelector(`[data-employment-${key}]`);
        if (el) el.textContent = val || '';
      });
    },
  });

  // Emergency Contact
  wirePanelForm('#emergencyForm', {
    onSuccess: (u) => {
      const full = document.querySelector('[data-emergency-fullname]');
      if (full) full.textContent = u.emergency_contact_fullname || '';
      ['relationship','phone','email'].forEach((k) => {
        const el = document.querySelector(`[data-emergency-${k}]`);
        if (el) el.textContent = u[`emergency_contact_${k}`] || '';
      });
    },
  });

  // Personal Info (names, etc.)
  wirePanelForm('#personalForm', {
    onSuccess: (u) => {
      document.querySelectorAll('[data-profile-full-name]').forEach(el => el.textContent = u.full_name || '');
      document.querySelectorAll('[data-user-initials]').forEach(el => el.textContent = u.initials || '');
      ['phone_number','personal_email','state','city'].forEach((k) => {
        const el = document.querySelector(`[data-personal-${k}]`);
        if (el) el.textContent = u[k] || '';
      });
    },
  });

  // Skills (tags)
  wirePanelForm('#skillsForm', {
    onSuccess: (u) => {
      const container = document.querySelector('[data-skill-tags]');
      if (container && Array.isArray(u.skills)) {
        container.innerHTML = u.skills.map(s => `<span class="tag">${s}</span>`).join('');
      }
    },
  });
});

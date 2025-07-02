function bindLivePreview(inputId, previewId, fallback = '') {
  const input = document.getElementById(inputId);
  const preview = document.getElementById(previewId);

  if (input && preview) {
    input.addEventListener('input', () => {
      preview.textContent = input.value || fallback;
    });

    // Initialize preview on page load
    preview.textContent = input.value || fallback;
  }
}

function bindDateRangePreview(startId, endId, previewId) {
  const startInput = document.getElementById(startId);
  const endInput = document.getElementById(endId);
  const preview = document.getElementById(previewId);

  function updateDates() {
    const start = startInput?.value || 'Start';
    const end = endInput?.value || 'End';
    preview.textContent = `${start} - ${end}`;
  }

  startInput?.addEventListener('input', updateDates);
  endInput?.addEventListener('input', updateDates);

  updateDates(); // Initialize on load
}

function bindBulletPreview(textareaId, previewListId, fallback = 'Responsibilities') {
  const textarea = document.getElementById(textareaId);
  const previewList = document.getElementById(previewListId);

  function updateBullets() {
    const lines = (textarea?.value || '').split('\n').filter(line => line.trim());
    previewList.innerHTML = '';

    if (lines.length === 0) {
      const fallbackLi = document.createElement('li');
      fallbackLi.textContent = fallback;
      previewList.appendChild(fallbackLi);
      return;
    }

    lines.forEach(line => {
      const li = document.createElement('li');
      li.textContent = line.trim();
      previewList.appendChild(li);
    });
  }

  textarea?.addEventListener('input', updateBullets);
  updateBullets(); // Initialize on load
}

document.addEventListener('DOMContentLoaded', () => {
  const experienceForm = document.getElementById('experience-form');
  if (!experienceForm) return;

  const entries = document.getElementById('experience-entries');
  const previewContainer = document.getElementById('experience-preview-container');
  const totalFormsInput = document.getElementById('id_form-TOTAL_FORMS');
  const addBtn = document.getElementById('add-experience-btn');

  // Initial preview binding for form-0
  bindPreviewForIndex(0);

  addBtn?.addEventListener('click', () => {
    const currentIndex = parseInt(totalFormsInput.value);
    const firstEntry = entries.querySelector('.experience-entry');

    if (!firstEntry) {
      console.error("⛔ .experience-entry not found!")
      return;
    }
    
    const newEntry = firstEntry.cloneNode(true);


    // Clean values and update IDs
    newEntry.querySelectorAll('input, textarea, label').forEach(el => {
      if (el.name) el.name = el.name.replace(/form-\d+/, `form-${currentIndex}`);
      if (el.id) el.id = el.id.replace(/form-\d+/, `form-${currentIndex}`);
      if (el.htmlFor) el.htmlFor = el.htmlFor.replace(/form-\d+/, `form-${currentIndex}`);
      if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') el.value = '';
    });

    entries.appendChild(newEntry);
    totalFormsInput.value = currentIndex + 1;

    // Add matching preview HTML
    const previewBlock = document.createElement('div');
    previewBlock.innerHTML = `
      <p><strong id="preview_job_title_${currentIndex}">Job Title</strong> at <span id="preview_company_${currentIndex}">Company Name</span></p>
      <p><em id="preview_dates_${currentIndex}">Start - End</em></p>
      <ul id="preview_description_bullets_${currentIndex}">
        <li>Responsibilities</li>
      </ul>
    `;
    previewContainer.appendChild(previewBlock);

    // Bind inputs to this preview block
    bindPreviewForIndex(currentIndex);
  });
});

function bindPreviewForIndex(index) {
  const titleId = `id_form-${index}-job_title`;
  const companyId = `id_form-${index}-company`;
  const startId = `id_form-${index}-start_date`;
  const endId = `id_form-${index}-end_date`;
  const descId = `id_form-${index}-description`;

  bindLivePreview(titleId, `preview_job_title_${index}`, 'Job Title');
  bindLivePreview(companyId, `preview_company_${index}`, 'Company Name');
  bindDateRangePreview(startId, endId, `preview_dates_${index}`);
  bindBulletPreview(descId, `preview_description_bullets_${index}`, 'Responsibilities');

  const presentCheckbox = document.querySelector(`input.present-checkbox[data-end-field-id="id_form-${index}-end_date"]`);
  if (presentCheckbox) {
    bindPresentCheckbox(presentCheckbox);
  }

}

function bindPresentCheckbox(checkbox) {
  checkbox.addEventListener('change', () => {
    const endInput = document.getElementById(checkbox.dataset.endFieldId);
    const preview = document.getElementById(checkbox.dataset.previewId);

    if (checkbox.checked) {
      endInput.disabled = true;
      const startInput = document.getElementById(endInput.id.replace('end_date', 'start_date'));
      const start = startInput?.value || 'Start';
      preview.textContent = `${start} - Present`;
    } else {
      endInput.disabled = false;
      // Rebind date preview normally
      const startId = endInput.id.replace('end_date', 'start_date');
      bindDateRangePreview(startId, endInput.id, checkbox.dataset.previewId);
    }
  });
}


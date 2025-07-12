// ========== Utility: Live Preview Binding ==========
function bindLivePreview(inputId, previewId, fallback = "") {
  const input = document.getElementById(inputId);
  const preview = document.getElementById(previewId);

  if (input && preview) {
    input.addEventListener("input", () => {
      preview.textContent = input.value.trim() || fallback;
    });

    // Initialize on load
    preview.textContent = input.value.trim() || fallback;
  }
}

// ========== Utility: Bullet List Preview ==========
function bindBulletPreview(textareaId, previewListId, fallback = "Responsibilities") {
  const textarea = document.getElementById(textareaId);
  const previewList = document.getElementById(previewListId);

  if (!textarea || !previewList) return;

  function updateBullets() {
    const lines = textarea.value.split("\n").filter(line => line.trim());
    previewList.innerHTML = "";

    if (lines.length === 0) {
      const li = document.createElement("li");
      li.textContent = fallback;
      previewList.appendChild(li);
    } else {
      lines.forEach(line => {
        const li = document.createElement("li");
        li.textContent = line.trim();
        previewList.appendChild(li);
      });
    }
  }

  textarea.addEventListener("input", updateBullets);
  updateBullets(); // on load
}

// ========== Utility: Date Range Preview ==========
function bindDateRangePreview(startId, endId, previewId) {
  const startInput = document.getElementById(startId);
  const endInput = document.getElementById(endId);
  const preview = document.getElementById(previewId);

  if (!preview) return;

  function updateRange() {
    const start = startInput?.value || "";
    const end = endInput?.value || "";
    preview.textContent = `${start} – ${end}`.trim() || "Start – End";
  }

  if (startInput) startInput.addEventListener("input", updateRange);
  if (endInput) endInput.addEventListener("input", updateRange);

  updateRange(); // on load
}

// ========== Main Preview Binder ==========
function bindDynamicExperiencePreviews() {
  const totalFormsInput = document.getElementById('id_form-TOTAL_FORMS');
  const totalForms = parseInt(totalFormsInput?.value || 1);
  const container = document.getElementById('experience-preview-container');
  if (!container) return;

  container.innerHTML = ''; // Clear previous preview blocks

  for (let i = 0; i < totalForms; i++) {
    const titleId = `id_form-${i}-job_title`;
    const companyId = `id_form-${i}-company`;
    const startId = `id_form-${i}-start_date`;
    const endId = `id_form-${i}-end_date`;
    const descId = `id_form-${i}-description`;

    const previewBlock = document.createElement('div');
    previewBlock.className = 'experience-preview-block';
    previewBlock.innerHTML = `
      <p>
        <strong><span id="preview_job_title_${i}">Job Title</span></strong>
        at <strong><span id="preview_company_${i}">Company Name</span></strong>
      </p>
      <p><em><span id="preview_dates_${i}">Start – End</span></em></p>
      <ul id="preview_description_bullets_${i}">
        <li>Responsibilities</li>
      </ul>
    `;
    container.appendChild(previewBlock);

    bindLivePreview(titleId, `preview_job_title_${i}`, "Job Title");
    bindLivePreview(companyId, `preview_company_${i}`, "Company Name");
    bindDateRangePreview(startId, endId, `preview_dates_${i}`);
    bindBulletPreview(descId, `preview_description_bullets_${i}`, "Responsibilities");
  }
}

// ========== Form Add Handler ==========
function handleExperienceFormAdd() {
  const addBtn = document.getElementById("add-experience-btn");
  const formContainer = document.getElementById("experience-entries");
  const totalForms = document.getElementById("id_form-TOTAL_FORMS");
  const templateHtml = document.getElementById("empty-form-template").innerHTML;

  if (!addBtn || !formContainer || !totalForms || !templateHtml) return;

  addBtn.addEventListener("click", () => {
    const formCount = parseInt(totalForms.value);
    const newFormHtml = templateHtml.replace(/__prefix__/g, formCount);

    const newEntry = document.createElement("div");
    newEntry.classList.add("experience-entry");
    newEntry.innerHTML = newFormHtml;

    formContainer.appendChild(newEntry);
    totalForms.value = formCount + 1;

    bindDynamicExperiencePreviews(); // rebuild preview section
  });
}

// ========== DOM Ready ==========
document.addEventListener("DOMContentLoaded", () => {
  if (document.getElementById('experience-form')) {
    bindDynamicExperiencePreviews();
    handleExperienceFormAdd();
  }
});

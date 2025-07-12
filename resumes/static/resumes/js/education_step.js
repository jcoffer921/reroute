// ========== Utility: Update a preview span based on input ==========
function bindLivePreview(inputId, previewId, fallback = "") {
  const input = document.getElementById(inputId);
  const preview = document.getElementById(previewId);

  if (input && preview) {
    input.addEventListener("input", () => {
      preview.textContent = input.value.trim() || fallback;
    });
  }
}

// ========== Utility: Format and update date range ==========
function bindDateRangePreview(startId, endId, previewId) {
  const startInput = document.getElementById(startId);
  const endInput = document.getElementById(endId);
  const preview = document.getElementById(previewId);

  function updateRange() {
    const start = startInput?.value || "";
    const end = endInput?.value || "";
    preview.textContent = `${start} – ${end}`.trim() || "Start – End";
  }

  if (startInput) startInput.addEventListener("input", updateRange);
  if (endInput) endInput.addEventListener("input", updateRange);
}

// ========== Main Preview Binder ==========
function bindDynamicEducationPreviews() {
  const totalFormsInput = document.getElementById('id_form-TOTAL_FORMS');
  const totalForms = parseInt(totalFormsInput?.value || 1);
  const container = document.getElementById('education-preview-container');
  if (!container) return;

  container.innerHTML = ''; // Clear previous preview blocks

  for (let i = 0; i < totalForms; i++) {
    const schoolId = `id_form-${i}-school`;
    const degreeId = `id_form-${i}-degree`;
    const startId = `id_form-${i}-start_date`;
    const endId = `id_form-${i}-end_date`;
    const descId = `id_form-${i}-description`;

    const previewBlock = document.createElement('div');
    previewBlock.className = 'education-preview-block';
    previewBlock.innerHTML = `
      <strong id="preview_school_${i}">School Name</strong><br>
      <em id="preview_degree_${i}">Degree</em><br>
      <span id="preview_edudates_${i}">Start – End</span>
      <p id="preview_edudesc_${i}">Course description</p>
      <hr>
    `;
    container.appendChild(previewBlock);

    bindLivePreview(schoolId, `preview_school_${i}`, "School Name");
    bindLivePreview(degreeId, `preview_degree_${i}`, "Degree");
    bindLivePreview(descId, `preview_edudesc_${i}`, "Course description");
    bindDateRangePreview(startId, endId, `preview_edudates_${i}`);
  }
}

// ========== Handle Form Additions ==========
function handleEducationFormAdd() {
  const addBtn = document.getElementById("add-education-btn");
  const formContainer = document.getElementById("education-form");
  const totalForms = document.getElementById("id_form-TOTAL_FORMS");
  const templateHtml = document.getElementById("empty-form-template").innerHTML;

  if (!addBtn || !formContainer || !totalForms || !templateHtml) return;

  addBtn.addEventListener("click", () => {
    const formCount = parseInt(totalForms.value);
    const newFormHtml = templateHtml.replace(/__prefix__/g, formCount);

    const newEntry = document.createElement("div");
    newEntry.classList.add("education-entry");
    newEntry.innerHTML = newFormHtml;

    formContainer.insertBefore(newEntry, document.querySelector(".form-navigation"));
    totalForms.value = formCount + 1;

    // Re-bind previews to all fields (rebuilds everything)
    bindDynamicEducationPreviews();
  });
}

// ========== DOM Ready ==========
document.addEventListener("DOMContentLoaded", () => {
  if (document.getElementById('education-form')) {
    bindDynamicEducationPreviews();
    handleEducationFormAdd();
  }
});

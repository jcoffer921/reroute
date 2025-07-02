
document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('education-form')) {
    bindDynamicEducationPreviews();
  }
});

document.addEventListener("DOMContentLoaded", () => {
  const addBtn = document.getElementById("add-education-btn");
  const formContainer = document.getElementById("education-form");
  const totalForms = document.getElementById("id_form-TOTAL_FORMS");
  const templateHtml = document.getElementById("empty-form-template").innerHTML;

  addBtn.addEventListener("click", () => {
    let formCount = parseInt(totalForms.value);
    let newFormHtml = templateHtml.replace(/__prefix__/g, formCount);
    
    // Create new div and insert new form HTML
    const newEntry = document.createElement("div");
    newEntry.classList.add("education-entry");
    newEntry.innerHTML = newFormHtml;

    // Insert above navigation buttons
    formContainer.insertBefore(newEntry, document.querySelector(".form-navigation"));

    // Update total forms count
    totalForms.value = formCount + 1;
  });
});

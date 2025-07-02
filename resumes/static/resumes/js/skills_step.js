document.addEventListener("DOMContentLoaded", function () {
  console.log("✅ skills_step.js loaded");

  const textarea = document.getElementById("skills_input");
  const preview = document.getElementById("preview_skills_list");

  if (!textarea || !preview) {
    console.warn("❌ Cannot find textarea or preview list");
    return;
  }

  function cleanLine(line) {
    return line.replace(/^[•\-\*\s]+/, '').trim();
  }

  function updatePreview() {
    const lines = textarea.value.split('\n').map(cleanLine).filter(Boolean);
    preview.innerHTML = "";

    if (lines.length === 0) {
      const fallback = document.createElement("li");
      fallback.textContent = "Skill Name";
      preview.appendChild(fallback);
    } else {
      lines.forEach(skill => {
        const li = document.createElement("li");
        li.textContent = skill;
        preview.appendChild(li);
      });
    }
  }

  textarea.addEventListener("input", updatePreview);
  updatePreview(); // run once on page load
});

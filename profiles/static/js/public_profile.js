document.addEventListener('DOMContentLoaded', () => {
  // ===== Section Tabs (e.g., Profile, Resume, etc.) =====
  const tabButtons = document.querySelectorAll('.tab-button');
  const tabSections = document.querySelectorAll('.tab-section');

  tabButtons.forEach(btn => {
    btn.addEventListener('click', function () {
      const targetId = this.getAttribute('data-target');
      tabSections.forEach(section => section.style.display = 'none');
      tabButtons.forEach(b => b.classList.remove('active-tab'));

      const targetSection = document.getElementById(targetId);
      if (targetSection) {
        targetSection.style.display = 'block';
        this.classList.add('active-tab');
      }
    });
  });

  // ===== Generic Slide Panel Logic =====
  const slideConfigs = [
    {
      triggerId: 'editSlideTrigger',
      panelId: 'slideEditor',
      cancelId: 'cancelSlide',
      formId: 'personalSlideForm',
      saveBtnId: 'saveSlide',
    },
    {
      triggerId: 'editEmploymentTrigger',
      panelId: 'employmentSlideEditor',
      cancelId: 'cancelEmploymentSlide',
      formId: 'employmentSlideForm',
      saveBtnId: 'saveEmploymentSlide',
    },
  ];

  slideConfigs.forEach(config => {
    const trigger = document.getElementById(config.triggerId);
    const panel = document.getElementById(config.panelId);
    const cancelBtn = document.getElementById(config.cancelId);
    const form = document.getElementById(config.formId);
    const saveBtn = document.getElementById(config.saveBtnId);
    const btnText = saveBtn?.querySelector('.btn-text');
    const spinner = saveBtn?.querySelector('.spinner');

    if (trigger && panel) {
      trigger.addEventListener('click', () => {
        panel.classList.add('visible');
      });
    }

    if (cancelBtn && panel) {
      cancelBtn.addEventListener('click', () => {
        panel.classList.remove('visible');
      });
    }

    if (form && saveBtn) {
      form.addEventListener('submit', function (e) {
        e.preventDefault();

        // Show spinner, hide button text
        spinner.style.display = 'inline-block';
        btnText.style.display = 'none';

        fetch(form.action, {
          method: 'POST',
          headers: { 'X-Requested-With': 'XMLHttpRequest' },
          body: new FormData(form),
        })
          .then(response => response.json())
          .then(data => {
            spinner.style.display = 'none';
            btnText.style.display = 'inline';
            if (data.success) {
              panel.classList.remove('visible');
              location.reload();
            } else {
              alert('❌ Failed to save. Please try again.');
            }
          })
          .catch(() => {
            spinner.style.display = 'none';
            btnText.style.display = 'inline';
            alert('❌ Server error.');
          });
      });
    }
  });

  // ===== Button Toggle Groups (e.g., Gender or Status Selectors) =====
  document.querySelectorAll('.btn-toggle-group').forEach(group => {
    const hiddenInput = group.nextElementSibling;

    group.querySelectorAll('button').forEach(btn => {
      btn.addEventListener('click', () => {
        group.querySelectorAll('button').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        hiddenInput.value = btn.dataset.value;
      });
    });
  });

  // ===== Emergency + Demographics Panel Triggers =====
  const emergencyTrigger = document.getElementById("editEmergencyTrigger");
  const demographicsTrigger = document.getElementById("editDemographicsTrigger");

  emergencyTrigger?.addEventListener('click', () => {
    document.getElementById("emergencySlidePanel").style.right = "0";
  });

  demographicsTrigger?.addEventListener('click', () => {
    document.getElementById("demographicsSlidePanel").style.right = "0";
  });
});

// ===== Close any slide-in panel by ID =====
function closePanel(panelId) {
  document.getElementById(panelId).style.right = "-100%";
}

document.addEventListener('DOMContentLoaded', () => {
  const phoneInput = document.getElementById('phone_number');
  const emergencyPhoneInput = document.getElementById('emergency_contact_phone');

  phoneInput?.addEventListener('input', function (e) {
    let input = e.target.value.replace(/\D/g, ''); // Remove non-digit characters

    // Format: 123-456-7890
    if (input.length > 3 && input.length <= 6) {
      input = `${input.slice(0, 3)}-${input.slice(3)}`;
    } else if (input.length > 6) {
      input = `${input.slice(0, 3)}-${input.slice(3, 6)}-${input.slice(6, 10)}`;
    }

    e.target.value = input;
  });

  emergencyPhoneInput?.addEventListener('input', function (e) {
    let input = e.target.value.replace(/\D/g, ''); // Remove non-digit characters

    // Format: 123-456-7890
    if (input.length > 3 && input.length <= 6) {
      input = `${input.slice(0, 3)}-${input.slice(3)}`;
    } else if (input.length > 6) {
      input = `${input.slice(0, 3)}-${input.slice(3, 6)}-${input.slice(6, 10)}`;
    }

    e.target.value = input;
  });
});

function handleProfilePicChange(input) {
  const file = input.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = function(e) {
      document.getElementById("previewImage").src = e.target.result;
      document.getElementById("profilePicModal").style.display = "block";
      document.getElementById("modalPicInput").files = input.files;
    };
    reader.readAsDataURL(file);
  }
}

function closeModal() {
  document.getElementById("profilePicModal").style.display = "none";
}

function removeProfilePicture() {
  window.location.href = "{% url 'remove_profile_picture' %}";
}

function toggleBio() {
  const preview = document.getElementById('bioPreview');
  const full = document.getElementById('fullBio');
  preview.style.display = 'none';
  full.style.display = 'block';
}

function toggleBioEdit() {
  const form = document.getElementById('editBioForm');
  form.style.display = form.style.display === 'none' ? 'block' : 'none';
}
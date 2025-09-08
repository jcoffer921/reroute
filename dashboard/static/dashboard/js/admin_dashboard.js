// Ensure DOM is loaded before running
document.addEventListener("DOMContentLoaded", () => {
  const { dates, usersByDay, jobsByDay } = window.dashboardData || { dates: [], usersByDay: [], jobsByDay: [] };

  // Chart: Users Growth
  const ctxUsers = document.getElementById("usersChart").getContext("2d");
  new Chart(ctxUsers, {
    type: "line",
    data: {
      labels: dates,
      datasets: [{
        label: "New Users",
        data: usersByDay,
        borderColor: "#0d6efd",
        backgroundColor: "rgba(13, 110, 253, 0.15)",
        fill: true,
        tension: 0.3,
        pointRadius: 0
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: true, labels: { boxWidth: 12 } }
      },
      scales: {
        x: { grid: { display: false } },
        y: { grid: { color: 'rgba(0,0,0,0.05)' } }
      }
    }
  });

  // Chart: Jobs Growth
  const ctxJobs = document.getElementById("jobsChart").getContext("2d");
  new Chart(ctxJobs, {
    type: "line",
    data: {
      labels: dates,
      datasets: [{
        label: "New Jobs",
        data: jobsByDay,
        borderColor: "#198754",
        backgroundColor: "rgba(25, 135, 84, 0.15)",
        fill: true,
        tension: 0.3,
        pointRadius: 0
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: true, labels: { boxWidth: 12 } }
      },
      scales: {
        x: { grid: { display: false } },
        y: { grid: { color: 'rgba(0,0,0,0.05)' } }
      }
    }
  });

  // Modal confirmation for inline admin actions
  const modal = document.getElementById('confirmModal');
  const msgEl = document.getElementById('confirmModalMessage');
  const btnOk = document.getElementById('confirmOk');
  const btnCancel = document.getElementById('confirmCancel');
  const backdrop = document.querySelector('.rr-modal__backdrop');
  let pendingForm = null;

  function openModal(message, form) {
    pendingForm = form;
    if (msgEl) msgEl.textContent = message || 'Are you sure?';
    if (modal) {
      modal.classList.add('open');
      modal.setAttribute('aria-hidden', 'false');
    }
  }
  function closeModal() {
    if (modal) {
      modal.classList.remove('open');
      modal.setAttribute('aria-hidden', 'true');
    }
    pendingForm = null;
  }

  if (btnOk) {
    btnOk.addEventListener('click', () => {
      if (pendingForm) pendingForm.submit();
      closeModal();
    });
  }
  if (btnCancel) btnCancel.addEventListener('click', closeModal);
  if (backdrop) backdrop.addEventListener('click', closeModal);
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeModal();
  });

  document.querySelectorAll('form.js-confirm').forEach(form => {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const message = form.dataset.message || 'Are you sure?';
      openModal(message, form);
    });
  });
});

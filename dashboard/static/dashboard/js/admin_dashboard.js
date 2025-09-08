// Ensure DOM is loaded before running
document.addEventListener("DOMContentLoaded", () => {
  const {
    dates = [],
    usersByDay = [],
    jobsByDay = [],
    applicationsByDay = [],
    employersByDay = []
  } = window.dashboardData || {};

  // Chart: Users Growth
  const ctxUsers = document.getElementById("usersChart").getContext("2d");
  const usersChart = new Chart(ctxUsers, {
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
  const jobsChart = new Chart(ctxJobs, {
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

  // Optional charts: Applications and Employers
  let applicationsChart = null;
  const appCanvas = document.getElementById('applicationsChart');
  if (appCanvas && Array.isArray(applicationsByDay) && applicationsByDay.length) {
    const ctxApps = appCanvas.getContext('2d');
    applicationsChart = new Chart(ctxApps, {
      type: 'line',
      data: {
        labels: dates,
        datasets: [{
          label: 'New Applications',
          data: applicationsByDay,
          borderColor: '#fd7e14',
          backgroundColor: 'rgba(253, 126, 20, 0.15)',
          fill: true,
          tension: 0.3,
          pointRadius: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: true, labels: { boxWidth: 12 } } },
        scales: { x: { grid: { display: false } }, y: { grid: { color: 'rgba(0,0,0,0.05)' } } }
      }
    });
  }

  let employersChart = null;
  const empCanvas = document.getElementById('employersChart');
  if (empCanvas && Array.isArray(employersByDay) && employersByDay.length) {
    const ctxEmp = empCanvas.getContext('2d');
    employersChart = new Chart(ctxEmp, {
      type: 'line',
      data: {
        labels: dates,
        datasets: [{
          label: 'New Employers',
          data: employersByDay,
          borderColor: '#17a2b8',
          backgroundColor: 'rgba(23, 162, 184, 0.15)',
          fill: true,
          tension: 0.3,
          pointRadius: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: true, labels: { boxWidth: 12 } } },
        scales: { x: { grid: { display: false } }, y: { grid: { color: 'rgba(0,0,0,0.05)' } } }
      }
    });
  }

  // Remove slides without data
  document.querySelectorAll('.charts-carousel__slide').forEach(slide => {
    const canvas = slide.querySelector('canvas');
    const id = canvas ? canvas.id : '';
    const hasChart = (
      (id === 'usersChart' && usersChart) ||
      (id === 'jobsChart' && jobsChart) ||
      (id === 'applicationsChart' && applicationsChart) ||
      (id === 'employersChart' && employersChart)
    );
    if (!hasChart) slide.remove();
  });

  // Simple charts carousel
  const carousel = document.querySelector('.charts-carousel');
  if (carousel) {
    const track = carousel.querySelector('.charts-carousel__track');
    let slides = Array.from(carousel.querySelectorAll('.charts-carousel__slide'));
    const prevBtn = carousel.querySelector('.charts-carousel__nav--prev');
    const nextBtn = carousel.querySelector('.charts-carousel__nav--next');
    const dotsWrap = carousel.querySelector('.charts-carousel__dots');

    let index = 0;

    // Build dots
    slides.forEach((_, i) => {
      const b = document.createElement('button');
      b.type = 'button';
      b.setAttribute('role', 'tab');
      b.setAttribute('aria-controls', `chart-slide-${i}`);
      b.setAttribute('aria-selected', i === 0 ? 'true' : 'false');
      b.addEventListener('click', () => goTo(i));
      dotsWrap.appendChild(b);
    });

    // Label slides for a11y
    slides.forEach((slide, i) => slide.id = `chart-slide-${i}`);

    function update() {
      slides = Array.from(carousel.querySelectorAll('.charts-carousel__slide'));
      track.style.transform = `translateX(-${index * 100}%)`;
      dotsWrap.querySelectorAll('button').forEach((b, i) => b.setAttribute('aria-selected', i === index ? 'true' : 'false'));
      // Ensure visible chart resizes correctly
      setTimeout(() => {
        if (index === 0 && usersChart) usersChart.resize();
        if (index === 1 && jobsChart) jobsChart.resize();
        if (index === 2 && applicationsChart) applicationsChart.resize();
        if (index === 3 && employersChart) employersChart.resize();
      }, 0);
      // Toggle controls if only one slide
      const show = slides.length > 1;
      [prevBtn, nextBtn, dotsWrap].forEach(el => { if (el) el.style.display = show ? '' : 'none'; });
    }

    function goTo(i) {
      index = Math.max(0, Math.min(slides.length - 1, i));
      update();
    }

    function next() { goTo(index + 1); }
    function prev() { goTo(index - 1); }

    if (nextBtn) nextBtn.addEventListener('click', next);
    if (prevBtn) prevBtn.addEventListener('click', prev);

    // Swipe support
    let startX = 0, dx = 0;
    const threshold = 40;
    track.addEventListener('touchstart', (e) => { startX = e.touches[0].clientX; dx = 0; }, { passive: true });
    track.addEventListener('touchmove', (e) => { dx = e.touches[0].clientX - startX; }, { passive: true });
    track.addEventListener('touchend', () => {
      if (dx > threshold) prev();
      else if (dx < -threshold) next();
      dx = 0;
    });

    // Keyboard arrows when focused within carousel
    carousel.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowRight') next();
      if (e.key === 'ArrowLeft') prev();
    });

    // Autoplay with pause-on-hover and visibility
    let timer = null;
    const delay = 5000;
    function start() {
      if (timer || slides.length <= 1) return;
      timer = setInterval(() => goTo((index + 1) % slides.length), delay);
    }
    function stop() { if (timer) { clearInterval(timer); timer = null; } }
    carousel.addEventListener('mouseenter', stop);
    carousel.addEventListener('mouseleave', start);
    carousel.addEventListener('touchstart', stop, { passive: true });
    carousel.addEventListener('touchend', start, { passive: true });
    document.addEventListener('visibilitychange', () => { document.hidden ? stop() : start(); });

    // Initial position
    update();
    start();
  }

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

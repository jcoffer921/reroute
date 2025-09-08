// Simple client-side filtering for notifications tabs
(function() {
  const tabs = document.querySelectorAll('.notifications-tabs .tab');
  const cards = document.querySelectorAll('.notification-card');

  function setActive(tab) {
    tabs.forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    const filter = tab.getAttribute('data-filter');
    cards.forEach(c => {
      if (filter === 'all') {
        c.style.display = '';
      } else {
        c.style.display = (c.getAttribute('data-type') === filter) ? '' : 'none';
      }
    });
  }

  tabs.forEach(tab => tab.addEventListener('click', () => setActive(tab)));
})();


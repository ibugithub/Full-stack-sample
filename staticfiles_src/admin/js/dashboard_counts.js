(() => {
  const root = document.querySelector('[data-dashboard-counts-url]');
  const counters = document.querySelectorAll('[data-dashboard-count]');
  if (!root || !counters.length) return;
  fetch(root.dataset.dashboardCountsUrl, { credentials: 'same-origin', headers: { Accept: 'application/json' } })
    .then((response) => { if (!response.ok) throw new Error('Counts unavailable'); return response.json(); })
    .then(({ counts }) => counters.forEach((element) => {
      const count = counts[element.dataset.dashboardCount];
      if (!count) return;
      element.textContent = `${count.value} ${count.label}`;
      element.setAttribute('aria-label', `${count.value} ${count.label} ${element.dataset.countName}`);
    }))
    .catch(() => counters.forEach((element) => { element.textContent = 'Unavailable'; }));
})();

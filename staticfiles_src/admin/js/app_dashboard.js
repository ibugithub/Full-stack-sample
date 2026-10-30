(() => {
  const search = document.querySelector('[data-directory-input]');
  if (search) {
    const rows = [...document.querySelectorAll('[data-directory-feature]')];
    document.querySelector('[data-directory-search]').hidden = false;
    search.addEventListener('input', () => {
      const query = search.value.trim().toLocaleLowerCase();
      rows.forEach((row) => { row.hidden = !row.dataset.featureName.toLocaleLowerCase().includes(query); });
      document.querySelector('[data-directory-empty]').hidden = rows.some((row) => !row.hidden);
    });
  }
  const account = document.querySelector('.app-account-menu');
  if (account) {
    document.addEventListener('pointerdown', (event) => {
      if (!account.contains(event.target)) account.open = false;
    });
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && account.open) {
        account.open = false;
        account.querySelector('summary').focus();
      }
    });
  }
})();

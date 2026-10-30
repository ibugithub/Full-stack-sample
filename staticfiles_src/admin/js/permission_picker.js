(() => {
  function initialize() {
    document.querySelectorAll('[data-permission-picker]').forEach((picker) => {
      if (picker.dataset.initialized) return;
      picker.dataset.initialized = 'true';
      const search = picker.querySelector('[data-permission-search]');
      const features = [...picker.querySelectorAll('[data-permission-feature]')];
      const selectedFilter = picker.querySelector('[data-picker-selected]');
      const selectAll = picker.querySelector('[data-picker-select-all]');
      const superuserField = picker.dataset.superuserField;
      const effectiveEditor = picker.dataset.effectiveEditor === 'true';
      const superuserInput = superuserField ? document.getElementById(superuserField) : null;
      const superuserNotice = picker.querySelector('[data-superuser-notice]');
      const updateAutomaticAccess = () => {
        if (!superuserNotice) return;
        const enabled = superuserInput ? superuserInput.checked : !superuserNotice.hidden;
        superuserNotice.hidden = !enabled;
        updateCount();
        filterRows();
      };
      const visibleChoices = () => features.filter((feature) => !feature.hidden)
        .flatMap((feature) => [...feature.querySelectorAll('input[type="checkbox"]:not(:disabled)')]);
      let selectedOnly = false;
      const updateCount = () => {
        picker.querySelector('[data-permission-count]').textContent =
          `${picker.querySelectorAll('input[type="checkbox"]:checked').length} selected`;
      };
      const filterRows = () => {
        const query = search.value.trim().toLocaleLowerCase();
        features.forEach((feature) => {
          feature.hidden = !feature.textContent.toLocaleLowerCase().includes(query)
            || (selectedOnly && !feature.querySelector('input:checked'));
        });
        picker.querySelector('[data-permission-empty]').hidden = features.some((feature) => !feature.hidden);
        if (selectAll) {
          const choices = visibleChoices();
          const allChecked = choices.length > 0 && choices.every((input) => input.checked);
          selectAll.disabled = choices.length === 0;
          selectAll.textContent = allChecked ? 'Clear selection' : 'Select all';
          selectAll.title = `${allChecked ? 'Clear' : 'Select'} permissions in the currently visible rows`;
        }
      };
      const reconcileSuperuser = () => {
        if (effectiveEditor && superuserInput?.checked
            && [...picker.querySelectorAll('input[type="checkbox"]')].some((input) => !input.checked)) {
          superuserInput.checked = false;
          superuserInput.dispatchEvent(new Event('change', { bubbles: true }));
        }
      };
      selectAll?.addEventListener('click', () => {
        const choices = visibleChoices();
        const checked = !choices.every((input) => input.checked);
        choices.forEach((input) => { input.checked = checked; });
        reconcileSuperuser();
        updateCount();
        filterRows();
      });
      search.addEventListener('input', filterRows);
      selectedFilter.addEventListener('click', () => {
        selectedOnly = !selectedOnly;
        selectedFilter.setAttribute('aria-pressed', String(selectedOnly));
        filterRows();
      });
      picker.addEventListener('change', () => { reconcileSuperuser(); updateCount(); filterRows(); });
      superuserInput?.addEventListener('change', () => {
        if (effectiveEditor && superuserInput.checked) {
          picker.querySelectorAll('input[type="checkbox"]:not(:disabled)').forEach((input) => { input.checked = true; });
        }
        updateAutomaticAccess();
      });
      updateAutomaticAccess();
      updateCount();
      filterRows();
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initialize);
  else initialize();
})();

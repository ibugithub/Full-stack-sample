(() => {
  const table = document.querySelector('#changelist-form .results');
  const hint = document.querySelector('[data-table-hint]');
  if (!table || !hint) return;
  const records = table.querySelector('#result_list');
  if (!records) return;
  const headers = [...records.querySelectorAll('thead th')];
  const rows = [...records.querySelectorAll('tbody tr')];
  rows.forEach((row) => {
    [...row.cells].forEach((cell, index) => {
      cell.dataset.columnLabel = headers[index]?.querySelector('.text')?.textContent.trim() || '';
      if (cell.colSpan > 1) cell.classList.add('app-record-error');
    });
    const primary = row.querySelector('th') || row.querySelector('td:not(.action-checkbox)');
    primary?.classList.add('app-record-primary');
    if (document.body.classList.contains('model-product')) {
      const status = row.querySelector('.field-status select');
      const updateStatus = () => {
        row.dataset.productStatus = status?.value || row.querySelector('.field-status')?.textContent.trim().toLowerCase() || '';
      };
      status?.addEventListener('change', updateStatus);
      updateStatus();
    }
  });
  let toolbar = document.querySelector('#toolbar');
  if (!toolbar) {
    toolbar = document.createElement('div');
    toolbar.id = 'toolbar';
    document.querySelector('.changelist-form-container').prepend(toolbar);
  }
  const tools = document.createElement('div');
  tools.className = 'app-record-tools';
  toolbar.append(tools);
  const filters = document.querySelector('#changelist-filter');
  if (filters) tools.append(filters);
  const sortLinks = headers.map((header) => {
    const link = header.querySelector('.text a');
    if (!link) return null;
    const item = document.createElement('a');
    const direction = header.querySelector('.toggle');
    item.href = direction?.href || link.href;
    item.textContent = `${link.textContent.trim()}${direction ? (direction.classList.contains('ascending') ? ' ↑' : ' ↓') : ''}`;
    if (direction) {
      item.classList.add('is-selected');
      item.setAttribute('aria-current', 'true');
      item.title = `Reverse ${link.textContent.trim()} sorting`;
    }
    return item;
  }).filter(Boolean);
  if (sortLinks.length) {
    const sort = document.createElement('section');
    sort.className = 'app-record-sort';
    sort.setAttribute('aria-label', 'Sort records');
    const heading = document.createElement('div');
    heading.className = 'app-filter-section-heading';
    const title = document.createElement('span');
    title.className = 'app-quick-filter__title';
    title.textContent = 'Sort by';
    const options = document.createElement('div');
    options.className = 'app-filter-pills';
    options.setAttribute('role', 'group');
    options.setAttribute('aria-label', 'Quick sorting choices');
    const extra = [];
    const quick = [
      ...sortLinks.filter((link) => link.classList.contains('is-selected')),
      ...sortLinks.filter((link) => !link.classList.contains('is-selected')),
    ].slice(0, 3);
    sortLinks.forEach((link) => {
      if (quick.includes(link)) options.append(link);
      else extra.push(link);
    });
    const currentUrl = new URL(window.location.href);
    if (currentUrl.searchParams.has('o')) {
      currentUrl.searchParams.delete('o');
      const reset = document.createElement('a');
      reset.href = currentUrl.href;
      reset.textContent = 'Clear sorting ×';
      heading.append(reset);
      sort.append(heading);
      const applied = document.createElement('div');
      applied.className = 'app-applied-filters';
      const selected = document.createElement('a');
      selected.href = currentUrl.href;
      const names = sortLinks.filter((link) => link.classList.contains('is-selected')).map((link) => link.textContent).join(', ');
      selected.textContent = `Sort: ${names || 'Custom'} ×`;
      selected.setAttribute('aria-label', 'Remove selected sorting');
      applied.append(selected);
      sort.append(applied);
    }
    sort.append(title, options);
    if (extra.length) {
      const more = document.createElement('details');
      more.className = 'app-filter-more';
      const summary = document.createElement('summary');
      summary.textContent = 'More sorting options';
      const plus = document.createElement('span');
      plus.setAttribute('aria-hidden', 'true');
      plus.textContent = '+';
      summary.append(plus);
      const remaining = document.createElement('div');
      remaining.className = 'app-filter-pills';
      extra.forEach((link) => remaining.append(link));
      more.append(summary, remaining);
      sort.append(more);
    }
    tools.append(sort);
  }
  const all = document.querySelector('#action-toggle');
  const checkboxes = [...records.querySelectorAll('input.action-select')];
  const actions = document.querySelectorAll('#changelist-form .actions');
  actions.forEach((action) => {
    const nativeSelect = action.querySelector('select[name="action"]');
    const run = action.querySelector('button[name="index"]');
    if (!nativeSelect || !run) return;
    action.querySelector('.action-counter')?.setAttribute('aria-live', 'polite');
    const buttons = document.createElement('div');
    buttons.className = 'app-action-buttons';
    [...nativeSelect.options].filter((option) => option.value).forEach((option) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = option.value === 'delete_selected' ? 'app-action-delete' : 'app-action-run';
      button.textContent = option.value === 'delete_selected' ? 'Delete selected' : option.textContent;
      button.title = option.textContent;
      button.addEventListener('click', () => {
        nativeSelect.value = option.value;
        // Keep Django's unsaved-edit warning and native confirmation workflow.
        run.click();
      });
      buttons.append(button);
    });
    const clear = document.createElement('button');
    clear.type = 'button';
    clear.className = 'app-action-clear';
    clear.textContent = 'Deselect all';
    clear.addEventListener('click', () => {
      if (all) {
        all.checked = true;
        all.click();
      }
      nativeSelect.value = '';
    });
    action.append(clear, buttons);
    nativeSelect.closest('label').classList.add('app-native-action');
    run.classList.add('app-native-action');
    action.classList.add('app-modern-actions');
  });
  let selectAll;
  if (all) {
    const label = document.createElement('label');
    label.className = 'app-record-select-all';
    selectAll = document.createElement('input');
    selectAll.type = 'checkbox';
    selectAll.addEventListener('change', () => {
      if (all.checked !== selectAll.checked) all.click();
    });
    label.append(selectAll, document.createTextNode('Select all'));
    tools.append(label);
  }
  const syncSelection = () => {
    const count = checkboxes.filter((checkbox) => checkbox.checked).length;
    actions.forEach((action) => { action.hidden = count === 0; });
    if (selectAll) {
      selectAll.checked = count > 0 && count === checkboxes.length;
      selectAll.indeterminate = count > 0 && count < checkboxes.length;
    }
  };
  document.querySelector('#changelist-form').addEventListener('click', () => queueMicrotask(syncSelection));
  document.querySelector('#changelist-form').addEventListener('change', syncSelection);
  window.addEventListener('pageshow', syncSelection);
  syncSelection();
  document.body.classList.add('app-record-layout');
  const mobile = window.matchMedia('(max-width: 767px)');
  const headerControls = [...records.querySelectorAll('thead a, thead input')];
  const update = () => {
    headerControls.forEach((control) => {
      if (mobile.matches) control.tabIndex = -1;
      else control.removeAttribute('tabindex');
    });
    const overflows = table.scrollWidth > table.clientWidth + 1;
    hint.hidden = !overflows;
    if (overflows) {
      table.tabIndex = 0;
      table.setAttribute('role', 'region');
      table.setAttribute('aria-label', 'Records table. Scroll horizontally for more columns.');
    } else {
      table.removeAttribute('tabindex');
      table.removeAttribute('role');
      table.removeAttribute('aria-label');
    }
  };
  update();
  mobile.addEventListener('change', update);
  if ('ResizeObserver' in window) new ResizeObserver(update).observe(table);
  else window.addEventListener('resize', update);
})();

/* Toggle native Django form widgets in place; Django handles saves and validation. */
document.addEventListener('DOMContentLoaded', () => {
  const page = document.querySelector('[data-record-page]');
  if (!page) return;

  const editor = document.getElementById('app-record-editor');
  const details = document.getElementById('app-record-readonly');
  const form = document.getElementById('app-record-form');
  const editButton = page.querySelector('[data-record-edit]');
  if (!editor || !details || !form || !editButton) return;

  let dirty = false;
  let submitting = false;
  const setEditing = (editing, focus = true) => {
    editor.hidden = !editing;
    details.hidden = editing;
    editButton.hidden = editing;
    editButton.setAttribute('aria-expanded', String(editing));
    page.querySelectorAll('[data-editor-action]').forEach((button) => {
      button.hidden = !editing;
    });
    page.querySelector('.app-editor-message').hidden = !editing;
    const description = page.querySelector('[data-record-description]');
    if (description) description.hidden = editing;
    if (focus) {
      const target = editing
        ? form.querySelector('.errorlist + input, input:not([type="hidden"]):not([type="checkbox"]):not([type="submit"]), textarea, select')
        : editButton;
      target?.focus({ preventScroll: true });
    }
  };

  editButton.addEventListener('click', () => setEditing(true));
  page.querySelectorAll('[data-record-cancel]').forEach((button) => {
    button.addEventListener('click', () => {
      if (dirty && !window.confirm('Discard your unsaved changes?')) return;
      // Reload only when needed to reset inline rows, file widgets and validation.
      if (dirty || page.dataset.editing === 'true') {
        dirty = false;
        const url = new URL(window.location.href);
        url.searchParams.delete('edit');
        window.location.replace(url);
      } else {
        setEditing(false);
      }
    });
  });
  form.addEventListener('input', () => { dirty = true; });
  form.addEventListener('change', () => { dirty = true; });
  // Django's autocomplete and other enhanced widgets emit jQuery changes.
  window.django?.jQuery(form).on('change', ':input', () => { dirty = true; });
  // Inline add/remove buttons change the form without a normal input event.
  form.addEventListener('click', (event) => {
    if (event.target.closest('.add-row a, .inline-deletelink')) dirty = true;
  });
  form.addEventListener('submit', (event) => {
    if (submitting) {
      event.preventDefault();
      return;
    }
    submitting = true;
    page.querySelectorAll('button[type="submit"], input[type="submit"]').forEach((button) => {
      button.setAttribute('aria-disabled', 'true');
      if (button.tagName === 'BUTTON') button.textContent = 'Saving...';
      else button.value = 'Saving...';
    });
  });
  window.addEventListener('beforeunload', (event) => {
    if (!dirty || submitting) return;
    event.preventDefault();
    event.returnValue = '';
  });
  setEditing(page.dataset.editing === 'true', false);
});

/* No network probes: use the browser's image load/error events for previews. */
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-image-preview]').forEach((preview) => {
    const image = preview.querySelector('[data-preview-image]');
    if (!image) return;

    const placeholder = preview.querySelector('[data-image-placeholder]');
    const link = image.closest('a');
    const ready = () => {
      placeholder.hidden = true;
      preview.classList.add('app-image-ready');
      link.removeAttribute('aria-hidden');
      link.removeAttribute('tabindex');
      preview.querySelector('[data-image-enlarge]').hidden = false;
    };
    const unavailable = () => {
      preview.classList.remove('app-image-ready');
      placeholder.hidden = false;
      link.hidden = true;
      preview.querySelector('[data-image-message]').textContent = 'Image unavailable';
      preview.querySelector('[data-image-hint]').textContent = 'The saved image could not be loaded. You can replace it when editing.';
      preview.querySelector('[data-image-enlarge]').hidden = true;
    };

    image.addEventListener('load', ready);
    image.addEventListener('error', unavailable);
    // Cached images may finish before the event listeners are attached.
    if (image.complete) {
      if (image.naturalWidth > 0) ready();
      else unavailable();
    }
  });
});

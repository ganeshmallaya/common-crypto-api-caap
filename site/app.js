(() => {
  const config = window.CAAP_SITE_CONFIG || {};

  const root = document.documentElement;
  const toggle = document.querySelector('.theme-toggle');
  let savedTheme;
  try {
    savedTheme = localStorage.getItem('theme');
  } catch {
    savedTheme = undefined;
  }
  const initialTheme =
    savedTheme === 'dark' || savedTheme === 'light'
      ? savedTheme
      : window.matchMedia?.('(prefers-color-scheme: dark)').matches
        ? 'dark'
        : 'light';
  root.dataset.theme = initialTheme;
  toggle?.setAttribute('aria-pressed', String(initialTheme === 'dark'));
  toggle?.addEventListener('click', () => {
    const next = root.dataset.theme === 'dark' ? 'light' : 'dark';
    root.dataset.theme = next;
    try {
      localStorage.setItem('theme', next);
    } catch {
      // Theme selection remains valid for this page even when storage is denied.
    }
    toggle.setAttribute('aria-pressed', String(next === 'dark'));
  });

  const architectureDetail = document.querySelector('.architecture-detail');
  const architectureChoices = document.querySelectorAll('[data-architecture-title]');
  architectureChoices.forEach((choice) => {
    choice.addEventListener('click', () => {
      architectureChoices.forEach((item) => {
        if (item.hasAttribute('aria-pressed')) item.setAttribute('aria-pressed', 'false');
      });
      if (choice.hasAttribute('aria-pressed')) choice.setAttribute('aria-pressed', 'true');
      const title = architectureDetail?.querySelector('h3');
      const detail = architectureDetail?.querySelector('p');
      if (title) title.textContent = choice.dataset.architectureTitle || '';
      if (detail) detail.textContent = choice.dataset.architectureDetail || '';
    });
  });

  if (!config.contentProtectionEnabled) return;

  // Presentation deterrent only. This is not authentication, authorization,
  // DRM, or a control for content already delivered to a browser.
  document.documentElement.classList.add('content-deterrent-enabled');
  const protectedRoot = document.querySelector('[data-research-content]');
  const inside = (event) =>
    protectedRoot && event.target instanceof Node && protectedRoot.contains(event.target);

  ['copy', 'cut', 'contextmenu', 'dragstart'].forEach((name) => {
    document.addEventListener(name, (event) => {
      if (inside(event)) event.preventDefault();
    });
  });
})();

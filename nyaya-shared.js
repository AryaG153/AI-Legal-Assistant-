(() => {
  const routes = [
    'dashboard.html',
    'ai-assistant.html',
    'knowledge-hub.html',
    'constitutional-articles.html',
    'acts-laws.html',
    'rights-hub.html',
    'consultation-history.html',
  ];

  const currentPage = window.location.pathname.split('/').pop() || 'login.html';
  const isAppPage = routes.includes(currentPage);

  const ensureBackdrop = () => {
    let backdrop = document.querySelector('[data-nyaya-backdrop]');
    if (!backdrop) {
      backdrop = document.createElement('div');
      backdrop.className = 'nyaya-sidebar-backdrop';
      backdrop.setAttribute('data-nyaya-backdrop', 'true');
      document.body.appendChild(backdrop);
    }
    return backdrop;
  };

  const openSidebar = () => {
    const sidebar = document.querySelector('[data-nyaya-sidebar]');
    const backdrop = ensureBackdrop();
    if (!sidebar) {
      return;
    }
    sidebar.classList.add('nyaya-sidebar-open');
    backdrop.classList.add('is-visible');
    document.body.classList.add('nyaya-nav-open');
  };

  const closeSidebar = () => {
    const sidebar = document.querySelector('[data-nyaya-sidebar]');
    const backdrop = document.querySelector('[data-nyaya-backdrop]');
    if (sidebar) {
      sidebar.classList.remove('nyaya-sidebar-open');
    }
    if (backdrop) {
      backdrop.classList.remove('is-visible');
    }
    document.body.classList.remove('nyaya-nav-open');
  };

  const setActiveLink = () => {
    document.querySelectorAll('[data-nyaya-sidebar] a[href]').forEach((link) => {
      const target = link.getAttribute('href');
      const isActive = target === currentPage;
      link.classList.toggle('is-active', isActive);
      if (isActive) {
        link.setAttribute('aria-current', 'page');
      } else {
        link.removeAttribute('aria-current');
      }
    });
  };

  const wireSidebarControls = () => {
    const toggleButtons = document.querySelectorAll('[data-nyaya-menu-button]');
    const backdrop = ensureBackdrop();

    toggleButtons.forEach((button) => {
      button.addEventListener('click', () => {
        const sidebar = document.querySelector('[data-nyaya-sidebar]');
        if (!sidebar) {
          return;
        }
        if (sidebar.classList.contains('nyaya-sidebar-open')) {
          closeSidebar();
        } else {
          openSidebar();
        }
      });
    });

    backdrop.addEventListener('click', closeSidebar);

    document.querySelectorAll('[data-nyaya-sidebar] a[href]').forEach((link) => {
      link.addEventListener('click', () => {
        if (window.innerWidth < 768) {
          closeSidebar();
        }
      });
    });

    window.addEventListener('resize', () => {
      if (window.innerWidth >= 768) {
        closeSidebar();
      }
    });
  };

  const patchInternalLinks = () => {
    document.querySelectorAll('a[href]').forEach((anchor) => {
      const href = anchor.getAttribute('href');
      if (!href) {
        return;
      }
      if (href === 'profile.html' || href === 'settings.html' || href === 'logout.html' || href === 'index.html') {
        anchor.setAttribute('href', 'dashboard.html');
      }
    });
  };

  if (isAppPage) {
    document.addEventListener('DOMContentLoaded', () => {
      setActiveLink();
      wireSidebarControls();
      patchInternalLinks();
    });
  }
})();

/* 共通の動き：メイン写真の切り替え、表示アニメーション、メニュー、読み進みバー */
(function () {
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  let active = 0, timer = null, paused = reduced.matches;
  const slides = document.querySelectorAll('[data-slide]');

  function setSlide(i) {
    active = i;
    slides.forEach(el => el.classList.toggle('is-active', +el.dataset.slide === i));
    document.querySelectorAll('[data-go]').forEach(el => el.setAttribute('aria-pressed', String(+el.dataset.go === i)));
  }
  function restart() {
    clearInterval(timer);
    if (!paused && !document.hidden && slides.length > 1) timer = setInterval(() => setSlide((active + 1) % slides.length), 6500);
  }
  function syncPause() {
    const pause = document.querySelector('.slide-pause');
    if (!pause) return;
    pause.textContent = paused ? '▶' : 'Ⅱ';
    pause.setAttribute('aria-label', paused ? '写真の自動切り替えを再開' : '写真の自動切り替えを停止');
  }

  const hero = document.querySelector('.hero');
  if (hero) {
    restart();
    syncPause();
    hero.addEventListener('focusin', () => clearInterval(timer));
    hero.addEventListener('focusout', restart);
    document.addEventListener('visibilitychange', restart);
  }

  const els = document.querySelectorAll('[data-reveal]');
  if ('IntersectionObserver' in window && !reduced.matches && els.length) {
    document.documentElement.classList.add('reveal-ready');
    const observer = new IntersectionObserver(entries => entries.forEach(entry => {
      if (entry.isIntersecting) { entry.target.classList.add('is-in'); observer.unobserve(entry.target); }
    }), { threshold: .06 });
    els.forEach(el => observer.observe(el));
  }

  document.addEventListener('click', e => {
    const go = e.target.closest('[data-go]');
    if (go) { setSlide(+go.dataset.go); restart(); }
    if (e.target.closest('.slide-pause')) { paused = !paused; syncPause(); restart(); }
    const menu = document.querySelector('.mobile-menu[open]');
    if (menu && (!menu.contains(e.target) || e.target.closest('a'))) menu.open = false;
    if (e.target.closest('a[href="#page-top"]')) {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: reduced.matches ? 'instant' : 'smooth' });
    }
  });
  document.addEventListener('keydown', e => {
    if (e.key !== 'Escape') return;
    const menu = document.querySelector('.mobile-menu[open]');
    if (menu) { menu.open = false; menu.querySelector('summary').focus(); }
  });
  window.addEventListener('resize', () => {
    if (innerWidth > 880) { const menu = document.querySelector('.mobile-menu'); if (menu) menu.open = false; }
  });

  let ticking = false;
  window.addEventListener('scroll', () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      const bar = document.getElementById('reading-progress');
      const range = document.documentElement.scrollHeight - innerHeight;
      if (bar) bar.style.width = (range > 0 ? scrollY / range * 100 : 0) + '%';
      ticking = false;
    });
  }, { passive: true });
})();

/* 施工実績：一覧・絞り込み・詳細モーダル（データは works-data.js） */
(function () {
  const works = window.WORKS || [];
  const grid = document.getElementById('works-grid');
  const cardTpl = document.getElementById('work-card');
  const filterBox = document.getElementById('works-filters');
  const modal = document.getElementById('work-modal');
  if (!grid || !cardTpl || !modal) return;

  const no = i => 'CASE ' + String(i + 1).padStart(2, '0');
  const dash = v => v || '—';
  let cat = 'すべて', sel = null, lastFocus = null;

  function setBg(el, src) {
    el.style.backgroundImage = 'url("' + src.replace(/"/g, '%22') + '")';
    const im = new Image();
    const fallback = () => { if (el.isConnected) el.innerHTML = '<span class="work-placeholder">施工写真 準備中</span>'; };
    const timeout = setTimeout(fallback, 4000);
    im.onload = () => { clearTimeout(timeout); el.textContent = ''; };
    im.onerror = () => { clearTimeout(timeout); fallback(); };
    im.src = src;
  }

  function renderGrid() {
    grid.innerHTML = '';
    const list = works.map((w, i) => ({ w, i })).filter(x => cat === 'すべて' || x.w.cat === cat);
    if (!list.length) { grid.innerHTML = '<p class="works-empty">施工実績は準備中です。</p>'; return; }
    list.forEach(({ w, i }) => {
      const node = cardTpl.content.firstElementChild.cloneNode(true);
      node.setAttribute('aria-label', w.client + 'の詳細を見る');
      node.querySelector('[data-bind-no]').textContent = no(i);
      node.querySelector('[data-bind-client]').textContent = w.client;
      const img = node.querySelector('[data-bind-img]');
      img.setAttribute('aria-label', w.client);
      if (w.img) setBg(img, w.img); else img.innerHTML = '<span class="work-placeholder">施工写真 準備中</span>';
      node.addEventListener('click', () => open(i));
      grid.appendChild(node);
    });
  }

  function renderFilters() {
    const cats = [...new Set(works.map(w => w.cat).filter(Boolean))];
    if (!cats.length || !filterBox) return;
    filterBox.hidden = false;
    filterBox.innerHTML = '';
    ['すべて', ...cats].forEach(c => {
      const b = document.createElement('button');
      b.type = 'button';
      b.textContent = c;
      b.setAttribute('aria-pressed', String(c === cat));
      b.addEventListener('click', () => { cat = c; renderFilters(); renderGrid(); });
      filterBox.appendChild(b);
    });
  }

  const rowTpl = document.getElementById('work-row');
  const rowsBox = document.getElementById('work-modal-rows');
  function fillModal() {
    const w = works[sel];
    document.getElementById('work-modal-no').textContent = no(sel);
    document.getElementById('work-modal-title').textContent = w.client;
    const img = document.getElementById('work-modal-img');
    img.setAttribute('aria-label', w.client);
    img.innerHTML = '';
    if (w.img) setBg(img, w.img); else { img.style.backgroundImage = 'none'; img.innerHTML = '<span class="work-placeholder">施工写真 準備中</span>'; }
    rowsBox.querySelectorAll(':scope > div').forEach(d => d.remove());
    [['施工場所', w.place], ['建物の種類', w.building], ['工事内容', w.work], ['工期', w.period], ['完工時期', w.done]].forEach(([k, v]) => {
      const r = rowTpl.content.firstElementChild.cloneNode(true);
      r.querySelector('dt').textContent = k;
      r.querySelector('dd').textContent = dash(v);
      rowsBox.appendChild(r);
    });
    const note = document.getElementById('work-modal-note');
    note.textContent = w.note || '';
    note.hidden = !w.note;
  }
  function open(i) {
    lastFocus = document.activeElement;
    sel = i;
    fillModal();
    modal.hidden = false;
    document.body.classList.add('modal-open');
    modal.querySelector('[role=dialog]').focus();
  }
  function close() {
    modal.hidden = true;
    sel = null;
    document.body.classList.remove('modal-open');
    if (lastFocus) lastFocus.focus();
  }
  modal.addEventListener('click', e => {
    if (e.target === modal || e.target.closest('[data-close]')) close();
    else if (e.target.closest('[data-prev]')) { sel = (sel - 1 + works.length) % works.length; fillModal(); }
    else if (e.target.closest('[data-next]')) { sel = (sel + 1) % works.length; fillModal(); }
  });
  document.addEventListener('keydown', e => {
    if (sel === null) return;
    if (e.key === 'Escape') close();
    if (e.key === 'Tab') {
      const f = [...modal.querySelectorAll('button')];
      if (e.shiftKey && document.activeElement === f[0]) { e.preventDefault(); f[f.length - 1].focus(); }
      else if (!e.shiftKey && document.activeElement === f[f.length - 1]) { e.preventDefault(); f[0].focus(); }
    }
  });

  renderFilters();
  renderGrid();
})();

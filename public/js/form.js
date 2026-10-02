/* お問い合わせ・応募フォーム：入力チェック → 確認画面 → 送信 → 完了 */
(function () {
  const cfg = window.FORM_CONFIG || {};

  document.querySelectorAll('form.js-form').forEach(form => {
    const kind = form.dataset.form;
    const parent = form.parentNode;

    // スパム対策（人には見えない入力欄）
    const hp = document.createElement('div');
    hp.className = 'hp-field';
    hp.setAttribute('aria-hidden', 'true');
    hp.innerHTML = '<label>空欄のままにしてください<input type="checkbox" name="botcheck" tabindex="-1" autocomplete="off"></label>';
    form.appendChild(hp);

    const fields = [...form.querySelectorAll('input[name]:not([name=botcheck]), select[name], textarea[name]')];
    const labelOf = el => {
      const l = form.querySelector('label[for="' + el.id + '"]');
      return l ? l.childNodes[0].textContent.trim() : el.name;
    };

    function showError(el, msg) {
      clearError(el);
      el.setAttribute('aria-invalid', 'true');
      const p = document.createElement('p');
      p.className = 'form-error';
      p.id = el.id + '-err';
      p.textContent = msg;
      el.setAttribute('aria-describedby', p.id);
      el.insertAdjacentElement('afterend', p);
    }
    function clearError(el) {
      el.removeAttribute('aria-invalid');
      el.removeAttribute('aria-describedby');
      const p = document.getElementById(el.id + '-err');
      if (p) p.remove();
    }
    function validate(el) {
      const v = el.value.trim();
      if (el.required && !v) { showError(el, labelOf(el) + 'を入力してください。'); return false; }
      if (v && el.type === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) { showError(el, 'メールアドレスの形式をご確認ください。'); return false; }
      if (v && el.type === 'tel' && !/^[0-9０-９+\-－ー()（）\s]{10,}$/.test(v)) { showError(el, 'お電話番号をご確認ください。'); return false; }
      clearError(el);
      return true;
    }
    fields.forEach(el => el.addEventListener('blur', () => { if (el.getAttribute('aria-invalid')) validate(el); }));

    let panel = null;
    function setPanel(node) {
      if (panel) panel.remove();
      panel = node;
      if (node) { parent.insertBefore(node, form.nextSibling); form.hidden = true; }
      else form.hidden = false;
      (node || form).scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    form.addEventListener('submit', e => {
      e.preventDefault();
      const bad = fields.filter(el => !validate(el));
      if (bad.length) { bad[0].focus(); return; }
      showConfirm();
    });

    function showConfirm() {
      const box = document.createElement('div');
      box.className = 'form-confirm';
      box.tabIndex = -1;
      const dl = document.createElement('dl');
      fields.forEach(el => {
        const row = document.createElement('div');
        const dt = document.createElement('dt'); dt.textContent = labelOf(el);
        const dd = document.createElement('dd'); dd.textContent = el.value.trim() || '—';
        row.append(dt, dd); dl.appendChild(row);
      });
      box.innerHTML = '<h3>入力内容のご確認</h3><p>以下の内容で送信します。よろしければ「送信する」を押してください。</p>';
      box.appendChild(dl);
      const status = document.createElement('p'); status.className = 'form-status'; status.setAttribute('role', 'alert');
      const actions = document.createElement('div'); actions.className = 'form-actions';
      actions.innerHTML = '<button type="button" class="form-back">← 修正する</button><button type="button" class="form-send">送信する<span aria-hidden="true">→</span></button>';
      box.append(actions, status);
      setPanel(box);
      box.focus({ preventScroll: true });
      actions.querySelector('.form-back').addEventListener('click', () => setPanel(null));
      actions.querySelector('.form-send').addEventListener('click', ev => send(ev.currentTarget, status));
    }

    async function send(btn, status) {
      status.textContent = '';
      if (!cfg.accessKey) {
        status.textContent = '現在、フォームからの送信を準備中です。お手数ですが、お電話でお問い合わせください。';
        return;
      }
      btn.disabled = true;
      btn.firstChild.textContent = '送信中…';
      const data = { access_key: cfg.accessKey, subject: (cfg.subjects || {})[kind] || 'ホームページからの送信', from_name: '大伸工業 ホームページ' };
      fields.forEach(el => { data[el.name] = el.value.trim(); });
      const nameEl = form.querySelector('[name="お名前"]');
      if (nameEl) data.name = nameEl.value.trim();
      data.botcheck = form.querySelector('[name=botcheck]').checked;
      try {
        const res = await fetch(cfg.endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body: JSON.stringify(data) });
        const json = await res.json().catch(() => ({}));
        if (!res.ok || json.success === false) throw new Error(json.message || res.status);
        form.reset();
        showDone();
      } catch (err) {
        btn.disabled = false;
        btn.firstChild.textContent = '送信する';
        status.textContent = '送信できませんでした。時間をおいて再度お試しいただくか、お電話でお問い合わせください。';
      }
    }

    function showDone() {
      const box = document.createElement('div');
      box.className = 'form-done';
      box.tabIndex = -1;
      const msg = kind === 'recruit'
        ? 'ご応募ありがとうございます。<br>内容を確認のうえ、担当者よりご連絡いたします。'
        : 'お問い合わせありがとうございます。<br>内容を確認のうえ、担当者よりご連絡いたします。';
      box.innerHTML = '<h3>送信が完了しました</h3><p>' + msg + '</p><button type="button">フォームに戻る</button>';
      setPanel(box);
      box.focus({ preventScroll: true });
      box.querySelector('button').addEventListener('click', () => setPanel(null));
    }
  });
})();

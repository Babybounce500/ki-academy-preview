(() => {
    'use strict';
    const PREFIX = 'redline_';
    const store = {
        get(key, fallback) { try { const v = localStorage.getItem(PREFIX + key); return v === null ? fallback : JSON.parse(v); } catch (_) { return fallback; } },
        set(key, value) { try { localStorage.setItem(PREFIX + key, JSON.stringify(value)); } catch (_) { /* Speicher gesperrt */ } }
    };
    const catalog = (Array.isArray(window.REDLINE_CATALOG) ? window.REDLINE_CATALOG : []).filter(t => t && t.id && t.name && t.url);
    const sections = Array.isArray(window.REDLINE_SECTIONS) ? window.REDLINE_SECTIONS : [];
    const byId = new Map(catalog.map(t => [t.id, t]));
    const ALL = 'Alle Module';
    const state = { windows: [], activeId: null, z: 20, explorerCategory: ALL, explorerQuery: '', explorerView: 'grid', pins: [], theme: 'redline' };

    const escapeHtml = v => String(v ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }[c]));
    const iconFor = v => v || 'fa-solid fa-link';
    const getTool = id => byId.get(id);
    const getExplorer = () => state.windows.find(w => w.explorer);
    const isMobile = () => window.innerWidth <= 768;
    const $ = id => document.getElementById(id);

    function persist() {
        store.set('windows', state.windows.map(w => ({ id: w.id, toolId: w.toolId, explorer: !!w.explorer, x: w.x, y: w.y, width: w.width, height: w.height, maximized: !!w.maximized, minimized: !!w.minimized, z: w.z })));
        store.set('active', state.activeId);
        store.set('pins', state.pins);
        store.set('theme', state.theme);
        store.set('explorer', { category: state.explorerCategory, view: state.explorerView });
    }
    function restore() {
        const t = store.get('theme', 'redline'); state.theme = t === 'contrast' ? 'contrast' : 'redline';
        const pins = store.get('pins', []); state.pins = Array.isArray(pins) ? pins.filter(id => byId.has(id)) : [];
        const ex = store.get('explorer', {});
        if (ex && typeof ex === 'object') {
            if (typeof ex.category === 'string' && (ex.category === ALL || sections.some(s => s.name === ex.category))) state.explorerCategory = ex.category;
            if (ex.view === 'list' || ex.view === 'grid') state.explorerView = ex.view;
        }
        const saved = store.get('windows', []);
        if (Array.isArray(saved)) {
            saved.slice(0, 12).forEach(w => {
                if (!w || typeof w !== 'object') return;
                const num = (v, d) => Number.isFinite(v) ? v : d;
                const base = { x: Math.max(0, num(w.x, 54)), y: Math.max(0, num(w.y, 54)), width: Math.max(340, num(w.width, 900)), height: Math.max(240, num(w.height, 560)), z: num(w.z, ++state.z), maximized: !!w.maximized, minimized: !!w.minimized };
                if (w.explorer) { state.windows.push({ id: 'explorer', title: 'Explorer — Redline', icon: 'fa-solid fa-folder-tree', explorer: true, ...base }); return; }
                const tool = getTool(w.toolId);
                if (tool) state.windows.push({ id: `tool-${tool.id}`, toolId: tool.id, title: tool.name, icon: iconFor(tool.icon), url: tool.url, ...base });
            });
            state.z = Math.max(state.z, ...state.windows.map(w => w.z), 20);
        }
        const active = store.get('active', null);
        state.activeId = state.windows.some(w => w.id === active) ? active : (state.windows.length ? state.windows[state.windows.length - 1].id : null);
    }
    function applyTheme() {
        document.documentElement.setAttribute('data-theme', state.theme);
        document.querySelectorAll('[data-theme-choice]').forEach(b => {
            const on = b.dataset.themeChoice === state.theme;
            b.querySelector('small').textContent = on ? 'AKTIV' : '';
            b.setAttribute('aria-pressed', String(on));
        });
    }

    function shortcutMarkup(tool) {
        return `<button class="desktop-shortcut" type="button" data-tool="${escapeHtml(tool.id)}" title="${escapeHtml(tool.name)} · ${escapeHtml(tool.description)}" aria-label="${escapeHtml(tool.name)} öffnen">
            <span class="shortcut-icon colored"><i class="${escapeHtml(iconFor(tool.icon))}" style="color:${escapeHtml(tool.color || '#fff1f2')}" aria-hidden="true"></i></span>
            <span class="desktop-shortcut-label">${escapeHtml(tool.name)}</span>
            <span class="desktop-shortcut-meta">${escapeHtml(tool.description)}</span>
        </button>`;
    }
    function renderShortcuts() {
        $('desktopShortcuts').innerHTML = sections.map(sec => {
            const tools = catalog.filter(t => t.category === sec.name);
            if (!tools.length) return '';
            return `<section class="desktop-shortcut-section" aria-label="${escapeHtml(sec.name)}">
                <div class="desktop-shortcut-section-title"><i class="${escapeHtml(sec.icon)}" aria-hidden="true"></i>${escapeHtml(sec.name)}</div>
                <div class="desktop-shortcut-row">${tools.map(shortcutMarkup).join('')}</div>
            </section>`;
        }).join('');
    }
    const categories = () => [ALL, ...sections.map(s => s.name)];
    function explorerTools() {
        const q = state.explorerQuery.trim().toLowerCase();
        return catalog.filter(t => (state.explorerCategory === ALL || t.category === state.explorerCategory) && (!q || `${t.name} ${t.description} ${t.category}`.toLowerCase().includes(q)));
    }
    function explorerMarkup() {
        const tools = explorerTools();
        const card = t => `<button class="file-card" type="button" data-tool="${escapeHtml(t.id)}" title="${escapeHtml(t.name)} öffnen">
            <span class="file-card-icon"><i class="${escapeHtml(iconFor(t.icon))}" style="color:${escapeHtml(t.color || '#fb7185')}" aria-hidden="true"></i></span>
            <span class="file-card-name">${escapeHtml(t.name)}</span>
            <span class="file-card-meta">${escapeHtml(t.description)}</span>
            <span class="file-card-url">${escapeHtml(t.category)}</span></button>`;
        const row = t => `<button class="file-card" type="button" data-tool="${escapeHtml(t.id)}" title="${escapeHtml(t.name)} öffnen">
            <span class="file-card-name"><i class="${escapeHtml(iconFor(t.icon))}" style="color:${escapeHtml(t.color || '#fb7185')}" aria-hidden="true"></i> ${escapeHtml(t.name)}</span>
            <span class="file-card-meta">${escapeHtml(t.category)} · ${escapeHtml(t.description)}</span></button>`;
        const content = tools.length ? `<div class="explorer-grid">${tools.map(state.explorerView === 'list' ? row : card).join('')}</div>` : '<div class="empty-state">Keine Module gefunden.</div>';
        return `<div class="explorer-layout">
            <aside class="explorer-sidebar"><h2>Ordner</h2>${categories().map(c => `<button class="folder-button${state.explorerCategory === c ? ' active' : ''}" type="button" data-folder="${escapeHtml(c)}"><i class="fa-solid fa-folder" aria-hidden="true"></i><span>${escapeHtml(c)}</span></button>`).join('')}</aside>
            <section class="explorer-content">
                <div class="explorer-toolbar">
                    <div class="explorer-path">REDLINE / ${escapeHtml(state.explorerCategory.toUpperCase())}</div>
                    <div class="explorer-view-controls"><button class="view-button${state.explorerView === 'grid' ? ' active' : ''}" type="button" data-view="grid" title="Rasteransicht" aria-label="Rasteransicht"><i class="fa-solid fa-table-cells-large" aria-hidden="true"></i></button><button class="view-button${state.explorerView === 'list' ? ' active' : ''}" type="button" data-view="list" title="Listenansicht" aria-label="Listenansicht"><i class="fa-solid fa-list" aria-hidden="true"></i></button></div>
                    <input class="explorer-search" id="explorerSearch" value="${escapeHtml(state.explorerQuery)}" placeholder="Module suchen …" aria-label="Module im Explorer suchen">
                </div>${content}
            </section>
        </div>`;
    }
    function windowMarkup(item) {
        const body = item.explorer ? explorerMarkup() : `<iframe src="${escapeHtml(item.url)}" title="${escapeHtml(item.title)}" allow="clipboard-read; clipboard-write" sandbox="allow-same-origin allow-scripts allow-forms allow-popups allow-modals allow-downloads"></iframe>`;
        const addr = item.explorer ? 'redline://explorer' : item.url;
        const pinned = item.toolId && state.pins.includes(item.toolId);
        const t = escapeHtml(item.title), id = escapeHtml(item.id);
        return `<section class="window-frame${item.explorer ? ' explorer-frame' : ''}${item.maximized ? ' maximized' : ''}${item.minimized ? ' mobile-hidden' : ''}${state.activeId === item.id ? ' active' : ''}" data-window="${id}" role="dialog" aria-label="${t}" style="left:${item.x}px;top:${item.y}px;width:${item.width}px;height:${item.height}px;z-index:${item.z}">
            <header class="window-titlebar" data-drag="${id}">
                <i class="window-title-icon ${escapeHtml(iconFor(item.icon))}" aria-hidden="true"></i><span class="window-title">${t}</span>
                <div class="window-address" title="${escapeHtml(addr)}"><i class="fa-solid fa-lock" aria-hidden="true"></i><input type="text" readonly value="${escapeHtml(addr)}" aria-label="Adresse des Moduls">${item.url ? `<a class="window-address-open" href="${escapeHtml(item.url)}" target="_blank" rel="noopener" title="In neuem Tab öffnen" aria-label="${t} in neuem Tab öffnen"><i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></a>` : ''}</div>
                <div class="window-controls">
                    ${item.toolId ? `<button class="window-control${pinned ? ' active-pin' : ''}" type="button" data-window-action="pin" data-window="${id}" title="${pinned ? 'Anheftung lösen' : 'Anheften'}" aria-label="${pinned ? 'Anheftung lösen' : 'Modul anheften'}" aria-pressed="${!!pinned}"><i class="fa-solid fa-thumbtack" aria-hidden="true"></i></button>` : ''}
                    ${item.url ? `<button class="window-control" type="button" data-window-action="reload" data-window="${id}" title="Neu laden" aria-label="Modul neu laden"><i class="fa-solid fa-rotate-right" aria-hidden="true"></i></button>` : ''}
                    <button class="window-control" type="button" data-window-action="minimize" data-window="${id}" title="Minimieren" aria-label="Fenster minimieren"><i class="fa-solid fa-minus" aria-hidden="true"></i></button>
                    <button class="window-control" type="button" data-window-action="maximize" data-window="${id}" title="Maximieren" aria-label="Fenster maximieren"><i class="fa-regular fa-square" aria-hidden="true"></i></button>
                    <button class="window-control close" type="button" data-window-action="close" data-window="${id}" title="Schließen" aria-label="Fenster schließen"><i class="fa-solid fa-xmark" aria-hidden="true"></i></button>
                </div>
            </header>
            <div class="window-body">${body}</div>${item.explorer ? '' : `<span class="resize-handle" data-resize="${id}" data-direction="se"></span>`}
        </section>`;
    }
    function renderWindows(save = true) {
        const keepSearch = document.activeElement && document.activeElement.id === 'explorerSearch';
        $('windowLayer').innerHTML = [...state.windows].sort((a, b) => a.z - b.z).map(windowMarkup).join('');
        $('taskbarWindows').innerHTML = state.windows.map(i => `<button class="taskbar-item${state.activeId === i.id ? ' active' : ''}" type="button" data-task="${escapeHtml(i.id)}" title="${escapeHtml(i.title)}" aria-label="${escapeHtml(i.title)} in den Vordergrund"><i class="${escapeHtml(iconFor(i.icon))}" aria-hidden="true"></i><span>${escapeHtml(i.title)}</span></button>`).join('');
        if (save) persist();
        return keepSearch;
    }
    function focusWindow(id) { const it = state.windows.find(w => w.id === id); if (!it) return; it.minimized = false; it.z = ++state.z; state.activeId = id; }
    function defaultGeom(offsetIdx) {
        const o = (offsetIdx % 5) * 26;
        const area = $('desktopCanvas');
        const aw = area.clientWidth || window.innerWidth, ah = area.clientHeight || window.innerHeight;
        return { x: 54 + o, y: 54 + o, width: Math.max(340, Math.min(930, aw - 108)), height: Math.max(240, Math.min(610, ah - 96)) };
    }
    function openExplorer() {
        const cur = getExplorer();
        if (cur) { focusWindow(cur.id); renderWindows(); return; }
        const g = defaultGeom(0);
        state.windows.push({ id: 'explorer', title: 'Explorer — Redline', icon: 'fa-solid fa-folder-tree', explorer: true, ...g, x: 42, y: 42, z: ++state.z, minimized: false });
        state.activeId = 'explorer'; renderWindows();
    }
    function openTool(id) {
        const tool = getTool(id); if (!tool) return;
        const existing = state.windows.find(w => w.toolId === id);
        if (existing) { focusWindow(existing.id); renderWindows(); return; }
        const item = { id: `tool-${tool.id}`, toolId: tool.id, title: tool.name, icon: iconFor(tool.icon), url: tool.url, ...defaultGeom(state.windows.length), z: ++state.z, minimized: false };
        state.windows.push(item); state.activeId = item.id; renderWindows();
        const results = $('taskbarSearchResults'); results.hidden = true;
    }
    function closeWindow(id) { state.windows = state.windows.filter(w => w.id !== id); state.activeId = state.windows.length ? state.windows[state.windows.length - 1].id : null; renderWindows(); }
    function reloadWindow(id) { const f = document.querySelector(`[data-window="${CSS.escape(id)}"] iframe`); if (f) f.src = f.src; }
    function renderTray() {
        $('toolTray').innerHTML = state.pins.length ? state.pins.map(id => { const t = getTool(id); return t ? `<button class="tray-chip" type="button" data-tool="${escapeHtml(id)}" title="${escapeHtml(t.name)} öffnen"><i class="${escapeHtml(iconFor(t.icon))}" aria-hidden="true"></i><span>${escapeHtml(t.name)}</span></button>` : ''; }).join('') : '<span class="appearance-note">Noch nichts angeheftet. Nutze die Pin-Schaltfläche im Fenster.</span>';
    }
    function togglePin(id) {
        const w = state.windows.find(x => x.id === id); if (!w || !w.toolId) return;
        state.pins = state.pins.includes(w.toolId) ? state.pins.filter(p => p !== w.toolId) : [...state.pins, w.toolId];
        renderTray(); renderWindows();
    }
    function renderSearch(query) {
        const q = query.trim().toLowerCase();
        const results = q ? catalog.filter(t => `${t.name} ${t.description} ${t.category}`.toLowerCase().includes(q)).slice(0, 8) : [];
        const el = $('taskbarSearchResults');
        el.innerHTML = results.map(t => `<button class="search-result" type="button" data-tool="${escapeHtml(t.id)}" title="${escapeHtml(t.name)} öffnen"><i class="${escapeHtml(iconFor(t.icon))}" aria-hidden="true"></i><span>${escapeHtml(t.name)}<small>${escapeHtml(t.category)}</small></span><i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i></button>`).join('');
        el.hidden = !results.length;
    }
    function startRedAnimation() {
        const canvas = $('matrixCanvas'), area = $('desktopCanvas'), ctx = canvas.getContext('2d');
        const reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        const resize = () => { canvas.width = area.clientWidth; canvas.height = area.clientHeight; };
        resize(); window.addEventListener('resize', resize);
        const nodes = Array.from({ length: 52 }, () => ({ x: Math.random() * canvas.width, y: Math.random() * canvas.height, vx: (Math.random() - .5) * .35, vy: (Math.random() - .5) * .35 }));
        const draw = () => {
            if (document.hidden) return;
            ctx.fillStyle = 'rgba(10, 1, 3, .2)'; ctx.fillRect(0, 0, canvas.width, canvas.height);
            nodes.forEach(n => { n.x += n.vx; n.y += n.vy; if (n.x < 0 || n.x > canvas.width) n.vx *= -1; if (n.y < 0 || n.y > canvas.height) n.vy *= -1; });
            nodes.forEach((a, i) => nodes.slice(i + 1).forEach(b => { const d = Math.hypot(a.x - b.x, a.y - b.y); if (d < 145) { ctx.strokeStyle = `rgba(248, 113, 113, ${.34 * (1 - d / 145)})`; ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke(); } }));
            nodes.forEach(n => { ctx.fillStyle = '#fb7185'; ctx.shadowColor = '#ef4444'; ctx.shadowBlur = 8; ctx.beginPath(); ctx.arc(n.x, n.y, 2.2, 0, Math.PI * 2); ctx.fill(); ctx.shadowBlur = 0; });
        };
        draw(); if (!reduce) setInterval(draw, 58);
    }
    function updateClock() {
        const now = new Date();
        $('tbTime').textContent = new Intl.DateTimeFormat('de-DE', { hour: '2-digit', minute: '2-digit' }).format(now);
        $('tbDate').textContent = new Intl.DateTimeFormat('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' }).format(now);
    }
    // Ziehen und Skalieren; iframes bekommen währenddessen pointer-events:none
    function dragOp(event, id, mode) {
        const item = state.windows.find(w => w.id === id); if (!item || item.maximized || isMobile()) return;
        focusWindow(id);
        const origin = { x: event.clientX, y: event.clientY, left: item.x, top: item.y, w: item.width, h: item.height };
        const el = document.querySelector(`[data-window="${CSS.escape(id)}"]`);
        const layer = $('windowLayer'); layer.querySelectorAll('iframe').forEach(f => { f.style.pointerEvents = 'none'; });
        const move = p => {
            if (mode === 'drag') { item.x = Math.max(0, origin.left + p.clientX - origin.x); item.y = Math.max(0, origin.top + p.clientY - origin.y); if (el) { el.style.left = item.x + 'px'; el.style.top = item.y + 'px'; } }
            else { item.width = Math.max(340, origin.w + p.clientX - origin.x); item.height = Math.max(240, origin.h + p.clientY - origin.y); if (el) { el.style.width = item.width + 'px'; el.style.height = item.height + 'px'; } }
        };
        const stop = () => { window.removeEventListener('pointermove', move); layer.querySelectorAll('iframe').forEach(f => { f.style.pointerEvents = ''; }); persist(); };
        window.addEventListener('pointermove', move); window.addEventListener('pointerup', stop, { once: true });
    }
    function closePopups() { $('toolTray').classList.remove('open'); $('appearancePopup').classList.remove('open'); }

    restore(); applyTheme(); renderShortcuts(); renderTray(); renderWindows(false); startRedAnimation(); updateClock(); setInterval(updateClock, 30000);
    $('startButton').addEventListener('click', openExplorer);
    $('explorerToggleBtn').addEventListener('click', openExplorer);
    $('trayToggleBtn').addEventListener('click', e => { e.stopPropagation(); $('appearancePopup').classList.remove('open'); $('toolTray').classList.toggle('open'); });
    $('themeToggleBtn').addEventListener('click', e => { e.stopPropagation(); $('toolTray').classList.remove('open'); $('appearancePopup').classList.toggle('open'); });
    $('taskbarSearchInput').addEventListener('input', e => renderSearch(e.target.value));
    document.addEventListener('click', e => {
        const choice = e.target.closest('[data-theme-choice]');
        if (choice) { state.theme = choice.dataset.themeChoice; applyTheme(); persist(); return; }
        const tool = e.target.closest('[data-tool]'); if (tool) { openTool(tool.dataset.tool); closePopups(); return; }
        const task = e.target.closest('[data-task]'); if (task) { focusWindow(task.dataset.task); renderWindows(); return; }
        const act = e.target.closest('[data-window-action]');
        if (act) {
            const id = act.dataset.window, type = act.dataset.windowAction;
            if (type === 'close') closeWindow(id);
            if (type === 'minimize') { const it = state.windows.find(w => w.id === id); if (it) { it.minimized = true; if (state.activeId === id) state.activeId = null; } renderWindows(); }
            if (type === 'maximize') { const it = state.windows.find(w => w.id === id); if (it) { focusWindow(id); it.maximized = !it.maximized; renderWindows(); } }
            if (type === 'reload') reloadWindow(id);
            if (type === 'pin') togglePin(id);
            return;
        }
        const folder = e.target.closest('[data-folder]'); if (folder) { state.explorerCategory = folder.dataset.folder; renderWindows(); return; }
        const view = e.target.closest('[data-view]'); if (view) { state.explorerView = view.dataset.view; renderWindows(); return; }
        if (!e.target.closest('#toolTray, #trayToggleBtn, #appearancePopup, #themeToggleBtn')) closePopups();
        if (!e.target.closest('#taskbarSearch')) $('taskbarSearchResults').hidden = true;
    });
    document.addEventListener('input', e => {
        if (e.target.id !== 'explorerSearch') return;
        state.explorerQuery = e.target.value; const caret = e.target.selectionStart;
        renderWindows(false); const next = $('explorerSearch'); if (next) { next.focus(); next.setSelectionRange(caret, caret); }
    });
    document.addEventListener('pointerdown', e => {
        const handle = e.target.closest('[data-resize]');
        if (handle) { e.preventDefault(); dragOp(e, handle.dataset.resize, 'resize'); return; }
        const bar = e.target.closest('[data-drag]');
        if (bar && !e.target.closest('.window-controls, .window-address')) { dragOp(e, bar.dataset.drag, 'drag'); return; }
        const win = e.target.closest('[data-window]');
        if (win && state.activeId !== win.dataset.window) {
            focusWindow(win.dataset.window);
            document.querySelectorAll('.window-frame').forEach(f => f.classList.toggle('active', f.dataset.window === state.activeId));
            const el = document.querySelector(`[data-window="${CSS.escape(state.activeId)}"]`); if (el) el.style.zIndex = state.windows.find(w => w.id === state.activeId).z;
            persist();
        }
    });
    document.addEventListener('keydown', e => {
        if (e.key === 'Escape') { closePopups(); $('taskbarSearchResults').hidden = true; }
        if (e.key === 'Enter' && e.target.id === 'taskbarSearchInput') { const first = document.querySelector('#taskbarSearchResults [data-tool]'); if (first) openTool(first.dataset.tool); }
    });
})();
if ('serviceWorker' in navigator && location.protocol !== 'file:') {
    window.addEventListener('load', () => { navigator.serviceWorker.register('./service-worker.js', { scope: './' }).catch(() => {}); });
}

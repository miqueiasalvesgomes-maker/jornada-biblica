/**
 * Jornada Bíblica 365 - Frontend Application Logic
 * Gerenciamento reativo de leituras, biblioteca, diário, estatísticas e WhatsApp.
 */

// Estado global da aplicação
const state = {
  currentDay: 1,
  todayDay: 1,
  plan: [],
  filteredPlan: [],
  books: [],
  settings: {},
  stats: {},
  currentFilter: 'all',
  searchQuery: '',
  theme: localStorage.getItem('jb365_theme') || 'theme-dark'
};

// ================= INICIALIZAÇÃO =================
document.addEventListener('DOMContentLoaded', async () => {
  initTheme();
  setupEventListeners();
  registerServiceWorker();
  await loadInitialData();
});

function registerServiceWorker() {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js').catch(err => {
      console.warn('Service Worker não pôde ser registrado:', err);
    });
  }
}

function initTheme() {
  document.body.className = state.theme;
  const icon = document.getElementById('theme-icon');
  if (icon) {
    icon.textContent = state.theme === 'theme-light' ? '☀️' : '🌙';
  }
}

function toggleTheme() {
  state.theme = state.theme === 'theme-light' ? 'theme-dark' : 'theme-light';
  document.body.className = state.theme;
  localStorage.setItem('jb365_theme', state.theme);
  const icon = document.getElementById('theme-icon');
  if (icon) {
    icon.textContent = state.theme === 'theme-light' ? '☀️' : '🌙';
  }
  showToast(state.theme === 'theme-light' ? 'Modo claro ativado' : 'Modo escuro nobre ativado');
}

async function loadInitialData() {
  try {
    await Promise.all([
      fetchSettings(),
      fetchTodayData(),
      fetchStats(),
      fetchBooks(),
      fetchWhatsAppPreview()
    ]);
    // Carrega o plano completo em segundo plano
    fetchPlan();
  } catch (err) {
    console.error('Erro ao carregar dados iniciais:', err);
    showToast('Erro ao carregar dados do servidor.', 'error');
  }
}

// ================= REQUISIÇÕES DE API =================
async function apiGet(endpoint) {
  const res = await fetch(`/api${endpoint}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return await res.json();
}

async function apiPost(endpoint, body = {}) {
  const res = await fetch(`/api${endpoint}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || `HTTP ${res.status}`);
  }
  return await res.json();
}

async function apiPut(endpoint, body = {}) {
  const res = await fetch(`/api${endpoint}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return await res.json();
}

async function apiDelete(endpoint) {
  const res = await fetch(`/api${endpoint}`, { method: 'DELETE' });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return await res.json();
}

// ================= DADOS =================
async function fetchSettings() {
  state.settings = await apiGet('/settings');
  state.currentDay = parseInt(state.settings.current_day || '1', 10);
  state.todayDay = state.currentDay;
  
  // Preenche formulário de configurações
  const nameInput = document.getElementById('cfg-user-name');
  const phoneInput = document.getElementById('cfg-phone');
  const timeInput = document.getElementById('cfg-time');
  const dayInput = document.getElementById('cfg-current-day');
  if (nameInput) nameInput.value = state.settings.user_name || '';
  if (phoneInput) phoneInput.value = state.settings.whatsapp_number || '';
  if (timeInput) timeInput.value = state.settings.reminder_time || '07:00';
  if (dayInput) dayInput.value = state.settings.current_day || '1';
}

async function fetchTodayData(dayNum = null) {
  const targetDay = dayNum || state.currentDay;
  const endpoint = dayNum ? `/day/${dayNum}` : '/today';
  const data = await apiGet(endpoint);
  
  renderTodaySection(data);
}

async function fetchPlan() {
  state.plan = await apiGet('/plan');
  filterAndRenderPlan();
}

async function fetchBooks() {
  state.books = await apiGet('/books');
  renderLibrary();
}

async function fetchStats() {
  state.stats = await apiGet('/stats');
  renderStats();
}

async function fetchWhatsAppPreview() {
  try {
    const data = await apiGet('/whatsapp/preview');
    const previewEl = document.getElementById('whatsapp-message-preview');
    const directLink = document.getElementById('direct-wa-link');
    if (previewEl) previewEl.textContent = data.message;
    if (directLink && data.direct_url) directLink.href = data.direct_url;

    // Atualiza status do bot
    checkBotStatus();
  } catch (err) {
    console.warn('Não foi possível carregar prévia do WhatsApp:', err);
  }
}

async function checkBotStatus() {
  try {
    const status = await apiGet('/whatsapp/status');
    const badge = document.getElementById('bot-status-badge');
    if (badge) {
      if (status.is_logged_in) {
        badge.textContent = '🟢 Conectado ao WhatsApp';
        badge.className = 'status-badge-bot connected';
      } else {
        badge.textContent = '⚪ Sessão desconectada (necessário QR Code)';
        badge.className = 'status-badge-bot';
      }
    }
  } catch (e) {
    console.warn(e);
  }
}

// ================= RENDERIZADORES =================

// 1. RENDERIZAR ABA ESTUDO DE HOJE
function renderTodaySection(data) {
  const day = data.day_data;
  const progress = data.progress || {};
  const recommendedBooks = data.recommended_books || [];

  state.currentDay = day.day;

  // Header tags
  const dayTag = document.getElementById('today-day-tag');
  const catTag = document.getElementById('today-category-tag');
  const passageEl = document.getElementById('today-reading-passage');
  const themeEl = document.getElementById('today-theme');
  const verseTextEl = document.getElementById('today-verse-text');
  const verseRefEl = document.getElementById('today-verse-ref');
  const reflEl = document.getElementById('today-reflection-text');
  const navIndicator = document.getElementById('nav-day-indicator');

  if (dayTag) dayTag.textContent = `Dia ${day.day} de 365`;
  if (catTag) catTag.textContent = `${day.category} • ${day.testament}`;
  if (passageEl) passageEl.textContent = day.reading;
  if (themeEl) themeEl.textContent = day.theme;
  if (verseTextEl) verseTextEl.textContent = day.key_verse_text;
  if (verseRefEl) verseRefEl.textContent = `— ${day.key_verse_ref}`;
  if (reflEl) reflEl.textContent = day.reflection;
  if (navIndicator) navIndicator.textContent = `Dia ${day.day}`;

  // Link Bíblia Online
  const readOnlineBtn = document.getElementById('read-online-btn');
  if (readOnlineBtn) {
    // Busca automática por livro no bibliaonline.com.br
    const bookNameClean = day.reading.split(' ')[0].toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    readOnlineBtn.href = `https://www.bibliaonline.com.br/nvi/${bookNameClean}`;
  }

  // Tags
  const tagsList = document.getElementById('today-tags-list');
  if (tagsList) {
    tagsList.innerHTML = (day.tags || [])
      .map(tag => `<span class="tag-badge">#${tag}</span>`)
      .join('');
  }

  // Status de conclusão
  const isCompleted = progress.status === 'completed';
  const statusBadge = document.getElementById('today-status-badge');
  const statusText = document.getElementById('today-status-text');
  const completeBtnText = document.getElementById('complete-btn-text');
  const completeBtnIcon = document.getElementById('complete-btn-icon');
  const completeBtn = document.getElementById('toggle-complete-btn');

  if (statusBadge && statusText) {
    if (isCompleted) {
      statusBadge.className = 'today-status-badge completed';
      statusText.textContent = 'Concluído';
      if (completeBtnText) completeBtnText.textContent = 'Marcar como Pendente';
      if (completeBtnIcon) completeBtnIcon.textContent = '↩️';
      if (completeBtn) completeBtn.className = 'btn btn-secondary btn-lg';
    } else {
      statusBadge.className = 'today-status-badge';
      statusText.textContent = 'Pendente';
      if (completeBtnText) completeBtnText.textContent = 'Marcar como Concluído Hoje';
      if (completeBtnIcon) completeBtnIcon.textContent = '✅';
      if (completeBtn) completeBtn.className = 'btn btn-primary btn-lg';
    }
  }

  // Anotações
  const notesInput = document.getElementById('today-notes-input');
  const favVerseInput = document.getElementById('today-fav-verse-input');
  if (notesInput) notesInput.value = progress.personal_notes || '';
  if (favVerseInput) favVerseInput.value = progress.favorite_verse || '';

  // Livros recomendados
  const booksGrid = document.getElementById('today-books-grid');
  if (booksGrid) {
    if (recommendedBooks.length === 0) {
      booksGrid.innerHTML = `
        <div style="grid-column: 1 / -1; padding: 1rem; color: var(--text-muted); font-size: 0.9rem;">
          Nenhum livro cadastrado com este tema ainda. <a href="#" id="go-to-library-link" style="color: var(--gold-light);">Cadastre seus livros na aba Minha Biblioteca</a> para conectá-los automaticamente aqui!
        </div>
      `;
      const link = document.getElementById('go-to-library-link');
      if (link) {
        link.addEventListener('click', (e) => {
          e.preventDefault();
          switchTab('tab-library');
        });
      }
    } else {
      booksGrid.innerHTML = recommendedBooks.map(book => `
        <div class="book-rec-card">
          <div class="book-rec-spine" style="background: ${book.cover_color || '#1e3a8a'};"></div>
          <div class="book-rec-content">
            <h5 class="book-rec-title">${escapeHtml(book.title)}</h5>
            <span class="book-rec-author">${escapeHtml(book.author)}</span>
            <p class="book-rec-summary">${escapeHtml(book.summary || book.themes || '')}</p>
          </div>
        </div>
      `).join('');
    }
  }
}

// 2. RENDERIZAR PLANO 365
function filterAndRenderPlan() {
  const query = state.searchQuery.toLowerCase().trim();
  const filter = state.currentFilter;

  state.filteredPlan = state.plan.filter(item => {
    // Filtro de status / testamento
    if (filter === 'completed' && item.status !== 'completed') return false;
    if (filter === 'pending' && item.status === 'completed') return false;
    if (filter === 'ot' && item.testament !== 'Antigo Testamento') return false;
    if (filter === 'nt' && item.testament !== 'Novo Testamento') return false;
    if (filter === 'notes' && !item.has_notes) return false;

    // Busca textual
    if (query) {
      const matchReading = item.reading.toLowerCase().includes(query);
      const matchTheme = item.theme.toLowerCase().includes(query);
      const matchVerse = (item.key_verse_text || '').toLowerCase().includes(query);
      const matchTags = (item.tags || []).some(t => t.toLowerCase().includes(query));
      if (!matchReading && !matchTheme && !matchVerse && !matchTags) return false;
    }
    return true;
  });

  const grid = document.getElementById('plan-days-grid');
  if (!grid) return;

  if (state.filteredPlan.length === 0) {
    grid.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 4rem 1rem; color: var(--text-muted);">
        <p style="font-size: 1.2rem; font-weight: 600;">Nenhum dia encontrado com esses filtros.</p>
        <p style="font-size: 0.9rem; margin-top: 0.5rem;">Tente ajustar sua busca ou selecionar outro filtro acima.</p>
      </div>
    `;
    return;
  }

  grid.innerHTML = state.filteredPlan.map(item => {
    const isCompleted = item.status === 'completed';
    return `
      <div class="day-card ${isCompleted ? 'completed' : ''}" data-day="${item.day}">
        <div class="day-card-header">
          <span class="day-badge-small">Dia ${item.day}</span>
          <div class="day-check-icon">${isCompleted ? '✓' : ''}</div>
        </div>
        <div class="day-reading-text">${escapeHtml(item.reading)}</div>
        <div class="day-theme-text">${escapeHtml(item.theme)}</div>
        <div class="day-card-footer">
          <span>${item.category}</span>
          <span>${item.has_notes ? '✍️ Anotação' : ''}</span>
        </div>
      </div>
    `;
  }).join('');

  // Evento de clique em cada card do plano
  grid.querySelectorAll('.day-card').forEach(card => {
    card.addEventListener('click', () => {
      const dayNum = parseInt(card.getAttribute('data-day'), 10);
      openDayDetailModal(dayNum);
    });
  });

  // Contador de concluídos
  const completedCount = state.plan.filter(i => i.status === 'completed').length;
  const counterEl = document.getElementById('plan-completed-counter');
  if (counterEl) counterEl.textContent = completedCount;
}

// 3. RENDERIZAR BIBLIOTECA
function renderLibrary() {
  const grid = document.getElementById('library-books-grid');
  if (!grid) return;

  if (state.books.length === 0) {
    grid.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 4rem 1rem; color: var(--text-muted);">
        <p style="font-size: 1.2rem; font-weight: 600;">Sua biblioteca ainda está vazia.</p>
        <p style="font-size: 0.9rem; margin-top: 0.5rem;">Clique no botão acima "Cadastrar Novo Livro" para incluir as obras da sua estante!</p>
      </div>
    `;
    return;
  }

  grid.innerHTML = state.books.map(b => {
    const themesList = (b.themes || '').split(',').map(t => t.trim()).filter(Boolean);
    return `
      <div class="library-book-card" data-book-id="${b.id}">
        <div class="book-card-spine-preview" style="background: ${b.cover_color || '#1e3a8a'};"></div>
        <div class="book-card-title">${escapeHtml(b.title)}</div>
        <div class="book-card-meta">${escapeHtml(b.author)} ${b.year ? `• ${b.year}` : ''}</div>
        
        <div class="book-card-themes">
          ${themesList.map(t => `<span class="tag-badge">${escapeHtml(t)}</span>`).join('')}
        </div>

        <p class="book-card-summary">${escapeHtml(b.summary || '')}</p>

        <div class="book-card-actions">
          <button class="btn-sm btn-ghost edit-book-btn" data-id="${b.id}">✏️ Editar</button>
          <button class="btn-sm btn-ghost delete-book-btn" data-id="${b.id}" style="color: var(--ruby-danger);">🗑️ Excluir</button>
        </div>
      </div>
    `;
  }).join('');

  // Eventos de editar e excluir
  grid.querySelectorAll('.edit-book-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const id = parseInt(btn.getAttribute('data-id'), 10);
      openEditBookModal(id);
    });
  });

  grid.querySelectorAll('.delete-book-btn').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.stopPropagation();
      const id = parseInt(btn.getAttribute('data-id'), 10);
      if (confirm('Tem certeza que deseja remover este livro da sua biblioteca?')) {
        await apiDelete(`/books/${id}`);
        showToast('Livro removido com sucesso!');
        await fetchBooks();
        await fetchStats();
      }
    });
  });
}

// 4. RENDERIZAR ESTATÍSTICAS
function renderStats() {
  const s = state.stats;
  if (!s) return;

  const pctEl = document.getElementById('stats-percentage-text');
  const compDaysEl = document.getElementById('stats-completed-days');
  const barEl = document.getElementById('stats-global-bar');
  const streakEl = document.getElementById('stats-streak-text');
  const headerStreakEl = document.getElementById('header-streak-count');
  const notesCountEl = document.getElementById('stats-notes-count');
  const booksCountEl = document.getElementById('stats-books-count');

  const otTextEl = document.getElementById('stats-ot-text');
  const otBarEl = document.getElementById('stats-ot-bar');
  const ntTextEl = document.getElementById('stats-nt-text');
  const ntBarEl = document.getElementById('stats-nt-bar');

  if (pctEl) pctEl.textContent = `${s.percentage || 0}%`;
  if (compDaysEl) compDaysEl.textContent = s.completed_count || 0;
  if (barEl) barEl.style.width = `${s.percentage || 0}%`;
  if (streakEl) streakEl.textContent = s.streak || 0;
  if (headerStreakEl) headerStreakEl.textContent = s.streak || 0;
  if (notesCountEl) notesCountEl.textContent = s.notes_count || 0;
  if (booksCountEl) booksCountEl.textContent = s.books_count || 0;

  // Antigo Testamento (265 dias)
  const otPct = Math.min(100, Math.round(((s.ot_completed || 0) / 265) * 100));
  if (otTextEl) otTextEl.textContent = `${s.ot_completed || 0} de 265 (${otPct}%)`;
  if (otBarEl) otBarEl.style.width = `${otPct}%`;

  // Novo Testamento (100 dias)
  const ntPct = Math.min(100, Math.round(((s.nt_completed || 0) / 100) * 100));
  if (ntTextEl) ntTextEl.textContent = `${s.nt_completed || 0} de 100 (${ntPct}%)`;
  if (ntBarEl) ntBarEl.style.width = `${ntPct}%`;
}

// ================= MODAL DETALHES DO DIA =================
async function openDayDetailModal(dayNum) {
  const modal = document.getElementById('day-detail-modal');
  const badge = document.getElementById('modal-day-number');
  const body = document.getElementById('modal-day-body');

  badge.textContent = `Dia ${dayNum} de 365`;
  body.innerHTML = `<div style="text-align: center; padding: 2rem;">Carregando detalhes do dia ${dayNum}...</div>`;
  modal.classList.add('open');

  try {
    const data = await apiGet(`/day/${dayNum}`);
    const d = data.day_data;
    const prog = data.progress || {};
    const isCompleted = prog.status === 'completed';

    body.innerHTML = `
      <div style="display: flex; flex-direction: column; gap: 1.5rem;">
        <div>
          <span style="font-size: 0.85rem; color: var(--gold-light); text-transform: uppercase; font-weight: 700;">${d.category} • ${d.testament}</span>
          <h2 style="font-family: var(--font-serif); font-size: 2.2rem; color: #fff; margin-top: 0.3rem;">${escapeHtml(d.reading)}</h2>
          <h4 style="font-size: 1.1rem; color: var(--gold-light); margin-top: 0.2rem;">${escapeHtml(d.theme)}</h4>
        </div>

        <div class="verse-highlight-box" style="padding: 1.5rem;">
          <blockquote class="verse-text" style="font-size: 1.25rem;">${escapeHtml(d.key_verse_text)}</blockquote>
          <cite class="verse-reference">— ${escapeHtml(d.key_verse_ref)}</cite>
        </div>

        <div style="background: var(--bg-tertiary); padding: 1.2rem; border-radius: var(--radius-md);">
          <h5 style="color: #fff; font-size: 0.95rem; font-weight: 700; margin-bottom: 0.5rem;">💡 Reflexão Bíblica</h5>
          <p style="color: #cbd5e1; font-size: 0.95rem; line-height: 1.6;">${escapeHtml(d.reflection)}</p>
        </div>

        <div style="display: flex; gap: 1rem; align-items: center; justify-content: space-between; border-top: 1px solid var(--border-subtle); padding-top: 1.2rem;">
          <button class="btn ${isCompleted ? 'btn-secondary' : 'btn-primary'}" id="modal-toggle-status-btn">
            ${isCompleted ? '↩️ Marcar como Pendente' : '✅ Marcar como Concluído'}
          </button>
          <button class="btn btn-secondary" id="modal-jump-to-study-btn">
            📖 Abrir como Estudo Principal
          </button>
        </div>
      </div>
    `;

    document.getElementById('modal-toggle-status-btn').addEventListener('click', async () => {
      await apiPost(`/day/${dayNum}/complete`);
      modal.classList.remove('open');
      showToast(`Status do dia ${dayNum} atualizado!`);
      await fetchStats();
      await fetchPlan();
      if (dayNum === state.currentDay) {
        await fetchTodayData();
      }
    });

    document.getElementById('modal-jump-to-study-btn').addEventListener('click', async () => {
      modal.classList.remove('open');
      await fetchTodayData(dayNum);
      switchTab('tab-today');
    });

  } catch (err) {
    body.innerHTML = `<div style="color: var(--ruby-danger);">Erro ao carregar detalhes do dia.</div>`;
  }
}

// ================= MODAL ADICIONAR / EDITAR LIVRO =================
function openAddBookModal() {
  document.getElementById('book-modal-title').textContent = 'Cadastrar Livro na Minha Estante';
  document.getElementById('book-form').reset();
  document.getElementById('book-id-input').value = '';
  document.getElementById('book-modal').classList.add('open');
}

function openEditBookModal(bookId) {
  const book = state.books.find(b => b.id === bookId);
  if (!book) return;

  document.getElementById('book-modal-title').textContent = 'Editar Livro da Estante';
  document.getElementById('book-id-input').value = book.id;
  document.getElementById('book-title-input').value = book.title || '';
  document.getElementById('book-author-input').value = book.author || '';
  document.getElementById('book-publisher-input').value = book.publisher || '';
  document.getElementById('book-year-input').value = book.year || '';
  document.getElementById('book-color-input').value = book.cover_color || '#1e3a8a';
  document.getElementById('book-themes-input').value = book.themes || '';
  document.getElementById('book-summary-input').value = book.summary || '';
  document.getElementById('book-notes-input').value = book.notes || '';

  document.getElementById('book-modal').classList.add('open');
}

// ================= EVENT LISTENERS =================
function setupEventListeners() {
  // 1. Navegação de abas
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const tabId = btn.getAttribute('data-tab');
      switchTab(tabId);
    });
  });

  // 2. Alternância de tema
  const themeBtn = document.getElementById('theme-toggle-btn');
  if (themeBtn) themeBtn.addEventListener('click', toggleTheme);

  // 3. Botão Concluir Hoje
  const completeBtn = document.getElementById('toggle-complete-btn');
  if (completeBtn) {
    completeBtn.addEventListener('click', async () => {
      try {
        const res = await apiPost(`/day/${state.currentDay}/complete`);
        showToast(res.new_status === 'completed' ? '🎉 Glória a Deus! Estudo de hoje concluído!' : 'Estudo marcado como pendente.');
        await fetchTodayData();
        await fetchStats();
        await fetchPlan();
      } catch (e) {
        showToast('Erro ao alternar status do dia.', 'error');
      }
    });
  }

  // 4. Navegação Dia Anterior / Próximo
  const prevBtn = document.getElementById('prev-day-btn');
  const nextBtn = document.getElementById('next-day-btn');
  if (prevBtn) {
    prevBtn.addEventListener('click', () => {
      if (state.currentDay > 1) {
        fetchTodayData(state.currentDay - 1);
      }
    });
  }
  if (nextBtn) {
    nextBtn.addEventListener('click', () => {
      if (state.currentDay < 365) {
        fetchTodayData(state.currentDay + 1);
      }
    });
  }

  // 5. Salvar anotações do diário
  const saveNotesBtn = document.getElementById('save-notes-btn');
  if (saveNotesBtn) {
    saveNotesBtn.addEventListener('click', async () => {
      const notes = document.getElementById('today-notes-input').value;
      const favVerse = document.getElementById('today-fav-verse-input').value;
      try {
        await apiPost(`/day/${state.currentDay}/notes`, {
          personal_notes: notes,
          favorite_verse: favVerse
        });
        showToast('Anotações salvas com sucesso!');
        await fetchStats();
        await fetchPlan();
      } catch (e) {
        showToast('Erro ao salvar anotações.', 'error');
      }
    });
  }

  // Copiar versículo
  const copyVerseBtn = document.getElementById('copy-verse-btn');
  if (copyVerseBtn) {
    copyVerseBtn.addEventListener('click', () => {
      const text = document.getElementById('today-verse-text').textContent.trim();
      const ref = document.getElementById('today-verse-ref').textContent.trim();
      navigator.clipboard.writeText(`"${text}" ${ref}`).then(() => {
        showToast('Versículo copiado para a área de transferência!');
      });
    });
  }

  // Compartilhar estudo no WhatsApp rápido
  const waQuickBtn = document.getElementById('whatsapp-quick-send-btn');
  if (waQuickBtn) {
    waQuickBtn.addEventListener('click', () => {
      switchTab('tab-whatsapp');
    });
  }

  // 6. Filtros do Plano 365
  document.querySelectorAll('.filter-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      state.currentFilter = chip.getAttribute('data-filter');
      filterAndRenderPlan();
    });
  });

  const searchInput = document.getElementById('plan-search-input');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      state.searchQuery = e.target.value;
      filterAndRenderPlan();
    });
  }

  const clearSearchBtn = document.getElementById('clear-search-btn');
  if (clearSearchBtn) {
    clearSearchBtn.addEventListener('click', () => {
      if (searchInput) searchInput.value = '';
      state.searchQuery = '';
      filterAndRenderPlan();
    });
  }

  // 7. Modais
  const addBtn = document.getElementById('open-add-book-modal-btn');
  if (addBtn) addBtn.addEventListener('click', openAddBookModal);

  const closeBookModalBtn = document.getElementById('close-book-modal-btn');
  const cancelBookModalBtn = document.getElementById('cancel-book-modal-btn');
  if (closeBookModalBtn) closeBookModalBtn.addEventListener('click', () => document.getElementById('book-modal').classList.remove('open'));
  if (cancelBookModalBtn) cancelBookModalBtn.addEventListener('click', () => document.getElementById('book-modal').classList.remove('open'));

  const closeDayModalBtn = document.getElementById('close-day-modal-btn');
  if (closeDayModalBtn) closeDayModalBtn.addEventListener('click', () => document.getElementById('day-detail-modal').classList.remove('open'));

  // 8. Submit formulário de livro
  const bookForm = document.getElementById('book-form');
  if (bookForm) {
    bookForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const bookId = document.getElementById('book-id-input').value;
      const payload = {
        title: document.getElementById('book-title-input').value,
        author: document.getElementById('book-author-input').value,
        publisher: document.getElementById('book-publisher-input').value,
        year: document.getElementById('book-year-input').value ? parseInt(document.getElementById('book-year-input').value, 10) : null,
        cover_color: document.getElementById('book-color-input').value,
        themes: document.getElementById('book-themes-input').value,
        summary: document.getElementById('book-summary-input').value,
        notes: document.getElementById('book-notes-input').value
      };

      try {
        if (bookId) {
          await apiPut(`/books/${bookId}`, payload);
          showToast('Livro atualizado com sucesso!');
        } else {
          await apiPost('/books', payload);
          showToast('Livro cadastrado na sua biblioteca!');
        }
        document.getElementById('book-modal').classList.remove('open');
        await fetchBooks();
        await fetchStats();
        await fetchTodayData(); // Atualiza livros recomendados de hoje
      } catch (err) {
        showToast('Erro ao salvar livro: ' + err.message, 'error');
      }
    });
  }

  // 9. Configurações & WhatsApp
  const settingsForm = document.getElementById('settings-form');
  if (settingsForm) {
    settingsForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const payload = {
        user_name: document.getElementById('cfg-user-name').value,
        whatsapp_number: document.getElementById('cfg-phone').value,
        reminder_time: document.getElementById('cfg-time').value,
        current_day: document.getElementById('cfg-current-day').value
      };

      try {
        await apiPost('/settings', payload);
        showToast('Configurações salvas!');
        state.currentDay = parseInt(payload.current_day, 10);
        await fetchTodayData();
        await fetchWhatsAppPreview();
      } catch (err) {
        showToast('Erro ao salvar configurações.', 'error');
      }
    });
  }

  // Bot Login WhatsApp (QR Code)
  const botLoginBtn = document.getElementById('bot-login-btn');
  if (botLoginBtn) {
    botLoginBtn.addEventListener('click', async () => {
      showToast('Abrindo janela do WhatsApp Web... Por favor, escaneie o QR Code.');
      await apiPost('/whatsapp/login');
      // Checa status após 15 segundos
      setTimeout(checkBotStatus, 15000);
    });
  }

  // Bot Disparar Envio Agora
  const botSendNowBtn = document.getElementById('bot-send-now-btn');
  if (botSendNowBtn) {
    botSendNowBtn.addEventListener('click', async () => {
      showToast('Disparando envio automático via WhatsApp bot...');
      try {
        const res = await apiPost('/whatsapp/send-now');
        showToast(res.message);
      } catch (err) {
        showToast(err.message, 'error');
      }
    });
  }

  // Copiar mensagem do WhatsApp
  const copyWaMsgBtn = document.getElementById('copy-wa-message-btn');
  if (copyWaMsgBtn) {
    copyWaMsgBtn.addEventListener('click', () => {
      const text = document.getElementById('whatsapp-message-preview').textContent;
      navigator.clipboard.writeText(text).then(() => {
        showToast('Mensagem formatada copiada para a área de transferência!');
      });
    });
  }
}

// ================= HELPERS DE UI =================
function switchTab(tabId) {
  document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));

  const targetPane = document.getElementById(tabId);
  const targetBtn = document.querySelector(`.nav-btn[data-tab="${tabId}"]`);

  if (targetPane) targetPane.classList.add('active');
  if (targetBtn) targetBtn.classList.add('active');

  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function showToast(message, type = 'success') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <span>${type === 'success' ? '✨' : '⚠️'}</span>
    <span>${message}</span>
  `;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/[&<>'"]/g, 
    tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
  );
}

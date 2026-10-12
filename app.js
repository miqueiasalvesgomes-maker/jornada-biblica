/**
 * Jornada Bíblica 365 - Frontend Application Logic
 * Gerenciamento reativo de leituras, múltiplos membros/perfis, biblioteca, diário, estatísticas e WhatsApp.
 */

// Lê user_id da URL caso compartilhado (ex: ?user_id=2)
const urlParams = new URLSearchParams(window.location.search);
const paramUserId = urlParams.get('user_id');
if (paramUserId) {
  localStorage.setItem('jb365_user_id', paramUserId);
}

// Estado global da aplicação
const state = {
  currentUserId: parseInt(localStorage.getItem('jb365_user_id') || '1', 10),
  users: [],
  currentUser: null,
  currentDay: 1,
  todayDay: 1,
  plan: [],
  filteredPlan: [],
  books: [],
  bookCounts: { total: 90, in_progress: 1, pending: 89, completed: 0 },
  bookStatusFilter: 'all',
  bookCategoryFilter: 'all',
  bookSearchQuery: '',
  bookViewMode: 'grouped', // 'grouped' ou 'grid'
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
      console.warn('Service Worker não registrado:', err);
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
    await fetchUsers().catch(e => console.warn('Aviso users:', e));
    await Promise.allSettled([
      fetchSettings(),
      fetchTodayData(),
      fetchStats(),
      fetchBooks(),
      fetchWhatsAppPreview()
    ]);
    fetchPlan().catch(e => console.warn('Aviso plan:', e));
  } catch (err) {
    console.error('Erro ao carregar dados iniciais:', err);
  }
}

// ================= REQUISIÇÕES DE API TRANSPARENTES (MULTI-USUÁRIO) =================
async function apiGet(endpoint) {
  const url = new URL(`/api${endpoint}`, window.location.origin);
  if (!url.searchParams.has('user_id') && state.currentUserId) {
    url.searchParams.set('user_id', state.currentUserId);
  }
  const res = await fetch(url.pathname + url.search);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return await res.json();
}

async function apiPost(endpoint, body = {}) {
  if (typeof body === 'object' && body !== null && !('user_id' in body) && state.currentUserId) {
    body.user_id = state.currentUserId;
  }
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
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || `HTTP ${res.status}`);
  }
  return await res.json();
}

async function apiDelete(endpoint) {
  const res = await fetch(`/api${endpoint}`, { method: 'DELETE' });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || `HTTP ${res.status}`);
  }
  return await res.json();
}

// ================= GESTÃO DE USUÁRIOS & PERFIS =================
async function fetchUsers() {
  try {
    state.users = await apiGet('/users');
    let active = state.users.find(u => u.id === state.currentUserId);
    if (!active && state.users.length > 0) {
      active = state.users[0];
      state.currentUserId = active.id;
      localStorage.setItem('jb365_user_id', active.id);
    }
    state.currentUser = active;

    // Atualiza cabeçalho
    const avatarEl = document.getElementById('header-user-avatar');
    const nameEl = document.getElementById('header-user-name');
    if (avatarEl && active) avatarEl.textContent = active.avatar_icon || '🕊️';
    if (nameEl && active) nameEl.textContent = active.name || 'Membro';

    renderMembers();
    renderProfileQuickList();
  } catch (err) {
    console.warn('Erro ao carregar usuários:', err);
  }
}

function renderMembers() {
  const grid = document.getElementById('members-list-grid');
  if (!grid) return;

  if (state.users.length === 0) {
    grid.innerHTML = `<div style="grid-column: 1 / -1; padding: 2rem; color: var(--text-muted); text-align: center;">Nenhum membro cadastrado.</div>`;
    return;
  }

  grid.innerHTML = state.users.map(u => {
    const isActive = u.id === state.currentUserId;
    const shareUrl = `${window.location.origin}/?user_id=${u.id}`;
    return `
      <div class="member-card ${isActive ? 'active-user' : ''}" data-user-id="${u.id}">
        <div class="member-card-header">
          <div class="member-avatar-lg">${escapeHtml(u.avatar_icon || '🕊️')}</div>
          <div class="member-header-info">
            <h4 class="member-name-heading">${escapeHtml(u.name)}</h4>
            <span class="member-phone-label">${escapeHtml(u.phone ? `📱 ${u.phone}` : 'Sem WhatsApp')}</span>
          </div>
        </div>

        <div class="member-progress-section">
          <div class="member-progress-labels">
            <span>Leitura Atual: <strong>Dia ${u.current_day}</strong></span>
            <span><strong>${u.percentage || 0}%</strong> (${u.completed_count || 0}/365)</span>
          </div>
          <div class="progress-bar-wrap">
            <div class="progress-bar-fill fill-gold" style="width: ${u.percentage || 0}%;"></div>
          </div>
        </div>

        <div class="member-actions-row">
          ${!isActive ? `
            <button class="btn btn-primary btn-sm switch-user-btn" data-id="${u.id}">
              <span>👤</span> Estudar como ${escapeHtml(u.name.split(' ')[0])}
            </button>
          ` : `
            <button class="btn btn-secondary btn-sm" disabled style="opacity: 0.9;">
              <span>⭐</span> Perfil Ativo
            </button>
          `}
          <button class="btn btn-ghost btn-sm copy-member-link-btn" data-url="${shareUrl}" title="Copiar link de estudo pessoal">
            <span>🔗</span> Link
          </button>
          <button class="btn btn-ghost btn-sm edit-member-btn" data-id="${u.id}" title="Editar perfil">
            <span>✏️</span> Editar
          </button>
          ${state.users.length > 1 ? `
            <button class="btn btn-ghost btn-sm delete-member-btn" data-id="${u.id}" style="color: var(--ruby-danger);" title="Excluir membro">
              <span>🗑️</span>
            </button>
          ` : ''}
        </div>
      </div>
    `;
  }).join('');

  // Eventos de clique nos botões de membro
  grid.querySelectorAll('.switch-user-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const id = parseInt(btn.getAttribute('data-id'), 10);
      switchUser(id);
    });
  });

  grid.querySelectorAll('.copy-member-link-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const url = btn.getAttribute('data-url');
      navigator.clipboard.writeText(url).then(() => {
        showToast('Link individual copiado! Envie para o membro acessar direto o plano dele.');
      });
    });
  });

  grid.querySelectorAll('.edit-member-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const id = parseInt(btn.getAttribute('data-id'), 10);
      openEditMemberModal(id);
    });
  });

  grid.querySelectorAll('.delete-member-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const id = parseInt(btn.getAttribute('data-id'), 10);
      if (confirm('Tem certeza que deseja remover este membro e seu histórico de leitura?')) {
        try {
          await apiDelete(`/users/${id}`);
          showToast('Membro removido com sucesso!');
          if (state.currentUserId === id) {
            state.currentUserId = state.users.find(u => u.id !== id)?.id || 1;
            localStorage.setItem('jb365_user_id', state.currentUserId);
          }
          await loadInitialData();
        } catch (err) {
          showToast(err.message, 'error');
        }
      }
    });
  });
}

function renderProfileQuickList() {
  const container = document.getElementById('profiles-quick-list');
  if (!container) return;

  container.innerHTML = state.users.map(u => {
    const isActive = u.id === state.currentUserId;
    return `
      <div class="profile-quick-item ${isActive ? 'active' : ''}" data-id="${u.id}">
        <div class="profile-quick-left">
          <span style="font-size: 1.6rem;">${escapeHtml(u.avatar_icon || '🕊️')}</span>
          <div>
            <strong style="color: #fff; font-size: 0.95rem;">${escapeHtml(u.name)}</strong>
            <div style="font-size: 0.78rem; color: var(--text-muted);">Dia ${u.current_day} de 365 • ${u.completed_count || 0} lidos</div>
          </div>
        </div>
        <div>
          ${isActive ? '<span style="color: var(--gold-light); font-weight: 800; font-size: 0.8rem;">● ATIVO</span>' : '<span style="color: var(--text-muted); font-size: 0.8rem;">Trocar ➔</span>'}
        </div>
      </div>
    `;
  }).join('');

  container.querySelectorAll('.profile-quick-item').forEach(item => {
    item.addEventListener('click', () => {
      const id = parseInt(item.getAttribute('data-id'), 10);
      document.getElementById('switch-profile-modal').classList.remove('open');
      if (id !== state.currentUserId) {
        switchUser(id);
      }
    });
  });
}

async function switchUser(userId) {
  state.currentUserId = userId;
  localStorage.setItem('jb365_user_id', userId);
  await loadInitialData();
  const userName = state.currentUser ? state.currentUser.name : 'Membro';
  showToast(`Estudo ativo alterado para ${userName}!`);
}

function openAddMemberModal() {
  document.getElementById('member-modal-title').textContent = 'Cadastrar Novo Membro';
  document.getElementById('member-form').reset();
  document.getElementById('member-id-input').value = '';
  document.getElementById('member-day-input').value = '1';
  document.getElementById('member-modal').classList.add('open');
}

function openEditMemberModal(userId) {
  const member = state.users.find(u => u.id === userId);
  if (!member) return;

  document.getElementById('member-modal-title').textContent = 'Editar Membro';
  document.getElementById('member-id-input').value = member.id;
  document.getElementById('member-name-input').value = member.name || '';
  document.getElementById('member-phone-input').value = member.phone || '';
  document.getElementById('member-day-input').value = member.current_day || 1;

  const radio = document.querySelector(`input[name="member_avatar"][value="${member.avatar_icon}"]`);
  if (radio) radio.checked = true;

  document.getElementById('member-modal').classList.add('open');
}

// ================= DADOS =================
async function fetchSettings() {
  try {
    state.settings = await apiGet('/settings');
  } catch (err) {
    console.warn('Configurações padrão adotadas:', err);
    state.settings = {};
  }

  // Preenche formulário de perfil com os dados do usuário ativo
  const nameInput = document.getElementById('cfg-user-name');
  const phoneInput = document.getElementById('cfg-phone');
  const timeInput = document.getElementById('cfg-time');
  const dayInput = document.getElementById('cfg-current-day');

  if (state.currentUser) {
    if (nameInput) nameInput.value = state.currentUser.name || '';
    if (phoneInput) phoneInput.value = state.currentUser.phone || '';
    if (dayInput) dayInput.value = state.currentUser.current_day || '1';
  } else {
    if (nameInput) nameInput.value = state.settings.user_name || '';
    if (phoneInput) phoneInput.value = state.settings.whatsapp_number || '';
    if (dayInput) dayInput.value = state.settings.current_day || '1';
  }
  if (timeInput) timeInput.value = state.settings.reminder_time || '07:00';
}

async function fetchTodayData(dayNum = null) {
  const endpoint = dayNum ? `/day/${dayNum}` : '/today';
  const data = await apiGet(endpoint);
  renderTodaySection(data);
}

async function fetchPlan() {
  state.plan = await apiGet('/plan');
  filterAndRenderPlan();
}

async function fetchBooks() {
  try {
    const res = await apiGet('/books');
    if (res && res.books) {
      state.books = res.books.map(b => ({
        ...b,
        status: b.reading_status || b.status || 'Pendente'
      }));
      state.bookCounts = res.counts || {
        total: state.books.length,
        in_progress: state.books.filter(b => b.status === 'Em Andamento').length,
        pending: state.books.filter(b => b.status === 'Pendente').length,
        completed: state.books.filter(b => b.status === 'Finalizado').length
      };
    } else if (Array.isArray(res)) {
      state.books = res.map(b => ({
        ...b,
        status: b.reading_status || b.status || 'Pendente'
      }));
      state.bookCounts = {
        total: state.books.length,
        in_progress: state.books.filter(b => b.status === 'Em Andamento').length,
        pending: state.books.filter(b => b.status === 'Pendente').length,
        completed: state.books.filter(b => b.status === 'Finalizado').length
      };
    }
    updateLibraryCounters();
    renderLibrary();
  } catch (err) {
    console.error('Erro ao buscar livros:', err);
  }
}

function updateLibraryCounters() {
  const c = state.bookCounts || {};
  const totalEl = document.getElementById('lib-count-total');
  const inprogEl = document.getElementById('lib-count-inprogress');
  const pendEl = document.getElementById('lib-count-pending');
  const compEl = document.getElementById('lib-count-completed');
  if (totalEl) totalEl.textContent = c.total !== undefined ? c.total : state.books.length;
  if (inprogEl) inprogEl.textContent = c.in_progress || 0;
  if (pendEl) pendEl.textContent = c.pending || 0;
  if (compEl) compEl.textContent = c.completed || 0;
}

async function updateBookStatus(bookId, newStatus, personalNotes = null) {
  try {
    const payload = { status: newStatus };
    if (personalNotes !== null && personalNotes !== undefined) {
      payload.notes = personalNotes;
    }
    await apiPost(`/books/${bookId}/status`, payload);

    // Atualiza o estado local do livro
    const book = state.books.find(b => b.id === bookId);
    if (book) {
      book.status = newStatus;
      book.reading_status = newStatus;
      if (personalNotes !== null && personalNotes !== undefined) {
        book.user_notes = personalNotes;
        book.personal_notes = personalNotes;
      }
    }

    // Recalcula contadores
    state.bookCounts = {
      total: state.books.length,
      in_progress: state.books.filter(b => b.status === 'Em Andamento').length,
      pending: state.books.filter(b => b.status === 'Pendente' || !b.status).length,
      completed: state.books.filter(b => b.status === 'Finalizado').length
    };
    updateLibraryCounters();
    renderLibrary();

    // Se estiver na aba hoje e o livro estiver listado, atualiza
    const todayGrid = document.getElementById('today-books-grid');
    if (todayGrid && state.currentDay) {
      try {
        const todayData = await apiGet(`/day/${state.currentDay}`);
        renderTodaySection(todayData);
      } catch (e) {
        // Ignora se não conseguir atualizar hoje
      }
    }

    const labelMap = {
      'Em Andamento': 'Em Andamento 📖',
      'Finalizado': 'Finalizado ✅',
      'Pendente': 'Pendente ⏳'
    };
    showToast(`Status atualizado para "${labelMap[newStatus] || newStatus}"!`);
  } catch (err) {
    showToast('Erro ao atualizar status: ' + err.message, 'error');
  }
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
    const groupLink = document.getElementById('group-wa-link');

    if (previewEl) previewEl.textContent = data.message;
    if (directLink && data.direct_url) directLink.href = data.direct_url;
    if (groupLink && data.group_url) groupLink.href = data.group_url;

    // Renderiza lista de membros cadastrados com botão de WhatsApp individual
    const membersList = document.getElementById('whatsapp-members-list');
    if (membersList && data.members) {
      if (data.members.length === 0) {
        membersList.innerHTML = `<p style="color: var(--text-muted); padding: 1rem;">Nenhum membro cadastrado.</p>`;
      } else {
        membersList.innerHTML = data.members.map(m => `
          <div class="wa-member-row">
            <div class="wa-member-info">
              <div class="wa-member-avatar">${escapeHtml(m.avatar_icon || '🕊️')}</div>
              <div>
                <div class="wa-member-name">${escapeHtml(m.name)}</div>
                <div class="wa-member-sub">
                  ${m.phone ? `📱 ${escapeHtml(m.phone)}` : '<span style="color: var(--amber-warning);">Sem telefone cadastrado</span>'} • Dia ${m.current_day}
                </div>
              </div>
            </div>
            <div class="wa-member-actions">
              ${m.individual_wa_url ? `
                <a href="${m.individual_wa_url}" target="_blank" class="btn btn-whatsapp btn-sm">
                  <span>📲</span> Enviar para ${escapeHtml(m.name.split(' ')[0])}
                </a>
              ` : `
                <button class="btn btn-secondary btn-sm edit-wa-phone-btn" data-id="${m.id}">
                  <span>✏️</span> Cadastrar Celular
                </button>
              `}
            </div>
          </div>
        `).join('');

        membersList.querySelectorAll('.edit-wa-phone-btn').forEach(btn => {
          btn.addEventListener('click', () => {
            const id = parseInt(btn.getAttribute('data-id'), 10);
            openEditMemberModal(id);
          });
        });
      }
    }

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
        badge.textContent = '⚪ Bot desativado em nuvem (Envio direto ativo)';
        badge.className = 'status-badge-bot';
      }
    }
  } catch (e) {
    // Silencia se em nuvem
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

  // LIVRO DE TRAVESSEIRO & CABECEIRA OFICIAL
  const bedsideBox = document.getElementById('today-bedside-container');
  const bedsideBook = data.bedside_book;
  const pastoralFocus = data.pastoral_focus;

  if (bedsideBox) {
    if (bedsideBook) {
      bedsideBox.style.display = 'block';
      const titleEl = document.getElementById('bedside-title-text');
      const authorEl = document.getElementById('bedside-author-text');
      const coverEl = document.getElementById('bedside-cover-image');
      const calloutTopic = document.getElementById('bedside-callout-topic');
      const calloutQuote = document.getElementById('bedside-callout-quote');
      const calloutRef = document.getElementById('bedside-callout-ref');
      const tagsRow = document.getElementById('bedside-tags-row');

      if (titleEl) titleEl.textContent = bedsideBook.title;
      if (authorEl) authorEl.textContent = `${bedsideBook.author} • ${bedsideBook.publisher || 'CPAD'}`;
      if (coverEl && bedsideBook.cover_image) {
        coverEl.src = bedsideBook.cover_image;
      }
      if (pastoralFocus) {
        if (calloutTopic) calloutTopic.textContent = `⚡ ${pastoralFocus.topic}`;
        if (calloutQuote) calloutQuote.textContent = `“${pastoralFocus.quote}”`;
        if (calloutRef) calloutRef.textContent = pastoralFocus.chapter_ref;
      }
      if (tagsRow) {
        const bThemes = (bedsideBook.themes || '').split(',').map(t => t.trim()).filter(Boolean);
        tagsRow.innerHTML = bThemes.slice(0, 6).map(t => `<span class="tag-badge">#${escapeHtml(t)}</span>`).join('');
      }

      const viewBtn = document.getElementById('btn-view-bedside-library');
      if (viewBtn) {
        viewBtn.onclick = () => {
          switchTab('tab-library');
        };
      }

      const shareBtn = document.getElementById('btn-share-pastoral-wa');
      if (shareBtn) {
        shareBtn.onclick = () => {
          const text = `📖 *Jornada Bíblica 365*\n🛌 *Livro de Travesseiro:* _${bedsideBook.title}_ (CPAD)\n⚡ *Foco Pastoral Diário:* ${pastoralFocus?.topic || 'Ministério'}\n"${pastoralFocus?.quote || ''}"\n— ${pastoralFocus?.chapter_ref || ''}`;
          window.open(`https://api.whatsapp.com/send?text=${encodeURIComponent(text)}`, '_blank');
        };
      }
    } else {
      bedsideBox.style.display = 'none';
    }
  }

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
      booksGrid.innerHTML = recommendedBooks.map(book => {
        const bStatus = book.reading_status || book.status || 'Pendente';
        return `
          <div class="book-rec-card" data-book-id="${book.id}">
            <div class="book-rec-spine" style="background: ${book.cover_color || '#1e3a8a'};"></div>
            <div class="book-rec-content">
              <h5 class="book-rec-title">${escapeHtml(book.title)}</h5>
              <span class="book-rec-author">${escapeHtml(book.author)} ${book.publisher ? `(${escapeHtml(book.publisher)})` : ''}</span>
              <p class="book-rec-summary">${escapeHtml(book.summary || book.themes || '')}</p>
              
              <div style="display: flex; align-items: center; justify-content: space-between; gap: 0.6rem; margin-top: 0.6rem; padding-top: 0.5rem; border-top: 1px solid var(--border-subtle);">
                <select class="select-status-dropdown" data-book-id="${book.id}" style="background: var(--bg-tertiary); color: #fff; border: 1px solid var(--border-subtle); padding: 0.25rem 0.5rem; border-radius: var(--radius-sm); font-size: 0.8rem; cursor: pointer;">
                  <option value="Pendente" ${bStatus === 'Pendente' ? 'selected' : ''}>⏳ Pendente</option>
                  <option value="Em Andamento" ${bStatus === 'Em Andamento' ? 'selected' : ''}>📖 Lendo</option>
                  <option value="Finalizado" ${bStatus === 'Finalizado' ? 'selected' : ''}>✅ Concluído</option>
                </select>
                <button class="btn btn-ghost btn-sm open-book-detail-btn" data-id="${book.id}">
                  <span>👁️</span> Detalhes
                </button>
              </div>
            </div>
          </div>
        `;
      }).join('');

      booksGrid.querySelectorAll('.select-status-dropdown').forEach(sel => {
        sel.addEventListener('change', (e) => {
          e.stopPropagation();
          const id = parseInt(sel.getAttribute('data-book-id'), 10);
          updateBookStatus(id, sel.value);
        });
      });

      booksGrid.querySelectorAll('.open-book-detail-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
          e.stopPropagation();
          const id = parseInt(btn.getAttribute('data-id'), 10);
          openBookDetailModal(id);
        });
      });
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
const CANONICAL_CATEGORIES = [
  { name: "Cabeceira & Ministério Pastoral", icon: "🛏️", plan: "Todos os 365 Dias (Leitura de Travesseiro Permanente e Prática Diária)" },
  { name: "Antigo Testamento, Pentateuco & Arqueologia", icon: "📜", plan: "Dias 1–240 (Pentateuco, Livros Históricos e Profetas)" },
  { name: "Novo Testamento, Evangelhos & Vida de Cristo", icon: "🕊️", plan: "Dias 241–365 (Evangelhos, Atos, Epístolas e Apocalipse)" },
  { name: "Teologia Sistemática, Doutrina & Hermenêutica", icon: "🏛️", plan: "Dias 1–365 (Fundamentos Doutrinários, Exegese e Interpretação)" },
  { name: "Línguas Originais (Grego & Hebraico)", icon: "🗣️", plan: "Dias 1–365 (Auxílio Linguístico Exegético para o AT e NT)" },
  { name: "Comentários & Manuais Bíblicos Panorâmicos", icon: "📖", plan: "Dias 1–365 (Apoio Expositivo Versículo por Versículo)" },
  { name: "História da Igreja Cristã", icon: "⏳", plan: "Dias 1–365 (Contexto Histórico do Povo de Deus e dos Pais da Igreja)" },
  { name: "Vida Cristã, Oração, Avivamento & Família", icon: "🔥", plan: "Dias 1–365 (Devocional Prático, Santidade, Oração e Avivamento)" },
  { name: "Missões, Evangelização & Educação Cristã", icon: "🌍", plan: "Dias 241–365 (A Grande Comissão e Formação de Discípulos)" },
  { name: "Liderança, Desenvolvimento & Sociedade", icon: "💡", plan: "Dias 1–365 (Gestão Ministerial, Comunicação e Liderança Bíblica)" }
];

function createBookCardHtml(b) {
  const isBedside = b.is_bedside === 1;
  const bStatus = b.reading_status || b.status || 'Pendente';
  const themesList = (b.themes || '').split(',').map(t => t.trim()).filter(Boolean);

  return `
    <div class="library-book-card ${isBedside ? 'is-bedside-card' : ''}" data-book-id="${b.id}">
      <div class="book-card-spine-preview" style="background: ${b.cover_color || '#1e3a8a'};"></div>
      
      <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 0.5rem;">
        <h4 class="book-card-title">${escapeHtml(b.title)}</h4>
        ${isBedside ? '<span style="font-size: 0.78rem; color: var(--gold-light); font-weight: 800; white-space: nowrap;">⭐ Cabeceira</span>' : ''}
      </div>

      <div class="book-card-meta">
        ${escapeHtml(b.author)} ${b.year ? `• ${b.year}` : ''} ${b.publisher ? `(${escapeHtml(b.publisher)})` : ''}
      </div>

      <div style="display: flex; gap: 0.4rem; flex-wrap: wrap; align-items: center; margin: 0.2rem 0;">
        <span class="tag-badge" style="color: var(--gold-light); border-color: rgba(212,175,55,0.3); font-weight: 700;">${escapeHtml(b.category || 'Teologia')}</span>
        ${b.plan_link ? `<span class="tag-badge" style="font-size: 0.75rem;">🔗 Plano: ${escapeHtml(b.plan_link)}</span>` : ''}
      </div>

      <div class="book-card-themes">
        ${themesList.slice(0, 4).map(t => `<span class="tag-badge">#${escapeHtml(t)}</span>`).join('')}
      </div>

      <p class="book-card-summary">${escapeHtml(b.summary || '')}</p>

      <div style="display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; padding-top: 0.6rem; border-top: 1px solid var(--border-subtle); margin-top: auto;">
        <label style="font-size: 0.8rem; color: var(--text-muted); font-weight: 700;">Status:</label>
        <select class="select-status-dropdown" data-book-id="${b.id}" style="background: var(--bg-tertiary); color: #fff; border: 1px solid var(--border-subtle); padding: 0.35rem 0.6rem; border-radius: var(--radius-sm); font-size: 0.85rem; cursor: pointer;">
          <option value="Pendente" ${bStatus === 'Pendente' ? 'selected' : ''}>⏳ Pendente</option>
          <option value="Em Andamento" ${bStatus === 'Em Andamento' ? 'selected' : ''}>📖 Em Andamento</option>
          <option value="Finalizado" ${bStatus === 'Finalizado' ? 'selected' : ''}>✅ Finalizado</option>
        </select>
      </div>

      <div class="book-card-actions">
        ${!isBedside ? `
          <button class="btn-sm btn-secondary set-bedside-btn" data-id="${b.id}" title="Definir como Livro de Cabeceira">⭐ Cabeceira</button>
        ` : `
          <span style="font-size: 0.8rem; color: var(--gold-light); font-weight: 700; display: inline-flex; align-items: center; gap: 0.3rem;">⭐ Cabeceira Oficial</span>
        `}
        <button class="btn-sm btn-ghost open-book-detail-btn" data-id="${b.id}">👁️ Detalhes</button>
        <button class="btn-sm btn-ghost edit-book-btn" data-id="${b.id}">✏️ Editar</button>
        <button class="btn-sm btn-ghost delete-book-btn" data-id="${b.id}" style="color: var(--ruby-danger);">🗑️ Excluir</button>
      </div>
    </div>
  `;
}

function renderLibrary() {
  // 1. Vitrine do Livro de Cabeceira Oficial (#library-bedside-feature-slot)
  const bedsideSlot = document.getElementById('library-bedside-feature-slot');
  if (bedsideSlot) {
    const bedsideBook = state.books.find(b => b.is_bedside === 1) || 
                        state.books.find(b => (b.title || '').includes('Pastor Pentecostal')) || 
                        state.books[0];
    if (bedsideBook) {
      const bStatus = bedsideBook.reading_status || bedsideBook.status || 'Em Andamento';
      bedsideSlot.innerHTML = `
        <div class="card-glass" style="border: 1px solid var(--gold-border); background: linear-gradient(135deg, rgba(212,175,55,0.1), rgba(15,23,42,0.9)); padding: 1.6rem; border-radius: var(--radius-lg); margin-bottom: 2rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.8rem; margin-bottom: 0.6rem;">
            <span style="font-size: 0.85rem; color: var(--gold-light); font-weight: 800; text-transform: uppercase; letter-spacing: 0.04em;">
              ⭐ LIVRO DE TRAVESSEIRO & CABECEIRA OFICIAL • LEITURA DIÁRIA OBRIGATÓRIA
            </span>
            <span class="tag-badge" style="background: rgba(212,175,55,0.2); color: var(--gold-light); border-color: var(--gold-border);">365 Dias</span>
          </div>
          <div class="book-card-spine-preview" style="background: var(--gold-primary); height: 5px; margin-bottom: 0.8rem;"></div>
          <h3 style="font-family: var(--font-serif); font-size: 1.6rem; color: #fff; margin-bottom: 0.3rem;">${escapeHtml(bedsideBook.title)}</h3>
          <div style="font-size: 0.9rem; color: var(--gold-light); margin-bottom: 0.8rem;">
            <strong>${escapeHtml(bedsideBook.author)}</strong> • ${escapeHtml(bedsideBook.publisher || 'CPAD')} ${bedsideBook.year ? `(${bedsideBook.year})` : ''}
          </div>
          <div style="display: flex; gap: 0.4rem; flex-wrap: wrap; margin-bottom: 0.8rem;">
            <span class="tag-badge" style="color: var(--gold-light); border-color: rgba(212,175,55,0.4);">👑 Regra de Ouro</span>
            <span class="tag-badge">📖 Teologia Pastoral</span>
            <span class="tag-badge">🕊️ Práticas Pentecostais</span>
          </div>
          <p style="color: #cbd5e1; font-size: 0.9rem; line-height: 1.6; margin-bottom: 1rem;">
            ${escapeHtml(bedsideBook.summary || 'Tratado clássico sobre a prática ministerial e vocação espiritual. Livro fixo de cabeceira acompanhando todos os dias da sua jornada bíblica.')}
          </p>
          <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem; border-top: 1px solid rgba(212,175,55,0.2); padding-top: 0.8rem;">
            <div style="display: flex; align-items: center; gap: 0.6rem;">
              <label style="font-size: 0.85rem; color: var(--gold-light); font-weight: 700;">Status da Leitura:</label>
              <select class="select-status-dropdown" data-book-id="${bedsideBook.id}" style="background: var(--bg-tertiary); color: #fff; border: 1px solid var(--gold-border); padding: 0.35rem 0.6rem; border-radius: var(--radius-sm); font-size: 0.85rem; cursor: pointer;">
                <option value="Em Andamento" ${bStatus === 'Em Andamento' ? 'selected' : ''}>📖 Lendo Atualmente (Cabeceira)</option>
                <option value="Finalizado" ${bStatus === 'Finalizado' ? 'selected' : ''}>✅ Concluído</option>
                <option value="Pendente" ${bStatus === 'Pendente' ? 'selected' : ''}>⏳ Pendente</option>
              </select>
            </div>
            <button class="btn btn-secondary btn-sm open-book-detail-btn" data-id="${bedsideBook.id}">
              <span>👁️</span> Detalhes & Anotações
            </button>
          </div>
        </div>
      `;
    }
  }

  // 2. Container dos Livros da Biblioteca (suporta tanto #library-books-grid quanto #library-books-container)
  const grid = document.getElementById('library-books-grid') || document.getElementById('library-books-container');
  if (!grid) return;

  if (state.books.length === 0) {
    grid.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 4rem 1rem; color: var(--text-muted); width: 100%;">
        <p style="font-size: 1.2rem; font-weight: 600;">Sua biblioteca ainda está vazia.</p>
        <p style="font-size: 0.9rem; margin-top: 0.5rem;">Clique em "Cadastrar Livro" para incluir obras na sua estante!</p>
      </div>
    `;
    return;
  }

  // Filtragem dos livros
  const query = (state.bookSearchQuery || '').toLowerCase().trim();
  const statusFilter = state.bookStatusFilter;
  const catFilter = state.bookCategoryFilter;

  const filtered = state.books.filter(b => {
    const bStatus = b.reading_status || b.status || 'Pendente';
    if (statusFilter !== 'all' && bStatus !== statusFilter) return false;
    if (catFilter !== 'all' && b.category !== catFilter) return false;
    if (query) {
      const matchTitle = (b.title || '').toLowerCase().includes(query);
      const matchAuthor = (b.author || '').toLowerCase().includes(query);
      const matchCategory = (b.category || '').toLowerCase().includes(query);
      const matchPublisher = (b.publisher || '').toLowerCase().includes(query);
      const matchThemes = (b.themes || '').toLowerCase().includes(query);
      const matchSummary = (b.summary || '').toLowerCase().includes(query);
      if (!matchTitle && !matchAuthor && !matchCategory && !matchPublisher && !matchThemes && !matchSummary) {
        return false;
      }
    }
    return true;
  });

  if (filtered.length === 0) {
    grid.innerHTML = `
      <div style="text-align: center; padding: 4rem 1rem; color: var(--text-muted); width: 100%;">
        <p style="font-size: 1.2rem; font-weight: 600;">Nenhum livro encontrado com esses filtros.</p>
        <p style="font-size: 0.9rem; margin-top: 0.5rem;">Tente ajustar o termo de busca ou selecionar outro tema teológico acima.</p>
        <button class="btn btn-secondary btn-sm" id="btn-reset-lib-filters" style="margin-top: 1rem;">
          🔄 Limpar Filtros da Estante
        </button>
      </div>
    `;
    const resetBtn = document.getElementById('btn-reset-lib-filters');
    if (resetBtn) {
      resetBtn.addEventListener('click', () => {
        state.bookStatusFilter = 'all';
        state.bookCategoryFilter = 'all';
        state.bookSearchQuery = '';
        const searchInput = document.getElementById('library-search-input');
        if (searchInput) searchInput.value = '';
        const catSelect = document.getElementById('library-category-select');
        if (catSelect) catSelect.value = 'all';
        document.querySelectorAll('[data-book-status]').forEach(c => {
          c.classList.toggle('active', c.getAttribute('data-book-status') === 'all');
        });
        document.querySelectorAll('.lib-stat-pill').forEach(c => {
          c.classList.toggle('active', c.getAttribute('data-status-filter') === 'all');
        });
        renderLibrary();
      });
    }
    return;
  }

  // Renderização: Modo Agrupado por Tema vs Grade Direta
  if (state.bookViewMode === 'grouped') {
    // Agrupa os livros filtrados por categoria
    const groups = {};
    filtered.forEach(b => {
      const cat = b.category || 'Outros Temas Teológicos';
      if (!groups[cat]) groups[cat] = [];
      groups[cat].push(b);
    });

    // Ordena de acordo com a lista canônica de categorias
    const sortedCategories = CANONICAL_CATEGORIES.filter(c => groups[c.name]);
    Object.keys(groups).forEach(catName => {
      if (!CANONICAL_CATEGORIES.some(c => c.name === catName)) {
        sortedCategories.push({ name: catName, icon: '📚', plan: 'Apoio Teológico Geral' });
      }
    });

    grid.innerHTML = sortedCategories.map(cat => {
      const bList = groups[cat.name];
      return `
        <div class="thematic-group-section" style="margin-bottom: 2.5rem; width: 100%;">
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.6rem; padding-bottom: 0.6rem; border-bottom: 1px solid var(--border-subtle); margin-bottom: 1.2rem;">
            <div style="display: flex; align-items: center; gap: 0.6rem;">
              <span style="font-size: 1.4rem;">${cat.icon}</span>
              <h3 style="font-family: var(--font-serif); font-size: 1.25rem; color: #fff;">${escapeHtml(cat.name)}</h3>
              <span class="tag-badge" style="background: rgba(255,255,255,0.06); color: var(--gold-light);">${bList.length} ${bList.length === 1 ? 'livro' : 'livros'}</span>
            </div>
            <div class="tag-badge" style="color: var(--text-muted); font-size: 0.78rem;">
              📅 Plano: ${escapeHtml(cat.plan)}
            </div>
          </div>
          <div class="library-shelf-container">
            ${bList.map(createBookCardHtml).join('')}
          </div>
        </div>
      `;
    }).join('');
  } else {
    // Modo Grade Completa Direta
    grid.innerHTML = `
      <div class="library-shelf-container" style="width: 100%;">
        ${filtered.map(createBookCardHtml).join('')}
      </div>
    `;
  }

  // Vincula eventos nos elementos renderizados
  attachLibraryItemEvents(document.getElementById('tab-library'));
}

function attachLibraryItemEvents(container) {
  if (!container) return;

  // 1. Mudança de status pelo seletor dropdown
  container.querySelectorAll('.select-status-dropdown').forEach(sel => {
    sel.addEventListener('change', (e) => {
      e.stopPropagation();
      const id = parseInt(sel.getAttribute('data-book-id'), 10);
      updateBookStatus(id, sel.value);
    });
  });

  // 2. Abrir Modal de Detalhes
  container.querySelectorAll('.open-book-detail-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const id = parseInt(btn.getAttribute('data-id'), 10);
      openBookDetailModal(id);
    });
  });

  // 3. Definir Livro de Cabeceira
  container.querySelectorAll('.set-bedside-btn').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.stopPropagation();
      const id = parseInt(btn.getAttribute('data-id'), 10);
      try {
        await apiPost(`/books/${id}/bedside`, {});
        showToast('Livro definido como Livro de Cabeceira Oficial!');
        await fetchBooks();
        await fetchTodayData();
      } catch (err) {
        showToast(err.message, 'error');
      }
    });
  });

  // 4. Editar livro
  container.querySelectorAll('.edit-book-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const id = parseInt(btn.getAttribute('data-id'), 10);
      openEditBookModal(id);
    });
  });

  // 5. Excluir livro
  container.querySelectorAll('.delete-book-btn').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.stopPropagation();
      const id = parseInt(btn.getAttribute('data-id'), 10);
      if (confirm('Tem certeza que deseja remover este livro da sua estante?')) {
        try {
          await apiDelete(`/books/${id}`);
          showToast('Livro removido da sua estante!');
          await fetchBooks();
          await fetchStats();
        } catch (err) {
          showToast(err.message, 'error');
        }
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
  if (document.getElementById('book-cover-image-input')) document.getElementById('book-cover-image-input').value = '';
  if (document.getElementById('book-is-bedside-input')) document.getElementById('book-is-bedside-input').checked = false;
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
  if (document.getElementById('book-cover-image-input')) {
    document.getElementById('book-cover-image-input').value = book.cover_image || '';
  }
  if (document.getElementById('book-is-bedside-input')) {
    document.getElementById('book-is-bedside-input').checked = (book.is_bedside === 1);
  }

  document.getElementById('book-modal').classList.add('open');
}

// ================= MODAL DETALHES DA OBRA & STATUS =================
function openBookDetailModal(bookId) {
  const book = state.books.find(b => b.id === bookId);
  if (!book) return;

  const modal = document.getElementById('book-detail-modal');
  const titleEl = document.getElementById('book-detail-modal-title');
  const bodyEl = document.getElementById('book-detail-modal-body');
  if (!modal || !bodyEl) return;

  if (titleEl) titleEl.textContent = book.title;
  const bStatus = book.reading_status || book.status || 'Pendente';
  const isBedside = book.is_bedside === 1;
  const themesList = (book.themes || '').split(',').map(t => t.trim()).filter(Boolean);

  bodyEl.innerHTML = `
    <div style="display: flex; flex-direction: column; gap: 1.2rem;">
      <div class="book-card-spine-preview" style="background: ${book.cover_color || '#1e3a8a'}; height: 5px;"></div>
      
      <div>
        <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 0.5rem; flex-wrap: wrap;">
          <h3 style="font-family: var(--font-serif); font-size: 1.6rem; color: #fff;">${escapeHtml(book.title)}</h3>
          ${isBedside ? '<span class="tag-badge" style="background: rgba(212,175,55,0.2); color: var(--gold-light); border-color: var(--gold-border);">⭐ Cabeceira Oficial</span>' : ''}
        </div>
        <p style="font-size: 0.95rem; color: var(--gold-light); margin-top: 0.3rem;">
          <strong>${escapeHtml(book.author)}</strong> • ${escapeHtml(book.publisher || 'CPAD / Editora Teológica')} ${book.year ? `(${book.year})` : ''}
        </p>
      </div>

      <div style="background: var(--bg-tertiary); padding: 1rem; border-radius: var(--radius-md); border: 1px solid var(--border-subtle); display: flex; flex-direction: column; gap: 0.5rem;">
        <div style="font-size: 0.85rem;">
          <span style="color: var(--text-muted); font-weight: 700;">🏷️ Categoria Teológica:</span>
          <span style="color: var(--gold-light); font-weight: 700; margin-left: 0.3rem;">${escapeHtml(book.category || 'Teologia Geral')}</span>
        </div>
        <div style="font-size: 0.85rem;">
          <span style="color: var(--text-muted); font-weight: 700;">🔗 Vinculado ao Plano:</span>
          <span style="color: #fff; margin-left: 0.3rem;">${escapeHtml(book.plan_link || 'Todos os 365 Dias')}</span>
        </div>
        <div style="font-size: 0.85rem;">
          <span style="color: var(--text-muted); font-weight: 700;">🔖 Temas:</span>
          <span style="margin-left: 0.3rem;">${themesList.map(t => `<span class="tag-badge">#${escapeHtml(t)}</span>`).join(' ')}</span>
        </div>
      </div>

      <div>
        <h5 style="color: #fff; font-size: 0.95rem; font-weight: 700; margin-bottom: 0.4rem;">📖 Resumo & Profundidade do Livro</h5>
        <p style="color: #cbd5e1; font-size: 0.9rem; line-height: 1.6;">${escapeHtml(book.summary || 'Excelente literatura teológica para aprofundar sua compreensão e prática bíblica.')}</p>
      </div>

      <div style="background: var(--bg-secondary); padding: 1rem; border-radius: var(--radius-md); border: 1px solid var(--border-subtle);">
        <label for="detail-status-select" style="display: block; font-size: 0.85rem; color: var(--gold-light); font-weight: 700; margin-bottom: 0.4rem;">
          Seu Status de Leitura Pessoal:
        </label>
        <select id="detail-status-select" class="standard-select" style="width: 100%;">
          <option value="Pendente" ${bStatus === 'Pendente' ? 'selected' : ''}>⏳ Pendente (Fila de Leitura)</option>
          <option value="Em Andamento" ${bStatus === 'Em Andamento' ? 'selected' : ''}>📖 Em Andamento (Lendo Atualmente)</option>
          <option value="Finalizado" ${bStatus === 'Finalizado' ? 'selected' : ''}>✅ Finalizado (Leitura Concluída)</option>
        </select>
      </div>

      <div>
        <label for="detail-notes-input" style="display: block; font-size: 0.85rem; color: var(--text-muted); font-weight: 700; margin-bottom: 0.4rem;">
          Suas Anotações Pessoais & Insights do Livro:
        </label>
        <textarea id="detail-notes-input" rows="4" class="standard-textarea" style="width: 100%;" placeholder="Registre suas anotações, capítulos lidos, citações marcantes e aplicações para o ministério e vida diária...">${escapeHtml(book.user_notes || book.personal_notes || '')}</textarea>
      </div>

      <div style="display: flex; gap: 0.8rem; justify-content: flex-end; align-items: center; border-top: 1px solid var(--border-subtle); padding-top: 1rem; margin-top: 0.5rem;">
        ${!isBedside ? `
          <button class="btn btn-secondary btn-sm" id="modal-set-bedside-btn">
            <span>⭐</span> Definir como Cabeceira Oficial
          </button>
        ` : ''}
        <button class="btn btn-primary btn-sm" id="modal-save-notes-btn">
          <span>💾</span> Salvar Status e Anotações
        </button>
      </div>
    </div>
  `;

  modal.classList.add('open');

  const saveBtn = document.getElementById('modal-save-notes-btn');
  if (saveBtn) {
    saveBtn.addEventListener('click', async () => {
      const newStatus = document.getElementById('detail-status-select').value;
      const notes = document.getElementById('detail-notes-input').value;
      await updateBookStatus(book.id, newStatus, notes);
      modal.classList.remove('open');
    });
  }

  const setBedsideBtn = document.getElementById('modal-set-bedside-btn');
  if (setBedsideBtn) {
    setBedsideBtn.addEventListener('click', async () => {
      await apiPost(`/books/${book.id}/bedside`, {});
      showToast('Livro definido como Livro de Cabeceira Oficial!');
      modal.classList.remove('open');
      await fetchBooks();
      await fetchTodayData();
    });
  }
}

// ================= EVENT LISTENERS =================
function setupEventListeners() {
  // 1. Navegação de abas (Desktop e Mobile)
  document.querySelectorAll('.nav-btn, .mobile-nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const tabId = btn.getAttribute('data-tab');
      switchTab(tabId);
    });
  });

  // 2. Alternância de tema
  const themeBtn = document.getElementById('theme-toggle-btn');
  if (themeBtn) themeBtn.addEventListener('click', toggleTheme);

  // 3. Seletor de Perfil no Topo
  const userHeaderBtn = document.getElementById('header-user-btn');
  if (userHeaderBtn) {
    userHeaderBtn.addEventListener('click', () => {
      document.getElementById('switch-profile-modal').classList.add('open');
    });
  }

  const closeSwitchModalBtn = document.getElementById('close-switch-modal-btn');
  if (closeSwitchModalBtn) {
    closeSwitchModalBtn.addEventListener('click', () => {
      document.getElementById('switch-profile-modal').classList.remove('open');
    });
  }

  const quickNewMemberBtn = document.getElementById('btn-quick-new-member');
  if (quickNewMemberBtn) {
    quickNewMemberBtn.addEventListener('click', () => {
      document.getElementById('switch-profile-modal').classList.remove('open');
      openAddMemberModal();
    });
  }

  // 4. Membro Modal (Cadastrar / Editar)
  const openAddMemberBtn = document.getElementById('open-add-member-modal-btn');
  if (openAddMemberBtn) openAddMemberBtn.addEventListener('click', openAddMemberModal);

  const closeMemberModalBtn = document.getElementById('close-member-modal-btn');
  const cancelMemberModalBtn = document.getElementById('cancel-member-modal-btn');
  if (closeMemberModalBtn) closeMemberModalBtn.addEventListener('click', () => document.getElementById('member-modal').classList.remove('open'));
  if (cancelMemberModalBtn) cancelMemberModalBtn.addEventListener('click', () => document.getElementById('member-modal').classList.remove('open'));

  const memberForm = document.getElementById('member-form');
  if (memberForm) {
    memberForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const memberId = document.getElementById('member-id-input').value;
      const avatarChecked = document.querySelector('input[name="member_avatar"]:checked');
      const payload = {
        name: document.getElementById('member-name-input').value.trim(),
        phone: document.getElementById('member-phone-input').value.trim(),
        current_day: parseInt(document.getElementById('member-day-input').value || '1', 10),
        avatar_icon: avatarChecked ? avatarChecked.value : '🕊️'
      };

      try {
        if (memberId) {
          await apiPut(`/users/${memberId}`, payload);
          showToast('Membro atualizado com sucesso!');
        } else {
          const res = await apiPost('/users', payload);
          showToast('Novo membro adicionado!');
          // Se for o primeiro ou recém-criado, pergunta se quer alternar
          if (res.id) {
            state.currentUserId = res.id;
            localStorage.setItem('jb365_user_id', res.id);
          }
        }
        document.getElementById('member-modal').classList.remove('open');
        await loadInitialData();
      } catch (err) {
        showToast('Erro ao salvar membro: ' + err.message, 'error');
      }
    });
  }

  // 5. Botão Concluir Hoje
  const completeBtn = document.getElementById('toggle-complete-btn');
  if (completeBtn) {
    completeBtn.addEventListener('click', async () => {
      try {
        const res = await apiPost(`/day/${state.currentDay}/complete`);
        showToast(res.new_status === 'completed' ? '🎉 Parabéns! Estudo de hoje concluído!' : 'Estudo marcado como pendente.');
        await fetchTodayData();
        await fetchStats();
        await fetchPlan();
        await fetchUsers(); // Atualiza barra de progresso do usuário
      } catch (e) {
        showToast('Erro ao alternar status do dia.', 'error');
      }
    });
  }

  // 6. Navegação Dia Anterior / Próximo
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

  // 7. Salvar anotações do diário
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
        showToast('Versículo copiado!');
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

  // Botão de Atualizar Versão / Limpar Cache PWA
  const forceUpdateBtn = document.getElementById('btn-force-update');
  if (forceUpdateBtn) {
    forceUpdateBtn.addEventListener('click', async () => {
      forceUpdateBtn.disabled = true;
      forceUpdateBtn.innerHTML = '<span>⏳</span> Limpando Cache...';
      try {
        if ('serviceWorker' in navigator) {
          const registrations = await navigator.serviceWorker.getRegistrations();
          for (let reg of registrations) {
            await reg.unregister();
          }
        }
        if ('caches' in window) {
          const cacheKeys = await caches.keys();
          for (let key of cacheKeys) {
            await caches.delete(key);
          }
        }
        localStorage.removeItem('jb365_sw_version');
        showToast('Atualização concluída com sucesso! Recarregando sistema...');
        setTimeout(() => {
          window.location.reload(true);
        }, 600);
      } catch (err) {
        showToast('Erro ao limpar cache: ' + err.message, 'error');
        forceUpdateBtn.disabled = false;
        forceUpdateBtn.innerHTML = '<span>🔄</span> Atualizar Versão / Limpar Cache';
      }
    });
  }

  // 8. Filtros do Plano 365
  document.querySelectorAll('.plan-filters-card .filter-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      document.querySelectorAll('.plan-filters-card .filter-chip').forEach(c => c.classList.remove('active'));
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

  // 8.1 Controles da Biblioteca Teológica
  // Filtros de status (Chips)
  document.querySelectorAll('[data-book-status]').forEach(chip => {
    chip.addEventListener('click', () => {
      document.querySelectorAll('[data-book-status]').forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      const statusVal = chip.getAttribute('data-book-status');
      state.bookStatusFilter = statusVal;
      
      // Sincroniza pílulas do ribbon
      document.querySelectorAll('.lib-stat-pill').forEach(pill => {
        pill.classList.toggle('active', pill.getAttribute('data-status-filter') === statusVal);
      });
      renderLibrary();
    });
  });

  // Filtros do ribbon superior da biblioteca
  document.querySelectorAll('.lib-stat-pill').forEach(pill => {
    pill.addEventListener('click', () => {
      document.querySelectorAll('.lib-stat-pill').forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      const statusVal = pill.getAttribute('data-status-filter');
      state.bookStatusFilter = statusVal;

      // Sincroniza chips
      document.querySelectorAll('[data-book-status]').forEach(c => {
        c.classList.toggle('active', c.getAttribute('data-book-status') === statusVal);
      });
      renderLibrary();
    });
  });

  // Busca na Biblioteca
  const libSearchInput = document.getElementById('library-search-input');
  if (libSearchInput) {
    libSearchInput.addEventListener('input', (e) => {
      state.bookSearchQuery = e.target.value;
      renderLibrary();
    });
  }

  const clearLibSearchBtn = document.getElementById('clear-lib-search-btn');
  if (clearLibSearchBtn) {
    clearLibSearchBtn.addEventListener('click', () => {
      if (libSearchInput) libSearchInput.value = '';
      state.bookSearchQuery = '';
      renderLibrary();
    });
  }

  // Seletor de Categoria Teológica
  const libCatSelect = document.getElementById('library-category-select');
  if (libCatSelect) {
    libCatSelect.addEventListener('change', (e) => {
      state.bookCategoryFilter = e.target.value;
      renderLibrary();
    });
  }

  // Alternância do Modo de Visualização (Agrupado por Tema vs Grade)
  const btnViewAgrupado = document.getElementById('btn-view-grouped');
  const btnViewGrade = document.getElementById('btn-view-grid');
  if (btnViewAgrupado && btnViewGrade) {
    btnViewAgrupado.addEventListener('click', () => {
      btnViewAgrupado.classList.add('active');
      btnViewGrade.classList.remove('active');
      state.bookViewMode = 'grouped';
      renderLibrary();
    });
    btnViewGrade.addEventListener('click', () => {
      btnViewGrade.classList.add('active');
      btnViewAgrupado.classList.remove('active');
      state.bookViewMode = 'grid';
      renderLibrary();
    });
  }

  // 9. Modais de Livro
  const addBookBtn = document.getElementById('open-add-book-modal-btn');
  if (addBookBtn) addBookBtn.addEventListener('click', openAddBookModal);

  const closeBookModalBtn = document.getElementById('close-book-modal-btn');
  const cancelBookModalBtn = document.getElementById('cancel-book-modal-btn');
  if (closeBookModalBtn) closeBookModalBtn.addEventListener('click', () => document.getElementById('book-modal').classList.remove('open'));
  if (cancelBookModalBtn) cancelBookModalBtn.addEventListener('click', () => document.getElementById('book-modal').classList.remove('open'));

  const closeDayModalBtn = document.getElementById('close-day-modal-btn');
  if (closeDayModalBtn) closeDayModalBtn.addEventListener('click', () => document.getElementById('day-detail-modal').classList.remove('open'));

  const closeBookDetailModalBtn = document.getElementById('close-book-detail-modal-btn');
  if (closeBookDetailModalBtn) {
    closeBookDetailModalBtn.addEventListener('click', () => {
      const modal = document.getElementById('book-detail-modal');
      if (modal) modal.classList.remove('open');
    });
  }

  // Fechar qualquer modal ao clicar fora (no backdrop)
  document.querySelectorAll('.modal-overlay').forEach(modal => {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.classList.remove('open');
      }
    });
  });

  // 10. Submit formulário de livro
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
        cover_image: document.getElementById('book-cover-image-input') ? document.getElementById('book-cover-image-input').value.trim() : null,
        is_bedside: document.getElementById('book-is-bedside-input') && document.getElementById('book-is-bedside-input').checked ? 1 : 0,
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
        await fetchTodayData();
      } catch (err) {
        showToast('Erro ao salvar livro: ' + err.message, 'error');
      }
    });
  }

  // 11. Salvar configurações do perfil atual
  const settingsForm = document.getElementById('settings-form');
  if (settingsForm) {
    settingsForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const currentName = document.getElementById('cfg-user-name').value.trim();
      const currentPhone = document.getElementById('cfg-phone').value.trim();
      const currentDayVal = parseInt(document.getElementById('cfg-current-day').value || '1', 10);

      try {
        if (state.currentUser) {
          await apiPut(`/users/${state.currentUser.id}`, {
            name: currentName,
            phone: currentPhone,
            avatar_icon: state.currentUser.avatar_icon || '🕊️',
            current_day: currentDayVal
          });
        }
        showToast('Perfil e configurações atualizados!');
        await loadInitialData();
      } catch (err) {
        showToast('Erro ao salvar configurações.', 'error');
      }
    });
  }

  // 12. Disparar Envio em Massa para Todos os Membros
  const broadcastBtn = document.getElementById('broadcast-all-members-btn');
  if (broadcastBtn) {
    broadcastBtn.addEventListener('click', async () => {
      try {
        broadcastBtn.disabled = true;
        broadcastBtn.textContent = '⏳ Disparando...';
        const res = await apiPost('/whatsapp/broadcast');
        showToast(res.message);
      } catch (err) {
        showToast(err.message, 'error');
      } finally {
        broadcastBtn.disabled = false;
        broadcastBtn.innerHTML = '<span>🚀</span> Disparar para Todos os Membros';
      }
    });
  }

  // Bot Login WhatsApp (QR Code)
  const botLoginBtn = document.getElementById('bot-login-btn');
  if (botLoginBtn) {
    botLoginBtn.addEventListener('click', async () => {
      showToast('Abrindo WhatsApp Web para leitura de QR Code...');
      await apiPost('/whatsapp/login');
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
  document.querySelectorAll('.mobile-nav-btn').forEach(b => b.classList.remove('active'));

  const targetPane = document.getElementById(tabId);
  const targetBtn = document.querySelector(`.nav-btn[data-tab="${tabId}"]`);
  const targetMobileBtn = document.querySelector(`.mobile-nav-btn[data-tab="${tabId}"]`);

  if (targetPane) targetPane.classList.add('active');
  if (targetBtn) targetBtn.classList.add('active');
  if (targetMobileBtn) targetMobileBtn.classList.add('active');

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
  return String(str).replace(/[&<>'"]/g, 
    tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
  );
}

/* ==========================================================================
   TAMALE HOUSE MARKET - MAIN UTILITY & AUTH MODULE
   ========================================================================== */

const TAMALE_HOUSES_KEY = 'thm_houses_data';
const CURRENT_USER_KEY = 'thm_current_user';
const SAVED_FAVOURITES_KEY = 'thm_saved_favourites';
const ENQUIRIES_KEY = 'thm_enquiries_list';

// Global Initializer
document.addEventListener('DOMContentLoaded', async () => {
  initNavigation();
  updateUserNavUI();
  initPasswordToggles();
  await syncCurrentUserWithServer();
  await syncFavouritesWithServer();
});

function initPasswordToggles() {
  document.querySelectorAll('.toggle-password-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const targetId = btn.getAttribute('data-target');
      const input = document.getElementById(targetId);
      if (!input) return;

      const eyeIcon = btn.querySelector('.eye-icon');
      const eyeOffIcon = btn.querySelector('.eye-off-icon');

      if (input.type === 'password') {
        input.type = 'text';
        if (eyeIcon) eyeIcon.style.display = 'none';
        if (eyeOffIcon) eyeOffIcon.style.display = 'inline-block';
      } else {
        input.type = 'password';
        if (eyeIcon) eyeIcon.style.display = 'inline-block';
        if (eyeOffIcon) eyeOffIcon.style.display = 'none';
      }
    });
  });
}

// Mobile Nav Toggle & Nav Link Interceptors
function initNavigation() {
  const toggleBtn = document.querySelector('.nav-toggle');
  const navMenu = document.querySelector('.nav-menu');

  if (toggleBtn && navMenu) {
    toggleBtn.setAttribute('aria-expanded', 'false');
    toggleBtn.addEventListener('click', () => {
      const isOpen = navMenu.classList.toggle('active');
      toggleBtn.setAttribute('aria-expanded', String(isOpen));
    });

    navMenu.querySelectorAll('a').forEach(link => link.addEventListener('click', () => {
      navMenu.classList.remove('active');
      toggleBtn.setAttribute('aria-expanded', 'false');
    }));

    document.addEventListener('keydown', event => {
      if (event.key === 'Escape') {
        navMenu.classList.remove('active');
        toggleBtn.setAttribute('aria-expanded', 'false');
      }
    });
  }

  // Highlight active link based on window location
  const currentPath = window.location.pathname;
  const navLinks = document.querySelectorAll('.nav-link');
  navLinks.forEach(link => {
    if (link.getAttribute('href') && currentPath.endsWith(link.getAttribute('href'))) {
      link.classList.add('active');
    }
  });
}

// User Session Management
function getCurrentUser() {
  const userJson = localStorage.getItem(CURRENT_USER_KEY);
  try { return userJson ? JSON.parse(userJson) : null; } catch (e) { return null; }
}

function setCurrentUser(user) {
  if (user) {
    localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(user));
  } else {
    localStorage.removeItem(CURRENT_USER_KEY);
  }
}

async function syncCurrentUserWithServer() {
  try {
    const res = await fetch('/api/auth/me');
    if (res.ok) {
      const data = await res.json();
      if (data.authenticated && data.user) {
        setCurrentUser(data.user);
        updateUserNavUI();
        return data.user;
      } else {
        localStorage.removeItem(CURRENT_USER_KEY);
        updateUserNavUI();
        return null;
      }
    }
  } catch (e) {
    // Offline or server temporarily unreachable
  }
  return getCurrentUser();
}

async function logoutUser() {
  try {
    await fetch('/api/auth/logout', { method: 'POST' });
  } catch (e) {}
  localStorage.removeItem(CURRENT_USER_KEY);
  const isDashboard = window.location.pathname.includes('/landlord/') || window.location.pathname.includes('/tenant/');
  if (isDashboard) {
    window.location.href = '../login.html';
  } else {
    window.location.href = 'login.html';
  }
}

function updateUserNavUI() {
  const user = getCurrentUser();
  const navActions = document.querySelector('.nav-actions');

  if (!navActions) return;

  if (user) {
    const isInsidePortal = window.location.pathname.includes('/landlord/') || window.location.pathname.includes('/tenant/');
    const dashboardPath = user.role === 'landlord'
      ? (isInsidePortal ? 'dashboard.html' : 'landlord/dashboard.html')
      : (isInsidePortal ? 'dashboard.html' : 'tenant/dashboard.html');

    navActions.innerHTML = `
      <a href="${dashboardPath}" class="btn btn-outline btn-sm">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
        ${escapeHTML(user.full_name || user.username)} (${escapeHTML(user.role.toUpperCase())})
      </a>
      <button onclick="logoutUser()" class="btn btn-primary btn-sm">Logout</button>
    `;
  }
}

// Contact Action Guard - Requires Authentication
function handleContactClick(e) {
  const user = getCurrentUser();
  if (!user) {
    e.preventDefault();
    e.stopPropagation();
    alert('Account Required: You must create an account or log in to contact landlords or arrange viewings on Tamale House Market.');
    const isDashboard = window.location.pathname.includes('/landlord/') || window.location.pathname.includes('/tenant/');
    window.location.href = isDashboard ? '../login.html' : 'login.html';
    return false;
  }
  return true;
}

// WhatsApp Link Generator
function formatGhanaPhone(phone) {
  if (!phone) return '233241234567';
  let clean = phone.replace(/[^0-9]/g, '');
  if (clean.startsWith('0')) {
    clean = '233' + clean.substring(1);
  }
  if (!clean.startsWith('233')) {
    clean = '233' + clean;
  }
  return clean;
}

function generateWhatsAppLink(phone, houseTitle, houseId) {
  const formattedPhone = formatGhanaPhone(phone || '0241234567');
  const textMessage = `Hello, I found your property "${houseTitle}" (Ref ID: ${houseId}) on Tamale House Market and I would like to inquire about its availability and arrange a viewing.`;
  const encodedMsg = encodeURIComponent(textMessage);
  return `https://wa.me/${formattedPhone}?text=${encodedMsg}`;
}

function generatePhoneLink(phone) {
  const cleanPhone = (phone || '0241234567').replace(/[^0-9+]/g, '');
  return `tel:${cleanPhone}`;
}

// Saved Properties (Favourites) Manager
function favKey() {
  const u = getCurrentUser();
  return u ? `${SAVED_FAVOURITES_KEY}_${u.username}` : SAVED_FAVOURITES_KEY;
}

function getSavedFavourites() {
  try { return JSON.parse(localStorage.getItem(favKey()) || '[]'); } catch (e) { return []; }
}

async function syncFavouritesWithServer() {
  const user = getCurrentUser();
  if (!user) return;
  try {
    const res = await fetch('/api/favourites');
    if (res.ok) {
      const favList = await res.json();
      const ids = favList.map(h => h.house_id);
      localStorage.setItem(favKey(), JSON.stringify(ids));
    }
  } catch (e) {}
}

async function toggleFavourite(houseId) {
  const user = getCurrentUser();
  if (!user) {
    alert('Account Required: You must create an account or log in to save properties to your favourites list.');
    const isDashboard = window.location.pathname.includes('/landlord/') || window.location.pathname.includes('/tenant/');
    window.location.href = isDashboard ? '../login.html' : 'login.html';
    return false;
  }

  let favourites = getSavedFavourites();
  const index = favourites.indexOf(houseId);
  const isCurrentlySaved = index >= 0;

  try {
    if (isCurrentlySaved) {
      await fetch(`/api/favourites/${encodeURIComponent(houseId)}`, { method: 'DELETE' });
      favourites.splice(index, 1);
      localStorage.setItem(favKey(), JSON.stringify(favourites));
      return false;
    } else {
      await fetch(`/api/favourites/${encodeURIComponent(houseId)}`, { method: 'POST' });
      favourites.push(houseId);
      localStorage.setItem(favKey(), JSON.stringify(favourites));
      return true;
    }
  } catch (e) {
    if (isCurrentlySaved) {
      favourites.splice(index, 1);
      localStorage.setItem(favKey(), JSON.stringify(favourites));
      return false;
    } else {
      favourites.push(houseId);
      localStorage.setItem(favKey(), JSON.stringify(favourites));
      return true;
    }
  }
}

function isFavourite(houseId) {
  const favourites = getSavedFavourites();
  return favourites.includes(houseId);
}

// Format Currency
function formatGHS(amount) {
  return `GH₵ ${Number(amount || 0).toLocaleString('en-GH')}`;
}

// Shared helpers
function escapeHTML(v) {
  return String(v ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

function safeParse(key, fallback) {
  try { const v = localStorage.getItem(key); return v ? JSON.parse(v) : fallback; } catch (e) { return fallback; }
}

function isHouseAvailable(h) {
  if (typeof h.available === 'boolean') return h.available;
  return h.water === 'Available';
}

function nextHouseId(houses) {
  const max = houses.reduce((m, h) => {
    const n = parseInt(String(h.house_id).replace(/\D/g, ''), 10);
    return isNaN(n) ? m : Math.max(m, n);
  }, 0);
  return `TAM-${String(max + 1).padStart(3, '0')}`;
}

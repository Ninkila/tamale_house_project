/* ==========================================================================
   TAMALE HOUSE MARKET - MAIN UTILITY & AUTH MODULE
   ========================================================================== */

const TAMALE_HOUSES_KEY = 'thm_houses_data';
const CURRENT_USER_KEY = 'thm_current_user';
const SAVED_FAVOURITES_KEY = 'thm_saved_favourites';
const ENQUIRIES_KEY = 'thm_enquiries_list';

// Global Initializer
document.addEventListener('DOMContentLoaded', () => {
  initNavigation();
  updateUserNavUI();
});

// Mobile Nav Toggle
function initNavigation() {
  const toggleBtn = document.querySelector('.nav-toggle');
  const navMenu = document.querySelector('.nav-menu');

  if (toggleBtn && navMenu) {
    toggleBtn.addEventListener('click', () => {
      navMenu.classList.toggle('active');
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
  return userJson ? JSON.parse(userJson) : null;
}

function setCurrentUser(user) {
  localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(user));
}

function logoutUser() {
  localStorage.removeItem(CURRENT_USER_KEY);
  // Redirect to home or login page
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
    const dashboardPath = user.role === 'landlord' ? 'landlord/dashboard.html' : 'tenant/dashboard.html';
    const relPath = window.location.pathname.includes('/landlord/') || window.location.pathname.includes('/tenant/') ? '#' : dashboardPath;

    navActions.innerHTML = `
      <a href="${relPath}" class="btn btn-outline btn-sm">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
        ${user.full_name || user.username} (${user.role.toUpperCase()})
      </a>
      <button onclick="logoutUser()" class="btn btn-primary btn-sm">Logout</button>
    `;
  }
}

// WhatsApp Link Generator
function formatGhanaPhone(phone) {
  if (!phone) return null;
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
  const formattedPhone = formatGhanaPhone(phone || '0240000000');
  const textMessage = `Hello, I found your property "${houseTitle}" (Ref ID: ${houseId}) on Tamale House Market and I would like to inquire about its availability and arrange a viewing.`;
  const encodedMsg = encodeURIComponent(textMessage);
  return `https://wa.me/${formattedPhone}?text=${encodedMsg}`;
}

function generatePhoneLink(phone) {
  const cleanPhone = (phone || '0240000000').replace(/[^0-9+]/g, '');
  return `tel:${cleanPhone}`;
}

// Saved Properties (Favourites) Manager
function getSavedFavourites() {
  const data = localStorage.getItem(SAVED_FAVOURITES_KEY);
  return data ? JSON.parse(data) : [];
}

function toggleFavourite(houseId) {
  const user = getCurrentUser();
  if (!user) {
    alert('Please log in to save properties to your favourites list.');
    window.location.href = window.location.pathname.includes('/landlord/') || window.location.pathname.includes('/tenant/') ? '../login.html' : 'login.html';
    return false;
  }

  let favourites = getSavedFavourites();
  const index = favourites.indexOf(houseId);

  if (index >= 0) {
    favourites.splice(index, 1);
    localStorage.setItem(SAVED_FAVOURITES_KEY, JSON.stringify(favourites));
    return false;
  } else {
    favourites.push(houseId);
    localStorage.setItem(SAVED_FAVOURITES_KEY, JSON.stringify(favourites));
    return true;
  }
}

function isFavourite(houseId) {
  const favourites = getSavedFavourites();
  return favourites.includes(houseId);
}

// Format Currency
function formatGHS(amount) {
  return `GH₵ ${Number(amount).toLocaleString('en-GH')}`;
}

/* ==========================================================================
   TAMALE HOUSE MARKET - TENANT DASHBOARD MODULE
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  verifyTenantAccess();
  initTenantDashboard();
  initSavedPropertiesPage();
  initTenantEnquiriesPage();
  initTenantSettingsPage();
});

function verifyTenantAccess() {
  const isTenantPage = window.location.pathname.includes('/tenant/');
  if (!isTenantPage) return;

  const user = getCurrentUser();
  if (!user || user.role !== 'tenant') {
    alert('Access Restricted: This dashboard is reserved for registered Tenants.');
    window.location.href = '../login.html';
  }
}

function initTenantDashboard() {
  const savedCountEl = document.getElementById('tenant-stat-saved');
  const enquiriesCountEl = document.getElementById('tenant-stat-enquiries');

  if (!savedCountEl) return;

  const favourites = getSavedFavourites();
  const enquiries = safeParse(ENQUIRIES_KEY, []);
  const user = getCurrentUser();

  const myEnquiries = enquiries.filter(e => e.tenant_username === (user ? user.username : 'Guest'));

  savedCountEl.textContent = favourites.length;
  if (enquiriesCountEl) enquiriesCountEl.textContent = myEnquiries.length;
}

// Saved Properties Page
function initSavedPropertiesPage() {
  const container = document.getElementById('saved-properties-grid');
  if (!container) return;

  renderSavedPropertiesList();
}

function renderSavedPropertiesList() {
  const container = document.getElementById('saved-properties-grid');
  if (!container) return;

  const favourites = getSavedFavourites();
  const houses = getHousesData();
  const savedHouses = houses.filter(h => favourites.includes(h.house_id));

  if (savedHouses.length === 0) {
    container.innerHTML = `
      <div class="empty-state" style="grid-column: 1 / -1;">
        <svg class="empty-state-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/></svg>
        <h3>No Saved Properties</h3>
        <p>You haven't saved any rental properties yet. Browse houses in Tamale and click the heart icon to save listings here.</p>
        <a href="../houses.html" class="btn btn-primary">Browse Available Houses</a>
      </div>
    `;
    return;
  }

  container.innerHTML = savedHouses.map(house => renderHouseCard(house)).join('');
}

// Tenant Submitted Enquiries
function initTenantEnquiriesPage() {
  const container = document.getElementById('tenant-enquiries-list');
  if (!container) return;

  const enquiries = safeParse(ENQUIRIES_KEY, []);
  const user = getCurrentUser();

  const myEnquiries = enquiries.filter(e => e.tenant_username === (user ? user.username : 'Guest'));

  if (myEnquiries.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <svg class="empty-state-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
        <h3>No Enquiries Submitted</h3>
        <p>You haven't sent any direct property enquiries yet.</p>
        <a href="../houses.html" class="btn btn-accent">Explore Properties</a>
      </div>
    `;
    return;
  }

  container.innerHTML = myEnquiries.map(item => `
    <div style="background:var(--secondary); padding:1.5rem; border-radius:var(--radius-md); border:1px solid var(--border-color); margin-bottom:1rem; box-shadow:var(--shadow-sm);">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
        <div>
          <h4 style="font-size:1.1rem; color:var(--primary); font-weight:700;">${escapeHTML(item.house_title)}</h4>
          <span style="font-size:0.8rem; color:var(--text-muted);">Submitted on: ${escapeHTML(item.date)}</span>
        </div>
        <span class="badge-status-pill status-pending">${escapeHTML(item.status)}</span>
      </div>
      <p style="background:var(--bg-light); padding:1rem; border-radius:var(--radius-sm); font-size:0.95rem; color:var(--text-main);">
        "${escapeHTML(item.message)}"
      </p>
    </div>
  `).join('');
}

// Tenant Settings Page
function initTenantSettingsPage() {
  const form = document.getElementById('tenant-settings-form');
  if (!form) return;

  const user = getCurrentUser();
  if (user) {
    document.getElementById('tenant-fullname').value = user.full_name || '';
    document.getElementById('tenant-email').value = user.email || '';
  }

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const updatedUser = {
      ...user,
      full_name: document.getElementById('tenant-fullname').value,
      email: document.getElementById('tenant-email').value
    };
    setCurrentUser(updatedUser);
    alert('Profile information updated successfully!');
  });
}

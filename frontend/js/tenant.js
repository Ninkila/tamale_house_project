/* ==========================================================================
   TAMALE HOUSE MARKET - TENANT DASHBOARD MODULE
   ========================================================================== */

document.addEventListener('DOMContentLoaded', async () => {
  const isAuthorized = await verifyTenantAccess();
  if (!isAuthorized) return;

  await initTenantDashboard();
  await initSavedPropertiesPage();
  await initTenantEnquiriesPage();
  initTenantSettingsPage();
});

async function verifyTenantAccess() {
  const isTenantPage = window.location.pathname.includes('/tenant/');
  if (!isTenantPage) return true;

  const user = await syncCurrentUserWithServer();
  if (!user || user.role !== 'tenant') {
    alert('Access Restricted: This dashboard is reserved for registered Tenants.');
    window.location.href = '../login.html';
    return false;
  }

  const nameEl = document.getElementById('sidebar-tenant-name') || document.getElementById('tenant-name-heading');
  if (nameEl) nameEl.textContent = user.full_name || user.username;
  const avatarEl = document.querySelector('.sidebar-user .user-avatar');
  if (avatarEl && user.full_name) {
    avatarEl.textContent = user.full_name.split(' ').map(w => w[0]).join('').substring(0, 2).toUpperCase();
  }
  return true;
}

async function fetchTenantFavourites() {
  try {
    const res = await fetch('/api/favourites');
    if (res.ok) {
      const favs = await res.json();
      const ids = favs.map(h => h.house_id);
      localStorage.setItem(favKey(), JSON.stringify(ids));
      return favs;
    }
  } catch (err) {
    console.warn('Backend unavailable, falling back to local favourites.', err);
  }
  const favourites = getSavedFavourites();
  const houses = getHousesData();
  return houses.filter(h => favourites.includes(h.house_id));
}

async function fetchTenantEnquiries() {
  try {
    const res = await fetch('/api/tenant/enquiries');
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn('Backend unavailable for tenant enquiries.', err);
  }
  const user = getCurrentUser();
  const enquiries = safeParse(ENQUIRIES_KEY, []);
  return enquiries.filter(e => e.tenant_username === (user ? user.username : 'Guest'));
}

async function initTenantDashboard() {
  const savedCountEl = document.getElementById('tenant-stat-saved');
  const enquiriesCountEl = document.getElementById('tenant-stat-enquiries');

  if (!savedCountEl && !enquiriesCountEl) return;

  const favourites = await fetchTenantFavourites();
  const enquiries = await fetchTenantEnquiries();

  if (savedCountEl) savedCountEl.textContent = favourites.length;
  if (enquiriesCountEl) enquiriesCountEl.textContent = enquiries.length;
}

// Saved Properties Page
async function initSavedPropertiesPage() {
  const container = document.getElementById('saved-properties-grid');
  if (!container) return;

  await renderSavedPropertiesList();
}

async function renderSavedPropertiesList() {
  const container = document.getElementById('saved-properties-grid');
  if (!container) return;

  const savedHouses = await fetchTenantFavourites();

  if (savedHouses.length === 0) {
    container.innerHTML = `
      <div class="empty-state" style="grid-column: 1 / -1;">
        <svg class="empty-state-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/></svg>
        <h3>No Saved Properties</h3>
        <p>You haven't saved any rental properties yet. Browse houses in Tamale and click the heart icon to save listings here.</p>
        <a href="../houses.html" class="btn btn-primary" style="margin-top:1rem;">Browse Available Houses</a>
      </div>
    `;
    return;
  }

  container.innerHTML = savedHouses.map(house => renderHouseCard(house)).join('');
}

// Tenant Submitted Enquiries
async function initTenantEnquiriesPage() {
  const container = document.getElementById('tenant-enquiries-list');
  if (!container) return;

  const myEnquiries = await fetchTenantEnquiries();

  if (myEnquiries.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <svg class="empty-state-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
        <h3>No Enquiries Submitted</h3>
        <p>You haven't sent any direct property enquiries yet.</p>
        <a href="../houses.html" class="btn btn-accent" style="margin-top:1rem;">Explore Properties</a>
      </div>
    `;
    return;
  }

  container.innerHTML = myEnquiries.map(item => `
    <div style="background:var(--secondary); padding:1.5rem; border-radius:var(--radius-md); border:1px solid var(--border-color); margin-bottom:1rem; box-shadow:var(--shadow-sm);">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
        <div>
          <h4 style="font-size:1.1rem; color:var(--primary); font-weight:700;">${escapeHTML(item.house_title || 'Rental Listing')}</h4>
          <span style="font-size:0.8rem; color:var(--text-muted);">Ref: ${escapeHTML(item.property_id || '')}</span>
        </div>
        <span class="badge-status-pill status-pending">${escapeHTML(item.status || 'Pending')}</span>
      </div>
      <p style="background:var(--bg-light); padding:1rem; border-radius:var(--radius-sm); font-size:0.95rem; color:var(--text-main); margin:0;">
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
    const fn = document.getElementById('tenant-fullname');
    const em = document.getElementById('tenant-email');
    if (fn) fn.value = user.full_name || '';
    if (em) em.value = user.email || '';
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const fullName = document.getElementById('tenant-fullname').value.trim();

    try {
      const res = await fetch('/api/auth/profile', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ full_name: fullName })
      });
      if (res.ok) {
        const data = await res.json();
        setCurrentUser(data.user);
        alert('Profile information updated successfully!');
      } else {
        alert('Failed to update profile information.');
      }
    } catch (err) {
      alert('Network error while updating profile.');
    }
  });
}

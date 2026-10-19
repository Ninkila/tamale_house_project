/* ==========================================================================
   TAMALE HOUSE MARKET - LANDLORD DASHBOARD MODULE
   ========================================================================== */

let currentLandlordProperties = [];

document.addEventListener('DOMContentLoaded', async () => {
  const isAuthorized = await verifyLandlordAccess();
  if (!isAuthorized) return;

  await initLandlordDashboard();
  initAddPropertyForm();
  await initMyPropertiesPage();
  await initLandlordEnquiriesPage();
  initLandlordSettingsPage();
  ensureEditPropertyModal();
});

async function verifyLandlordAccess() {
  if (!window.location.pathname.includes('/landlord/')) return true;

  const user = await syncCurrentUserWithServer();
  if (!user || user.role !== 'landlord') {
    alert('Access Restricted: This dashboard is reserved for registered Landlords.');
    window.location.href = '../login.html';
    return false;
  }

  const nameEl = document.getElementById('sidebar-user-name');
  if (nameEl) nameEl.textContent = user.full_name || user.username;
  const avatarEl = document.querySelector('.sidebar-user .user-avatar');
  if (avatarEl && user.full_name) {
    avatarEl.textContent = user.full_name.split(' ').map(w => w[0]).join('').substring(0, 2).toUpperCase();
  }
  return true;
}

// Fetch only the authenticated landlord's own listings from PostgreSQL
async function fetchLandlordHouses() {
  try {
    const res = await fetch('/api/landlord/properties');
    if (res.ok) {
      currentLandlordProperties = await res.json();
      return currentLandlordProperties;
    }
  } catch (err) {
    console.warn('Backend unavailable, falling back to cached properties.', err);
  }
  const user = getCurrentUser();
  if (!user) return [];
  currentLandlordProperties = getHousesData().filter(h => h.owner_username === user.username || h.landlord_id === user.id);
  return currentLandlordProperties;
}

// Fetch enquiries submitted for this landlord's properties
async function fetchLandlordEnquiries() {
  try {
    const res = await fetch('/api/landlord/enquiries');
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn('Backend unavailable for landlord enquiries.', err);
  }
  const ids = new Set(currentLandlordProperties.map(h => h.house_id));
  return safeParse(ENQUIRIES_KEY, []).filter(e => ids.has(e.house_id));
}

async function initLandlordDashboard() {
  const totalCountEl = document.getElementById('stat-total-properties');
  if (!totalCountEl) return;

  const houses = await fetchLandlordHouses();
  const enquiries = await fetchLandlordEnquiries();
  const available = houses.filter(h => isHouseAvailable(h)).length;

  totalCountEl.textContent = houses.length;
  const set = (id, v) => { const el = document.getElementById(id); if (el) el.textContent = v; };
  set('stat-avail-properties', available);
  set('stat-unavail-properties', houses.length - available);
  set('stat-total-enquiries', enquiries.length);

  await renderLandlordPropertiesTable();
}

function initAddPropertyForm() {
  const form = document.getElementById('add-property-form');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const user = getCurrentUser();
    const val = id => (document.getElementById(id) || {}).value || '';

    const rent = parseFloat(val('prop-rent'));
    const rooms = parseInt(val('prop-rooms'), 10);
    const bathrooms = parseInt(val('prop-bathrooms'), 10);
    const neighborhood = val('prop-neighborhood').trim();

    if (!neighborhood) return alert('Please enter the neighbourhood.');
    if (!(rent > 0)) return alert('Please enter a valid monthly rent in GH₵.');
    if (!(rooms >= 1) || !(bathrooms >= 0)) return alert('Please enter valid room and bathroom counts.');

    const payload = {
      title: val('prop-title').trim() || `${val('prop-type')} in ${neighborhood}`,
      house_type: val('prop-type'),
      neighborhood,
      monthly_rent_ghs: rent,
      rooms,
      bathrooms,
      furnishing: val('prop-furnishing'),
      water: val('prop-water'),
      electricity: val('prop-electricity'),
      compound: val('prop-compound'),
      landlord_phone: val('prop-phone').trim() || (user ? user.phone : '0241234567'),
      image: val('prop-image').trim()
    };

    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) submitBtn.disabled = true;

    try {
      const res = await fetch('/api/landlord/properties', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        const result = await res.json();
        alert(`Property "${payload.title}" listed successfully with Ref ID: ${result.house_id}!`);
        window.location.href = 'my-properties.html';
        return;
      } else {
        const errorData = await res.json().catch(() => ({}));
        alert(errorData.error || 'Failed to list property. Check database connection.');
      }
    } catch (err) {
      alert('Network error while saving property to PostgreSQL.');
    } finally {
      if (submitBtn) submitBtn.disabled = false;
    }
  });
}

async function initMyPropertiesPage() {
  if (!document.getElementById('my-properties-table-body')) return;
  await renderLandlordPropertiesTable();
}

async function renderLandlordPropertiesTable() {
  const container = document.getElementById('my-properties-table-body');
  if (!container) return;

  const houses = await fetchLandlordHouses();

  if (houses.length === 0) {
    container.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:2.5rem; color:var(--text-muted);">No rental properties listed yet. <a href="add-property.html" style="font-weight:700; color:var(--primary);">Add your first property</a>.</td></tr>`;
    return;
  }

  container.innerHTML = houses.map(house => {
    const avail = isHouseAvailable(house);
    const id = escapeHTML(house.house_id);
    const displayImage = house.image || 'https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?auto=format&fit=crop&w=800&q=80';
    const title = escapeHTML(house.title || house.house_type);

    return `
    <tr data-house-id="${id}">
      <td>
        <div style="display:flex; align-items:center; gap:0.75rem;">
          <img src="${escapeHTML(displayImage)}" alt="" style="width:48px; height:48px; border-radius:var(--radius-sm); object-fit:cover;" onerror="this.src='https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?auto=format&fit=crop&w=800&q=80'" />
          <div>
            <div style="font-weight:700; color:var(--primary);">${title}</div>
            <div style="font-size:0.78rem; color:var(--text-muted);">Ref: ${id}</div>
          </div>
        </div>
      </td>
      <td>${escapeHTML(house.neighborhood)}</td>
      <td><strong>${formatGHS(house.monthly_rent_ghs)}</strong></td>
      <td>${house.rooms} R / ${house.bathrooms} B</td>
      <td><span class="badge-status-pill ${avail ? 'status-active' : 'status-inactive'}">${avail ? 'Available' : 'Unavailable'}</span></td>
      <td>
        <div style="display:flex; gap:0.4rem; flex-wrap:wrap;">
          <button onclick="toggleHouseStatus('${id}')" class="btn btn-outline btn-sm" title="Toggle active/inactive availability">
            ${avail ? 'Deactivate' : 'Activate'}
          </button>
          <button onclick="openEditPropertyModal('${id}')" class="btn btn-primary btn-sm" title="Edit property details">
            Edit
          </button>
          <button onclick="deleteLandlordProperty('${id}')" class="btn btn-sm" style="background:#EF4444; color:#FFF;" title="Delete this listing permanently">
            Delete
          </button>
        </div>
      </td>
    </tr>`;
  }).join('');
}

async function toggleHouseStatus(houseId) {
  try {
    const res = await fetch(`/api/landlord/properties/${encodeURIComponent(houseId)}/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({})
    });
    if (res.ok) {
      await renderLandlordPropertiesTable();
      const statTotal = document.getElementById('stat-total-properties');
      if (statTotal) await initLandlordDashboard();
      return;
    }
  } catch (err) {}
  alert('Failed to update listing availability status.');
}

async function deleteLandlordProperty(houseId) {
  if (!confirm(`Are you sure you want to remove listing ${houseId}? This action cannot be undone.`)) {
    return;
  }

  try {
    const res = await fetch(`/api/landlord/properties/${encodeURIComponent(houseId)}`, {
      method: 'DELETE'
    });
    if (res.ok) {
      alert(`Listing ${houseId} removed successfully.`);
      await renderLandlordPropertiesTable();
      const statTotal = document.getElementById('stat-total-properties');
      if (statTotal) await initLandlordDashboard();
      return;
    } else {
      const errorData = await res.json().catch(() => ({}));
      alert(errorData.error || 'Failed to delete listing.');
    }
  } catch (err) {
    alert('Network error while deleting listing.');
  }
}

// Edit Property Modal Support
function ensureEditPropertyModal() {
  if (document.getElementById('edit-property-modal')) return;

  const modalHtml = `
    <div id="edit-property-modal" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.6); z-index:9999; align-items:center; justify-content:center; padding:1.5rem; overflow-y:auto;">
      <div style="background:#FFF; max-width:600px; width:100%; border-radius:var(--radius-lg); padding:2rem; box-shadow:var(--shadow-lg); max-height:90vh; overflow-y:auto;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.5rem;">
          <h2 style="font-size:1.4rem; color:var(--primary); margin:0;">Edit Rental Property</h2>
          <button onclick="closeEditPropertyModal()" style="background:none; border:none; font-size:1.5rem; cursor:pointer; color:var(--text-muted);">&times;</button>
        </div>
        <form id="edit-property-form" style="display:flex; flex-direction:column; gap:1.25rem;">
          <input type="hidden" id="edit-prop-id" />
          
          <div class="form-group">
            <label for="edit-prop-title">Listing Title</label>
            <input type="text" id="edit-prop-title" class="form-control" required />
          </div>

          <div class="form-grid form-grid-two">
            <div class="form-group">
              <label for="edit-prop-type">Property Type</label>
              <select id="edit-prop-type" class="form-select" required>
                <option value="Single Room">Single Room</option>
                <option value="Chamber and Hall">Chamber & Hall</option>
                <option value="2 Bedroom">2 Bedroom House</option>
                <option value="3 Bedroom">3 Bedroom House</option>
              </select>
            </div>
            <div class="form-group">
              <label for="edit-prop-neighborhood">Tamale Neighbourhood</label>
              <input type="text" id="edit-prop-neighborhood" class="form-control" required />
            </div>
          </div>

          <div class="form-grid form-grid-three">
            <div class="form-group">
              <label for="edit-prop-rent">Monthly Rent (GH₵)</label>
              <input type="number" id="edit-prop-rent" class="form-control" required min="100" />
            </div>
            <div class="form-group">
              <label for="edit-prop-rooms">Rooms</label>
              <input type="number" id="edit-prop-rooms" class="form-control" required min="1" max="10" />
            </div>
            <div class="form-group">
              <label for="edit-prop-bathrooms">Baths</label>
              <input type="number" id="edit-prop-bathrooms" class="form-control" required min="0" max="10" />
            </div>
          </div>

          <div class="form-grid form-grid-two">
            <div class="form-group">
              <label for="edit-prop-available">Availability Status</label>
              <select id="edit-prop-available" class="form-select">
                <option value="true">Available for Rent</option>
                <option value="false">Unavailable / Occupied</option>
              </select>
            </div>
            <div class="form-group">
              <label for="edit-prop-water">Water Supply</label>
              <select id="edit-prop-water" class="form-select">
                <option value="Available">Available (Pipe / Tanker)</option>
                <option value="Not Available">Limited / Borehole</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label for="edit-prop-image">Image URL</label>
            <input type="url" id="edit-prop-image" class="form-control" placeholder="https://..." />
          </div>

          <div style="display:flex; justify-content:flex-end; gap:0.75rem; margin-top:1rem;">
            <button type="button" onclick="closeEditPropertyModal()" class="btn btn-outline">Cancel</button>
            <button type="submit" class="btn btn-primary">Save Changes</button>
          </div>
        </form>
      </div>
    </div>
  `;
  document.body.insertAdjacentHTML('beforeend', modalHtml);

  document.getElementById('edit-property-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const houseId = document.getElementById('edit-prop-id').value;
    const payload = {
      title: document.getElementById('edit-prop-title').value.trim(),
      house_type: document.getElementById('edit-prop-type').value,
      neighborhood: document.getElementById('edit-prop-neighborhood').value.trim(),
      monthly_rent_ghs: parseFloat(document.getElementById('edit-prop-rent').value),
      rooms: parseInt(document.getElementById('edit-prop-rooms').value, 10),
      bathrooms: parseInt(document.getElementById('edit-prop-bathrooms').value, 10),
      available: document.getElementById('edit-prop-available').value === 'true',
      water: document.getElementById('edit-prop-water').value,
      image: document.getElementById('edit-prop-image').value.trim()
    };

    try {
      const res = await fetch(`/api/landlord/properties/${encodeURIComponent(houseId)}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        alert('Property listing updated successfully!');
        closeEditPropertyModal();
        await renderLandlordPropertiesTable();
        const statTotal = document.getElementById('stat-total-properties');
        if (statTotal) await initLandlordDashboard();
      } else {
        const errorData = await res.json().catch(() => ({}));
        alert(errorData.error || 'Failed to update property.');
      }
    } catch (err) {
      alert('Network error while updating property.');
    }
  });
}

function openEditPropertyModal(houseId) {
  ensureEditPropertyModal();
  const house = currentLandlordProperties.find(h => h.house_id === houseId);
  if (!house) return;

  document.getElementById('edit-prop-id').value = house.house_id;
  document.getElementById('edit-prop-title').value = house.title || `${house.house_type} in ${house.neighborhood}`;
  document.getElementById('edit-prop-type').value = house.house_type;
  document.getElementById('edit-prop-neighborhood').value = house.neighborhood;
  document.getElementById('edit-prop-rent').value = house.monthly_rent_ghs;
  document.getElementById('edit-prop-rooms').value = house.rooms;
  document.getElementById('edit-prop-bathrooms').value = house.bathrooms;
  document.getElementById('edit-prop-available').value = isHouseAvailable(house) ? 'true' : 'false';
  document.getElementById('edit-prop-water').value = house.water || 'Available';
  document.getElementById('edit-prop-image').value = house.image || '';

  const modal = document.getElementById('edit-property-modal');
  if (modal) modal.style.display = 'flex';
}

function closeEditPropertyModal() {
  const modal = document.getElementById('edit-property-modal');
  if (modal) modal.style.display = 'none';
}

// Landlord Enquiries Inbox
async function initLandlordEnquiriesPage() {
  const container = document.getElementById('landlord-enquiries-list');
  if (!container) return;

  const enquiries = await fetchLandlordEnquiries();

  if (enquiries.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <svg class="empty-state-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.5 12H16c-.7 2-2.5 3.5-4.5 3.5s-3.8-1.5-4.5-3.5H2.5"/><path d="M5.5 5.1L2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.5-6.9A2 2 0 0 0 16.7 4H7.3a2 2 0 0 0-1.8 1.1z"/></svg>
        <h3>No Enquiries Received Yet</h3>
        <p>When prospective tenants send enquiries regarding your rental listings, they will appear here.</p>
      </div>`;
    return;
  }

  container.innerHTML = enquiries.map(item => `
    <div style="background:var(--secondary); padding:1.5rem; border-radius:var(--radius-md); border:1px solid var(--border-color); margin-bottom:1rem; box-shadow:var(--shadow-sm);">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
        <div>
          <h4 style="font-size:1.1rem; color:var(--primary); font-weight:700;">${escapeHTML(item.house_title || 'Rental Inquiry')}</h4>
          <span style="font-size:0.8rem; color:var(--text-muted);">From: <strong>${escapeHTML(item.tenant_name)}</strong> (${escapeHTML(item.tenant_email)})</span>
        </div>
        <span class="badge-status-pill status-pending">${escapeHTML(item.status || 'Pending')}</span>
      </div>
      <p style="background:var(--bg-light); padding:1rem; border-radius:var(--radius-sm); font-size:0.95rem; color:var(--text-main); margin:0;">"${escapeHTML(item.message)}"</p>
    </div>
  `).join('');
}

// Landlord Settings
function initLandlordSettingsPage() {
  const form = document.getElementById('landlord-settings-form');
  if (!form) return;

  const user = getCurrentUser();
  if (user) {
    const fn = document.getElementById('set-fullname');
    const em = document.getElementById('set-email');
    const ph = document.getElementById('set-phone');
    if (fn) fn.value = user.full_name || '';
    if (em) em.value = user.email || '';
    if (ph) ph.value = user.phone || '';
    const wa = document.getElementById('set-whatsapp-consent');
    const phConsent = document.getElementById('set-phone-consent');
    if (wa && typeof user.show_whatsapp === 'boolean') wa.checked = user.show_whatsapp;
    if (phConsent && typeof user.show_phone === 'boolean') phConsent.checked = user.show_phone;
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
      full_name: document.getElementById('set-fullname').value.trim(),
      phone: document.getElementById('set-phone').value.trim(),
      show_whatsapp: document.getElementById('set-whatsapp-consent') ? document.getElementById('set-whatsapp-consent').checked : true,
      show_phone: document.getElementById('set-phone-consent') ? document.getElementById('set-phone-consent').checked : true
    };

    try {
      const res = await fetch('/api/auth/profile', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        const data = await res.json();
        setCurrentUser(data.user);
        alert('Landlord profile and contact preferences updated successfully!');
      } else {
        alert('Failed to update profile settings.');
      }
    } catch (err) {
      alert('Network error while updating settings.');
    }
  });
}

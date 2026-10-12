/* ==========================================================================
   TAMALE HOUSE MARKET - LANDLORD DASHBOARD MODULE
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  if (!verifyLandlordAccess()) return;
  initLandlordDashboard();
  initAddPropertyForm();
  initMyPropertiesPage();
  initLandlordEnquiriesPage();
  initLandlordSettingsPage();
});

function verifyLandlordAccess() {
  if (!window.location.pathname.includes('/landlord/')) return true;

  const user = getCurrentUser();
  if (!user || user.role !== 'landlord') {
    alert('Access Restricted: This dashboard is reserved for registered Landlords.');
    window.location.href = '../login.html';
    return false;
  }
  return true;
}

// Only the logged-in landlord's own listings
function getLandlordHouses() {
  const user = getCurrentUser();
  if (!user) return [];
  return getHousesData().filter(h => h.owner_username === user.username);
}

function getLandlordEnquiries() {
  const ids = new Set(getLandlordHouses().map(h => h.house_id));
  return safeParse(ENQUIRIES_KEY, []).filter(e => ids.has(e.house_id));
}

function initLandlordDashboard() {
  const totalCountEl = document.getElementById('stat-total-properties');
  if (!totalCountEl) return;

  const houses = getLandlordHouses();
  const available = houses.filter(isHouseAvailable).length;

  totalCountEl.textContent = houses.length;
  const set = (id, v) => { const el = document.getElementById(id); if (el) el.textContent = v; };
  set('stat-avail-properties', available);
  set('stat-unavail-properties', houses.length - available);
  set('stat-total-enquiries', getLandlordEnquiries().length);
}

function initAddPropertyForm() {
  const form = document.getElementById('add-property-form');
  if (!form) return;

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const user = getCurrentUser();
    const val = id => (document.getElementById(id) || {}).value || '';

    const rent = parseFloat(val('prop-rent'));
    const rooms = parseInt(val('prop-rooms'), 10);
    const bathrooms = parseInt(val('prop-bathrooms'), 10);
    const neighborhood = val('prop-neighborhood').trim();

    if (!neighborhood) return alert('Please enter the neighbourhood.');
    if (!(rent > 0)) return alert('Please enter a valid monthly rent.');
    if (!(rooms >= 1) || !(bathrooms >= 0)) return alert('Please enter valid room and bathroom counts.');

    const houses = getHousesData();
    const newId = nextHouseId(houses);

    houses.unshift({
      house_id: newId,
      owner_username: user.username,
      neighborhood,
      house_type: val('prop-type'),
      rooms,
      bathrooms,
      furnishing: val('prop-furnishing'),
      distance_from_central_tamale_km: 5.0,
      electricity: val('prop-electricity'),
      water: val('prop-water'),
      compound: val('prop-compound'),
      monthly_rent_ghs: rent,
      available: true,
      image: val('prop-image').trim() || 'https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?auto=format&fit=crop&w=800&q=80',
      landlord_phone: val('prop-phone').trim() || user.phone || '0241234567'
    });
    localStorage.setItem(TAMALE_HOUSES_KEY, JSON.stringify(houses));

    alert(`Property "${val('prop-title') || val('prop-type')}" listed successfully with Ref ID: ${newId}!`);
    window.location.href = 'my-properties.html';
  });
}

function initMyPropertiesPage() {
  if (!document.getElementById('my-properties-table-body')) return;
  renderLandlordPropertiesTable();
}

function renderLandlordPropertiesTable() {
  const container = document.getElementById('my-properties-table-body');
  if (!container) return;

  const houses = getLandlordHouses();

  if (houses.length === 0) {
    container.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:2rem;">No properties listed yet. <a href="add-property.html">Add your first property</a>.</td></tr>`;
    return;
  }

  container.innerHTML = houses.map(house => {
    const avail = isHouseAvailable(house);
    const id = escapeHTML(house.house_id);
    return `
    <tr>
      <td>
        <div style="display:flex; align-items:center; gap:0.75rem;">
          <img src="${escapeHTML(house.image)}" alt="" style="width:48px; height:48px; border-radius:var(--radius-sm); object-fit:cover;" />
          <div>
            <div style="font-weight:700; color:var(--primary);">${escapeHTML(house.house_type)}</div>
            <div style="font-size:0.78rem; color:var(--text-muted);">Ref: ${id}</div>
          </div>
        </div>
      </td>
      <td>${escapeHTML(house.neighborhood)}</td>
      <td><strong>${formatGHS(house.monthly_rent_ghs)}</strong></td>
      <td>${house.rooms} R / ${house.bathrooms} B</td>
      <td><span class="badge-status-pill ${avail ? 'status-active' : 'status-inactive'}">${avail ? 'Available' : 'Unavailable'}</span></td>
      <td>
        <div style="display:flex; gap:0.5rem;">
          <button onclick="toggleHouseStatus('${id}')" class="btn btn-outline btn-sm">Toggle Status</button>
          <button onclick="deleteLandlordProperty('${id}')" class="btn btn-sm" style="background:#EF4444; color:#FFF;">Delete</button>
        </div>
      </td>
    </tr>`;
  }).join('');
}

function isOwnedByCurrentUser(house) {
  const user = getCurrentUser();
  return !!(user && house && house.owner_username === user.username);
}

function toggleHouseStatus(houseId) {
  const houses = getHousesData();
  const house = houses.find(h => h.house_id === houseId);
  if (!isOwnedByCurrentUser(house)) return;

  house.available = !isHouseAvailable(house);
  localStorage.setItem(TAMALE_HOUSES_KEY, JSON.stringify(houses));
  renderLandlordPropertiesTable();
  initLandlordDashboard();
}

function deleteLandlordProperty(houseId) {
  const houses = getHousesData();
  if (!isOwnedByCurrentUser(houses.find(h => h.house_id === houseId))) return;

  if (confirm(`Are you sure you want to remove listing ${houseId}? This action cannot be undone.`)) {
    localStorage.setItem(TAMALE_HOUSES_KEY, JSON.stringify(houses.filter(h => h.house_id !== houseId)));
    renderLandlordPropertiesTable();
    initLandlordDashboard();
  }
}

function initLandlordEnquiriesPage() {
  const container = document.getElementById('landlord-enquiries-list');
  if (!container) return;

  const enquiries = getLandlordEnquiries();

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
          <h4 style="font-size:1.1rem; color:var(--primary); font-weight:700;">${escapeHTML(item.house_title)}</h4>
          <span style="font-size:0.8rem; color:var(--text-muted);">From: ${escapeHTML(item.tenant_name)} (${escapeHTML(item.tenant_email)}) • ${escapeHTML(item.date)}</span>
        </div>
        <span class="badge-status-pill status-pending">${escapeHTML(item.status)}</span>
      </div>
      <p style="background:var(--bg-light); padding:1rem; border-radius:var(--radius-sm); font-size:0.95rem; color:var(--text-main);">"${escapeHTML(item.message)}"</p>
    </div>
  `).join('');
}

function initLandlordSettingsPage() {
  const form = document.getElementById('landlord-settings-form');
  if (!form) return;

  const user = getCurrentUser();
  if (!user) return;

  document.getElementById('set-fullname').value = user.full_name || '';
  document.getElementById('set-email').value = user.email || '';
  document.getElementById('set-phone').value = user.phone || '';
  const wa = document.getElementById('set-whatsapp-consent');
  const ph = document.getElementById('set-phone-consent');
  if (wa && typeof user.show_whatsapp === 'boolean') wa.checked = user.show_whatsapp;
  if (ph && typeof user.show_phone === 'boolean') ph.checked = user.show_phone;

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    setCurrentUser({
      ...getCurrentUser(),
      full_name: document.getElementById('set-fullname').value.trim(),
      email: document.getElementById('set-email').value.trim(),
      phone: document.getElementById('set-phone').value.trim(),
      show_whatsapp: wa ? wa.checked : true,
      show_phone: ph ? ph.checked : true
    });
    alert('Landlord profile and contact preferences updated successfully!');
  });
}

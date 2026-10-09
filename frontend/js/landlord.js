/* ==========================================================================
   TAMALE HOUSE MARKET - LANDLORD DASHBOARD MODULE
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  verifyLandlordAccess();
  initLandlordDashboard();
  initAddPropertyForm();
  initMyPropertiesPage();
  initLandlordEnquiriesPage();
  initLandlordSettingsPage();
});

function verifyLandlordAccess() {
  const isLandlordPage = window.location.pathname.includes('/landlord/');
  if (!isLandlordPage) return;

  const user = getCurrentUser();
  if (!user || user.role !== 'landlord') {
    // If unauthenticated or tenant tries to enter, redirect to login
    alert('Access Restricted: This dashboard is reserved for registered Landlords.');
    window.location.href = '../login.html';
  }
}

// Overview Stats Calculator
function initLandlordDashboard() {
  const totalCountEl = document.getElementById('stat-total-properties');
  const availCountEl = document.getElementById('stat-avail-properties');
  const unavailCountEl = document.getElementById('stat-unavail-properties');
  const enquiryCountEl = document.getElementById('stat-total-enquiries');

  if (!totalCountEl) return;

  const houses = getHousesData();
  const enquiriesStr = localStorage.getItem(ENQUIRIES_KEY);
  const enquiries = enquiriesStr ? JSON.parse(enquiriesStr) : [];

  const available = houses.filter(h => h.water === 'Available').length;
  const unavailable = houses.length - available;

  totalCountEl.textContent = houses.length;
  availCountEl.textContent = available;
  unavailCountEl.textContent = unavailable;
  enquiryCountEl.textContent = enquiries.length;
}

// Add Property Form Handler
function initAddPropertyForm() {
  const form = document.getElementById('add-property-form');
  if (!form) return;

  form.addEventListener('submit', (e) => {
    e.preventDefault();

    const title = document.getElementById('prop-title').value;
    const houseType = document.getElementById('prop-type').value;
    const neighborhood = document.getElementById('prop-neighborhood').value;
    const rent = document.getElementById('prop-rent').value;
    const rooms = document.getElementById('prop-rooms').value;
    const bathrooms = document.getElementById('prop-bathrooms').value;
    const furnishing = document.getElementById('prop-furnishing').value;
    const electricity = document.getElementById('prop-electricity').value;
    const water = document.getElementById('prop-water').value;
    const compound = document.getElementById('prop-compound').value;
    const phone = document.getElementById('prop-phone').value || '0241234567';
    const imageUrl = document.getElementById('prop-image').value || 'https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?auto=format&fit=crop&w=800&q=80';

    const houses = getHousesData();
    const newId = `TAM-${String(houses.length + 1).padStart(3, '0')}`;

    const newHouse = {
      house_id: newId,
      neighborhood: neighborhood,
      house_type: houseType,
      rooms: parseInt(rooms),
      bathrooms: parseInt(bathrooms),
      furnishing: furnishing,
      distance_from_central_tamale_km: 5.0,
      electricity: electricity,
      water: water,
      compound: compound,
      monthly_rent_ghs: parseFloat(rent),
      image: imageUrl,
      landlord_phone: phone
    };

    houses.unshift(newHouse);
    localStorage.setItem(TAMALE_HOUSES_KEY, JSON.stringify(houses));

    alert(`Property "${title || houseType}" listed successfully with Ref ID: ${newId}!`);
    window.location.href = 'my-properties.html';
  });
}

// My Properties Manager Page
function initMyPropertiesPage() {
  const container = document.getElementById('my-properties-table-body');
  if (!container) return;

  renderLandlordPropertiesTable();
}

function renderLandlordPropertiesTable() {
  const container = document.getElementById('my-properties-table-body');
  if (!container) return;

  const houses = getHousesData();

  if (houses.length === 0) {
    container.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:2rem;">No properties listed yet. <a href="add-property.html">Add your first property</a>.</td></tr>`;
    return;
  }

  container.innerHTML = houses.map(house => `
    <tr>
      <td>
        <div style="display:flex; align-items:center; gap:0.75rem;">
          <img src="${house.image}" alt="" style="width:48px; height:48px; border-radius:var(--radius-sm); object-fit:cover;" />
          <div>
            <div style="font-weight:700; color:var(--primary);">${house.house_type}</div>
            <div style="font-size:0.78rem; color:var(--text-muted);">Ref: ${house.house_id}</div>
          </div>
        </div>
      </td>
      <td>${house.neighborhood}</td>
      <td><strong>${formatGHS(house.monthly_rent_ghs)}</strong></td>
      <td>${house.rooms} R / ${house.bathrooms} B</td>
      <td>
        <span class="badge-status-pill ${house.water === 'Available' ? 'status-active' : 'status-inactive'}">
          ${house.water === 'Available' ? 'Available' : 'Unavailable'}
        </span>
      </td>
      <td>
        <div style="display:flex; gap:0.5rem;">
          <button onclick="toggleHouseStatus('${house.house_id}')" class="btn btn-outline btn-sm">Toggle Status</button>
          <button onclick="deleteLandlordProperty('${house.house_id}')" class="btn btn-sm" style="background:#EF4444; color:#FFF;">Delete</button>
        </div>
      </td>
    </tr>
  `).join('');
}

function toggleHouseStatus(houseId) {
  const houses = getHousesData();
  const house = houses.find(h => h.house_id === houseId);
  if (house) {
    house.water = house.water === 'Available' ? 'Not Available' : 'Available';
    localStorage.setItem(TAMALE_HOUSES_KEY, JSON.stringify(houses));
    renderLandlordPropertiesTable();
    initLandlordDashboard();
  }
}

function deleteLandlordProperty(houseId) {
  if (confirm(`Are you sure you want to remove listing ${houseId}? This action cannot be undone.`)) {
    let houses = getHousesData();
    houses = houses.filter(h => h.house_id !== houseId);
    localStorage.setItem(TAMALE_HOUSES_KEY, JSON.stringify(houses));
    renderLandlordPropertiesTable();
    initLandlordDashboard();
  }
}

// Landlord Enquiries Manager
function initLandlordEnquiriesPage() {
  const container = document.getElementById('landlord-enquiries-list');
  if (!container) return;

  const enquiriesStr = localStorage.getItem(ENQUIRIES_KEY);
  const enquiries = enquiriesStr ? JSON.parse(enquiriesStr) : [];

  if (enquiries.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <svg class="empty-state-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.5 12H16c-.7 2-2.5 3.5-4.5 3.5s-3.8-1.5-4.5-3.5H2.5"/><path d="M5.5 5.1L2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.5-6.9A2 2 0 0 0 16.7 4H7.3a2 2 0 0 0-1.8 1.1z"/></svg>
        <h3>No Enquiries Received Yet</h3>
        <p>When prospective tenants send enquiries regarding your rental listings, they will appear here.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = enquiries.map(item => `
    <div style="background:var(--secondary); padding:1.5rem; border-radius:var(--radius-md); border:1px solid var(--border-color); margin-bottom:1rem; box-shadow:var(--shadow-sm);">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
        <div>
          <h4 style="font-size:1.1rem; color:var(--primary); font-weight:700;">${item.house_title}</h4>
          <span style="font-size:0.8rem; color:var(--text-muted);">From: ${item.tenant_name} (${item.tenant_email}) • ${item.date}</span>
        </div>
        <span class="badge-status-pill status-pending">${item.status}</span>
      </div>
      <p style="background:var(--bg-light); padding:1rem; border-radius:var(--radius-sm); font-size:0.95rem; color:var(--text-main);">
        "${item.message}"
      </p>
    </div>
  `).join('');
}

// Landlord Settings Page
function initLandlordSettingsPage() {
  const form = document.getElementById('landlord-settings-form');
  if (!form) return;

  const user = getCurrentUser();
  if (user) {
    document.getElementById('set-fullname').value = user.full_name || '';
    document.getElementById('set-email').value = user.email || '';
    document.getElementById('set-phone').value = user.phone || '0241234567';
  }

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const updatedUser = {
      ...user,
      full_name: document.getElementById('set-fullname').value,
      email: document.getElementById('set-email').value,
      phone: document.getElementById('set-phone').value,
      show_whatsapp: document.getElementById('set-whatsapp-consent').checked,
      show_phone: document.getElementById('set-phone-consent').checked
    };
    setCurrentUser(updatedUser);
    alert('Landlord profile and contact preferences updated successfully!');
  });
}

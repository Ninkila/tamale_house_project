/* ==========================================================================
   TAMALE HOUSE MARKET - PROPERTY DETAILS MODULE
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  if (window.location.pathname.includes('property.html')) {
    initPropertyDetailsPage();
  }
});

function initPropertyDetailsPage() {
  const urlParams = new URLSearchParams(window.location.search);
  const houseId = urlParams.get('id') || 'TAM-001';

  const houses = getHousesData();
  const house = houses.find(h => h.house_id === houseId);

  if (!house) {
    const c = document.getElementById('property-details-container');
    if (c) c.innerHTML = `<div class="empty-state"><h3>Listing Not Found</h3><p>This property may have been removed.</p><a href="houses.html" class="btn btn-primary">Browse Houses</a></div>`;
    return;
  }

  renderPropertyDetails(house);
  initEnquiryModal(house);
}

function renderPropertyDetails(house) {
  const container = document.getElementById('property-details-container');
  if (!container) return;

  const waUrl = generateWhatsAppLink(house.landlord_phone, `${house.house_type} in ${house.neighborhood}`, house.house_id);
  const telUrl = generatePhoneLink(house.landlord_phone);
  const isSaved = isFavourite(house.house_id);

  container.innerHTML = `
    <div class="property-detail-header" style="margin-bottom: 2rem;">
      <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:1rem;">
        <div>
          <h1 style="font-size: 2.2rem; font-weight: 800; color: var(--primary);">${escapeHTML(house.house_type)} in ${escapeHTML(house.neighborhood)}</h1>
          <p style="color: var(--text-muted); font-size: 1.05rem; display:flex; align-items:center; gap:0.5rem; margin-top:0.35rem;">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>
            ${escapeHTML(house.neighborhood)}, Tamale • ${house.distance_from_central_tamale_km} km from Central Tamale
          </p>
        </div>
        <div style="text-align: right;">
          <div style="font-size: 2.2rem; font-weight: 800; color: var(--primary);">${formatGHS(house.monthly_rent_ghs)} <span style="font-size:1rem; color:var(--text-muted); font-weight:500;">/ month</span></div>
          <span class="badge-status-pill status-active" style="margin-top:0.35rem;">Verified Rental Listing</span>
        </div>
      </div>
    </div>

    <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 2.5rem; margin-bottom: 3rem;">
      <div>
        <div style="border-radius: var(--radius-lg); overflow: hidden; height: 420px; background:#e2e8f0; margin-bottom: 1.5rem; box-shadow: var(--shadow-md);">
          <img src="${escapeHTML(house.image)}" alt="${escapeHTML(house.house_type)}" style="width:100%; height:100%; object-fit:cover;" />
        </div>

        <div style="background-color: var(--secondary); padding: 2rem; border-radius: var(--radius-lg); border:1px solid var(--border-color); box-shadow: var(--shadow-sm); margin-bottom: 2rem;">
          <h2 style="font-size: 1.4rem; color: var(--primary); margin-bottom: 1rem;">Property Overview</h2>
          <p style="color: var(--text-main); line-height: 1.7; margin-bottom: 1.5rem;">
            A beautiful, well-maintained ${escapeHTML(house.house_type.toLowerCase())} located in the serene neighbourhood of ${escapeHTML(house.neighborhood)}, Tamale. Ideal for working professionals or small families seeking comfort, accessibility, and peace of mind.
          </p>

          <h3 style="font-size: 1.15rem; color: var(--primary); margin-bottom: 1rem;">Key Specifications</h3>
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; background-color: var(--bg-light); padding: 1.25rem; border-radius: var(--radius-md);">
            <div><strong>Rooms:</strong> ${house.rooms} Bedrooms/Rooms</div>
            <div><strong>Bathrooms:</strong> ${house.bathrooms} Baths</div>
            <div><strong>Furnishing:</strong> ${escapeHTML(house.furnishing)}</div>
            <div><strong>Water Supply:</strong> ${escapeHTML(house.water)}</div>
            <div><strong>Electricity:</strong> ${escapeHTML(house.electricity)}</div>
            <div><strong>Walled Compound:</strong> ${escapeHTML(house.compound)}</div>
          </div>
        </div>
      </div>

      <!-- Landlord Contact Sidebar -->
      <div>
        <div style="background-color: var(--secondary); padding: 2rem; border-radius: var(--radius-lg); border:1px solid var(--border-color); box-shadow: var(--shadow-md); position: sticky; top: 100px;">
          <h3 style="font-size: 1.25rem; color: var(--primary); margin-bottom: 1.25rem;">Contact Landlord</h3>
          
          <div style="display:flex; align-items:center; gap:1rem; margin-bottom:1.5rem; padding-bottom:1.25rem; border-bottom:1px solid var(--border-color);">
            <div style="width:52px; height:52px; border-radius:var(--radius-full); background-color:var(--primary); color:var(--accent); display:flex; align-items:center; justify-content:center; font-weight:800; font-size:1.25rem;">
              LM
            </div>
            <div>
              <div style="font-weight:700; color:var(--primary); font-size:1.05rem;">Landlord Representative</div>
              <div style="font-size:0.85rem; color:var(--text-muted);">Tamale House Market Verified</div>
            </div>
          </div>

          <div style="display:flex; flex-direction:column; gap:1rem;">
            <a href="${waUrl}" target="_blank" rel="noopener" onclick="return handleContactClick(event)" class="btn btn-whatsapp btn-lg btn-full">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946.003-6.556 5.338-11.891 11.893-11.891 3.181.001 6.167 1.24 8.413 3.488 2.245 2.248 3.481 5.236 3.48 8.414-.003 6.557-5.338 11.892-11.893 11.892-1.99-.001-3.951-.5-5.688-1.448l-6.305 1.654z"/></svg>
              Chat on WhatsApp
            </a>

            <a href="${telUrl}" onclick="return handleContactClick(event)" class="btn btn-phone btn-lg btn-full">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
              Call Landlord Directly
            </a>

            <button onclick="handleEnquiryBtnClick(event)" class="btn btn-outline btn-full">
              Send Direct Enquiry
            </button>

            <button onclick="handleFavClick(event, '${house.house_id}')" class="btn btn-outline btn-full" style="margin-top:0.5rem;">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="${isSaved ? '#EF4444' : 'none'}" stroke="${isSaved ? '#EF4444' : 'currentColor'}" stroke-width="2"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/></svg>
              ${isSaved ? 'Saved to Favourites' : 'Save Property'}
            </button>
          </div>
        </div>
      </div>
    </div>
  `;
}

function handleEnquiryBtnClick(e) {
  if (e) e.preventDefault();
  const user = getCurrentUser();
  if (!user) {
    alert('Account Required: You must create an account or log in to send enquiries to landlords.');
    window.location.href = 'login.html';
    return;
  }
  const nameEl = document.getElementById('enquiry-name');
  const emailEl = document.getElementById('enquiry-email');
  if (nameEl && !nameEl.value) nameEl.value = user.full_name || '';
  if (emailEl && !emailEl.value) emailEl.value = user.email || '';
  openEnquiryModal();
}

function initEnquiryModal(house) {
  const modal = document.getElementById('enquiry-modal');
  if (!modal) return;

  const form = document.getElementById('enquiry-form');
  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const user = getCurrentUser();
      if (!user) {
        alert('Account Required: You must create an account or log in to send enquiries to landlords.');
        window.location.href = 'login.html';
        return;
      }
      const name = document.getElementById('enquiry-name').value;
      const email = document.getElementById('enquiry-email').value;
      const message = document.getElementById('enquiry-message').value;

      const newEnquiry = {
        id: 'ENQ-' + Date.now(),
        house_id: house.house_id,
        house_title: `${house.house_type} in ${house.neighborhood}`,
        tenant_name: name,
        tenant_email: email,
        tenant_username: user.username,
        message: message,
        date: new Date().toLocaleDateString(),
        status: 'Pending'
      };

      const list = safeParse(ENQUIRIES_KEY, []);
      list.push(newEnquiry);
      localStorage.setItem(ENQUIRIES_KEY, JSON.stringify(list));

      alert('Enquiry submitted successfully! Landlord will review your request.');
      closeEnquiryModal();
      form.reset();
    });
  }
}

function openEnquiryModal() {
  const modal = document.getElementById('enquiry-modal');
  if (modal) modal.style.display = 'flex';
}

function closeEnquiryModal() {
  const modal = document.getElementById('enquiry-modal');
  if (modal) modal.style.display = 'none';
}

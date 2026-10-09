/* ==========================================================================
   TAMALE HOUSE MARKET - HOUSES SEARCH & RENDER MODULE
   ========================================================================== */

// Default Dataset based on tamale_house_rentals.csv
const SEED_HOUSES = [
  { house_id: "TAM-001", neighborhood: "Tishegu", house_type: "2 Bedroom", rooms: 3, bathrooms: 2, furnishing: "Unfurnished", distance_from_central_tamale_km: 11.9, electricity: "Prepaid", water: "Available", compound: "Yes", monthly_rent_ghs: 1150, image: "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?auto=format&fit=crop&w=800&q=80", landlord_phone: "0241234567" },
  { house_id: "TAM-002", neighborhood: "Nyohini", house_type: "2 Bedroom", rooms: 3, bathrooms: 2, furnishing: "Unfurnished", distance_from_central_tamale_km: 11.1, electricity: "Prepaid", water: "Available", compound: "Yes", monthly_rent_ghs: 1400, image: "https://images.unsplash.com/photo-1570129477492-45c003edd2be?auto=format&fit=crop&w=800&q=80", landlord_phone: "0242345678" },
  { house_id: "TAM-003", neighborhood: "Fuo", house_type: "Chamber and Hall", rooms: 2, bathrooms: 2, furnishing: "Unfurnished", distance_from_central_tamale_km: 5.1, electricity: "Prepaid", water: "Available", compound: "No", monthly_rent_ghs: 800, image: "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&q=80", landlord_phone: "0243456789" },
  { house_id: "TAM-004", neighborhood: "Vittin", house_type: "Chamber and Hall", rooms: 2, bathrooms: 1, furnishing: "Furnished", distance_from_central_tamale_km: 7.5, electricity: "Prepaid", water: "Available", compound: "Yes", monthly_rent_ghs: 1300, image: "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=800&q=80", landlord_phone: "0244567890" },
  { house_id: "TAM-005", neighborhood: "Dungu", house_type: "3 Bedroom", rooms: 4, bathrooms: 3, furnishing: "Unfurnished", distance_from_central_tamale_km: 6.4, electricity: "Prepaid", water: "Available", compound: "Yes", monthly_rent_ghs: 1700, image: "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=800&q=80", landlord_phone: "0245678901" },
  { house_id: "TAM-006", neighborhood: "Vittin", house_type: "3 Bedroom", rooms: 4, bathrooms: 3, furnishing: "Unfurnished", distance_from_central_tamale_km: 10.3, electricity: "Prepaid", water: "Available", compound: "Yes", monthly_rent_ghs: 1950, image: "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?auto=format&fit=crop&w=800&q=80", landlord_phone: "0246789012" },
  { house_id: "TAM-007", neighborhood: "Jisonayili", house_type: "2 Bedroom", rooms: 3, bathrooms: 2, furnishing: "Furnished", distance_from_central_tamale_km: 13.5, electricity: "Postpaid", water: "Available", compound: "Yes", monthly_rent_ghs: 1650, image: "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=800&q=80", landlord_phone: "0247890123" },
  { house_id: "TAM-008", neighborhood: "Kanvilli", house_type: "Chamber and Hall", rooms: 2, bathrooms: 1, furnishing: "Unfurnished", distance_from_central_tamale_km: 12.6, electricity: "Postpaid", water: "Available", compound: "Yes", monthly_rent_ghs: 750, image: "https://images.unsplash.com/photo-1613977257363-707ba9348227?auto=format&fit=crop&w=800&q=80", landlord_phone: "0248901234" },
  { house_id: "TAM-009", neighborhood: "Lamashegu", house_type: "Single Room", rooms: 1, bathrooms: 1, furnishing: "Unfurnished", distance_from_central_tamale_km: 6.5, electricity: "Postpaid", water: "Available", compound: "Yes", monthly_rent_ghs: 550, image: "https://images.unsplash.com/photo-1598228723793-52759bba239c?auto=format&fit=crop&w=800&q=80", landlord_phone: "0249012345" },
  { house_id: "TAM-010", neighborhood: "Tishegu", house_type: "2 Bedroom", rooms: 3, bathrooms: 3, furnishing: "Unfurnished", distance_from_central_tamale_km: 2.3, electricity: "Prepaid", water: "Available", compound: "Yes", monthly_rent_ghs: 1250, image: "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?auto=format&fit=crop&w=800&q=80", landlord_phone: "0240123456" },
  { house_id: "TAM-011", neighborhood: "Nyohini", house_type: "Chamber and Hall", rooms: 2, bathrooms: 2, furnishing: "Unfurnished", distance_from_central_tamale_km: 6.4, electricity: "Postpaid", water: "Available", compound: "Yes", monthly_rent_ghs: 1000, image: "https://images.unsplash.com/photo-1605276374104-dee2a0ed3cd6?auto=format&fit=crop&w=800&q=80", landlord_phone: "0241122334" },
  { house_id: "TAM-012", neighborhood: "Education Ridge", house_type: "2 Bedroom", rooms: 3, bathrooms: 3, furnishing: "Unfurnished", distance_from_central_tamale_km: 7.2, electricity: "Prepaid", water: "Available", compound: "Yes", monthly_rent_ghs: 1700, image: "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80", landlord_phone: "0242233445" }
];

function getHousesData() {
  const stored = localStorage.getItem(TAMALE_HOUSES_KEY);
  if (stored) {
    try { return JSON.parse(stored); } catch (e) {}
  }
  localStorage.setItem(TAMALE_HOUSES_KEY, JSON.stringify(SEED_HOUSES));
  return SEED_HOUSES;
}

// Render House Card HTML
function renderHouseCard(house) {
  const isSaved = isFavourite(house.house_id);
  const heartColor = isSaved ? '#EF4444' : 'none';
  const heartStroke = isSaved ? '#EF4444' : '#64748B';
  const waUrl = generateWhatsAppLink(house.landlord_phone, `${house.house_type} in ${house.neighborhood}`, house.house_id);

  return `
    <div class="property-card" data-id="${house.house_id}">
      <div class="property-img-wrapper">
        <img src="${house.image}" alt="${house.house_type} in ${house.neighborhood}" class="property-img" loading="lazy" />
        <span class="property-badge badge-rent">${house.house_type}</span>
        <span class="badge-status" style="color: ${house.water === 'Available' ? '#065F46' : '#991B1B'}">
          ${house.water === 'Available' ? '● Water Available' : '○ Water Limited'}
        </span>
      </div>
      <div class="property-content">
        <div class="property-price">
          ${formatGHS(house.monthly_rent_ghs)} <span class="period">/ month</span>
        </div>
        <h3 class="property-title">
          <a href="property.html?id=${house.house_id}">${house.house_type} in ${house.neighborhood}</a>
        </h3>
        <div class="property-location">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>
          ${house.neighborhood}, Tamale (${house.distance_from_central_tamale_km} km from town)
        </div>
        
        <div class="property-features">
          <div class="feature-item" title="Rooms">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 4v16"/><path d="M2 8h18a2 2 0 0 1 2 2v10"/><path d="M2 17h20"/><path d="M6 8v9"/></svg>
            ${house.rooms} Rooms
          </div>
          <div class="feature-item" title="Bathrooms">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 6 6.5 3.5a1.5 1.5 0 0 0-2.12 0 1.5 1.5 0 0 0 0 2.12L6.88 8"/><path d="M4 12h16a1 1 0 0 1 1 1v3a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4v-3a1 1 0 0 1 1-1Z"/></svg>
            ${house.bathrooms} Baths
          </div>
          <div class="feature-item" title="Furnishing">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18"/></svg>
            ${house.furnishing}
          </div>
        </div>

        <div class="property-actions">
          <a href="property.html?id=${house.house_id}" class="btn btn-primary btn-sm" style="flex:1;">View Details</a>
          <a href="${waUrl}" target="_blank" rel="noopener" onclick="return handleContactClick(event)" class="btn btn-whatsapp btn-sm" title="Contact Landlord on WhatsApp">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946.003-6.556 5.338-11.891 11.893-11.891 3.181.001 6.167 1.24 8.413 3.488 2.245 2.248 3.481 5.236 3.48 8.414-.003 6.557-5.338 11.892-11.893 11.892-1.99-.001-3.951-.5-5.688-1.448l-6.305 1.654z"/></svg>
            Chat
          </a>
          <button onclick="handleFavClick(event, '${house.house_id}')" class="btn btn-outline btn-sm" title="Save to Favourites" style="padding: 0.4rem 0.6rem;">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="${heartColor}" stroke="${heartStroke}" stroke-width="2"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/></svg>
          </button>
        </div>
      </div>
    </div>
  `;
}

function handleFavClick(e, houseId) {
  e.preventDefault();
  e.stopPropagation();
  const added = toggleFavourite(houseId);
  const btn = e.currentTarget;
  const svg = btn.querySelector('svg');
  if (added) {
    svg.setAttribute('fill', '#EF4444');
    svg.setAttribute('stroke', '#EF4444');
  } else {
    svg.setAttribute('fill', 'none');
    svg.setAttribute('stroke', '#64748B');
  }
}

// Filter engine
function filterHouses(houses, criteria) {
  return houses.filter(house => {
    if (criteria.neighborhood && criteria.neighborhood.trim() !== '') {
      if (!house.neighborhood.toLowerCase().includes(criteria.neighborhood.toLowerCase().trim())) {
        return false;
      }
    }
    if (criteria.minRent && Number(house.monthly_rent_ghs) < Number(criteria.minRent)) {
      return false;
    }
    if (criteria.maxRent && Number(house.monthly_rent_ghs) > Number(criteria.maxRent)) {
      return false;
    }
    if (criteria.rooms && Number(house.rooms) < Number(criteria.rooms)) {
      return false;
    }
    if (criteria.bathrooms && Number(house.bathrooms) < Number(criteria.bathrooms)) {
      return false;
    }
    if (criteria.houseType && criteria.houseType !== 'Any' && house.house_type !== criteria.houseType) {
      return false;
    }
    return true;
  });
}

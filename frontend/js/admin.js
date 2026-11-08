document.addEventListener('DOMContentLoaded', async () => {
  const user = await syncCurrentUserWithServer();
  if (!user || user.role !== 'admin') {
    window.location.href = '../login.html';
    return;
  }

  const name = document.getElementById('admin-name');
  if (name) name.textContent = user.full_name || user.username;
  document.getElementById('refresh-analytics')?.addEventListener('click', loadAnalytics);
  await loadAnalytics();
});

async function loadAnalytics() {
  const refresh = document.getElementById('refresh-analytics');
  if (refresh) {
    refresh.disabled = true;
    refresh.textContent = 'Refreshing…';
  }

  try {
    const response = await fetch('/api/admin/analytics');
    if (!response.ok) throw new Error('Analytics request failed');
    renderAnalytics(await response.json());
  } catch (error) {
    const chart = document.getElementById('traffic-chart');
    if (chart) chart.innerHTML = '<p class="empty-analytics">Analytics are unavailable. Refresh to try again.</p>';
  } finally {
    if (refresh) {
      refresh.disabled = false;
      refresh.textContent = 'Refresh data';
    }
  }
}

function renderAnalytics(data) {
  const summary = data.summary || {};
  setMetric('metric-page-views', summary.page_views_30d);
  setMetric('metric-visitors', summary.unique_visitors_30d);
  setMetric('metric-listings', summary.active_listings);
  setMetric('metric-enquiries', summary.enquiries_30d);
  const today = document.getElementById('metric-today');
  if (today) today.textContent = `Today: ${formatNumber(summary.page_views_today)}`;

  renderTrafficChart(data.daily || []);
  renderRoles(data.roles || []);
  renderTopPages(data.top_pages || []);
  renderRecentUsers(data.recent_users || []);
}

function setMetric(id, value) {
  const element = document.getElementById(id);
  if (element) element.textContent = formatNumber(value);
}

function formatNumber(value) {
  return Number(value || 0).toLocaleString('en-GH');
}

function renderTrafficChart(days) {
  const chart = document.getElementById('traffic-chart');
  if (!chart) return;
  const max = Math.max(1, ...days.map(day => Number(day.views || 0)));
  chart.innerHTML = days.map(day => {
    const views = Number(day.views || 0);
    const height = Math.max(6, Math.round((views / max) * 100));
    return `<div class="chart-column" title="${escapeHTML(day.label)}: ${views} page views"><span class="chart-value">${views || ''}</span><div class="chart-bar" style="height:${height}%"></div><span class="chart-label">${escapeHTML(day.label)}</span></div>`;
  }).join('') || '<p class="empty-analytics">No traffic has been recorded yet.</p>';
}

function renderRoles(roles) {
  const list = document.getElementById('role-list');
  if (!list) return;
  const total = roles.reduce((sum, role) => sum + Number(role.count || 0), 0) || 1;
  list.innerHTML = roles.map(role => {
    const count = Number(role.count || 0);
    const width = Math.round((count / total) * 100);
    return `<div class="role-row"><div class="role-row-head"><span>${escapeHTML(role.role)}</span><strong>${count}</strong></div><div class="role-track"><span style="width:${width}%"></span></div></div>`;
  }).join('') || '<p class="empty-analytics">No accounts yet.</p>';
}

function renderTopPages(pages) {
  const list = document.getElementById('top-pages-list');
  if (!list) return;
  list.innerHTML = pages.map((page, index) => `<div class="top-page"><span class="page-rank">${index + 1}</span><span class="page-path">${escapeHTML(page.page_path)}</span><strong>${formatNumber(page.views)}</strong></div>`).join('') || '<p class="empty-analytics">No traffic has been recorded yet.</p>';
}

function renderRecentUsers(users) {
  const body = document.getElementById('recent-users');
  if (!body) return;
  body.innerHTML = users.map(user => `<tr><td><strong>${escapeHTML(user.full_name || user.username)}</strong><br><small>${escapeHTML(user.email)}</small></td><td><span class="badge-status-pill status-active">${escapeHTML(user.role)}</span></td><td>${new Date(user.created_at).toLocaleDateString('en-GH', { day: 'numeric', month: 'short' })}</td></tr>`).join('') || '<tr><td colspan="3" class="empty-analytics">No accounts yet.</td></tr>';
}

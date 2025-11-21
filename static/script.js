/**
 * script.js
 *
 * Frontend logic for the dashboard.
 * - Loads ticket data via /tickets/{user_id}
 * - Displays stats: total, new, updated
 * - Supports filtering by step, ID, date/time
 * - Auto-refreshes every 10 seconds
 * - Shows toast notifications
 */

// Initialize user_id from localStorage or generate new one
let userId = localStorage.getItem('user_id');
if (!userId) {
  userId = 'usr_' + Math.random().toString(36).substr(2, 9);
  localStorage.setItem('user_id', userId);
}
window.USER_ID = userId;

// Auto-refresh interval: 10 seconds
const AUTO_REFRESH_INTERVAL = 10000;

// Track previous counts to detect changes
let lastNewCount = 0;
let lastUpdatedCount = 0;

// Wait for DOM to load
document.addEventListener('DOMContentLoaded', () => {
  // Set webhook URL in UI
  const webhookUrl = `${window.location.origin}/webhook/${userId}`;
  document.getElementById('webhook-url').textContent = webhookUrl;

  // Start loading data
  refreshDashboard();
  setInterval(refreshDashboard, AUTO_REFRESH_INTERVAL);

  // Set up event listeners
  document.getElementById('apply-filters').addEventListener('click', refreshDashboard);
  document.getElementById('clear-filters').addEventListener('click', resetFilters);
  document.getElementById('clear-data').addEventListener('click', clearAllData);
});

function resetFilters() {
  document.getElementById('filter-step').value = '';
  document.getElementById('filter-ticket-id').value = '';
  document.getElementById('filter-date-from-date').value = '';
  document.getElementById('filter-date-from-time').value = '';
  document.getElementById('filter-date-to-date').value = '';
  document.getElementById('filter-date-to-time').value = '';
  refreshDashboard();
}

function clearAllData() {
  if (confirm("Are you sure you want to delete ALL your ticket data?")) {
    fetch(`/clear/${window.USER_ID}`, { method: 'POST' })
      .then(() => {
        showNotification("All data cleared.");
        refreshDashboard();
      })
      .catch(err => console.error("Clear failed:", err));
  }
}

function refreshDashboard() {
  const fetchTime = Date.now();

  fetch(`/tickets/${window.USER_ID}`)
    .then(res => {
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return res.json();
    })
    .then(data => {
      const container = document.getElementById('tickets-container');
      if (!container) return;

      // Count metrics
      const total = Object.keys(data).length;
      let newCount = 0;
      let updatedCount = 0;

      for (const ticket of Object.values(data)) {
        const changes = ticket.changes || {};
        if (changes.first_received) {
          newCount++;
        } else if (Object.keys(changes).length > 0) {
          updatedCount++;
        }
      }

      // Show notifications
      if (newCount > lastNewCount && lastNewCount >= 0) {
        showNotification(`📥 New ticket received (${newCount} total)`);
      }
      if (updatedCount > lastUpdatedCount && lastUpdatedCount >= 0) {
        showNotification(`🔄 Ticket updated (${updatedCount} total)`);
      }

      lastNewCount = newCount;
      lastUpdatedCount = updatedCount;

      // Update stats
      document.getElementById('total-count').textContent = total;
      document.getElementById('new-count').textContent = newCount;
      document.getElementById('updated-count').textContent = updatedCount;

      // Update last updated time
      const now = new Date();
      const minsAgo = Math.floor((now - fetchTime) / 60000);
      document.getElementById('last-updated').textContent =
        `Last updated: ${minsAgo === 0 ? 'just now' : `${minsAgo} ${minsAgo === 1 ? 'minute' : 'minutes'} ago`}`;

      // Render tickets
      renderTickets(container, data);
    })
    .catch(err => {
      console.error("Fetch error:", err);
      container.innerHTML = `<p style="color:red;">Failed to load data.</p>`;
    });
}

function renderTickets(container, data) {
  // Convert to array and sort by most recent
  const tickets = Object.entries(data)
    .map(([id, t]) => ({ id, ...t }))
    .sort((a, b) => new Date(b.received_at) - new Date(a.received_at));

  // Get filter values
  const stepFilter = document.getElementById('filter-step').value.toLowerCase();
  const idFilter = document.getElementById('filter-ticket-id').value.trim().toLowerCase();

  const fromDateStr = document.getElementById('filter-date-from-date').value;
  const fromTimeStr = document.getElementById('filter-date-from-time').value || '00:00';
  const toDateStr = document.getElementById('filter-date-to-date').value;
  const toTimeStr = document.getElementById('filter-date-to-time').value || '23:59';

  const dateFrom = fromDateStr ? new Date(`${fromDateStr}T${fromTimeStr}`) : null;
  const dateTo = toDateStr ? new Date(`${toDateStr}T${toTimeStr}`) : null;

  // Apply filters
  const filtered = tickets.filter(ticket => {
    if (stepFilter && (ticket.step || '').toLowerCase() !== stepFilter) return false;
    if (idFilter && !String(ticket.id || ticket.ticket_id).toLowerCase().includes(idFilter)) return false;
    const received = new Date(ticket.received_at);
    if (dateFrom && received < dateFrom) return false;
    if (dateTo && received > dateTo) return false;
    return true;
  });

  if (filtered.length === 0) {
    container.innerHTML = '<p class="empty">No tickets match the filters.</p>';
    return;
  }

  let html = '';
  for (const ticket of filtered) {
    const changes = ticket.changes || {};
    const cardClass = changes.first_received
      ? 'ticket new-ticket'
      : Object.keys(changes).length > 0
        ? 'ticket updated-ticket flash'
        : 'ticket';

    const step = ticket.step
      ? `<span class="status step-${ticket.step.toLowerCase()}">${ticket.step}</span>`
      : '';

    const received = new Date(ticket.received_at).toLocaleString();

    let tagsHtml = '';
    if (Array.isArray(ticket.tags) && ticket.tags.length > 0) {
      tagsHtml = '<p><strong>Tags:</strong> ' +
        ticket.tags.map(tag => `<span class="tag">${tag}</span>`).join('') +
        '</p>';
    }

    html += `
      <div class="${cardClass}">
        <h3>${ticket.id || ticket.ticket_id} ${step}</h3>
        <p><strong>Last Updated:</strong> ${received}</p>
        ${tagsHtml}
        <p><strong>Source:</strong> ${ticket.module || 'N/A'}</p>
        <p><strong>Email:</strong> "${ticket.email_subject || 'No subject'}"</p>
      </div>
    `;
  }

  container.innerHTML = html;

  setTimeout(() => {
    document.querySelectorAll('.flash').forEach(el => el.classList.remove('flash'));
  }, 2000);
}

function showNotification(message) {
  let toast = document.getElementById('toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'toast';
    toast.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: #34495e;
      color: white;
      padding: 14px 20px;
      border-radius: 8px;
      z-index: 1000;
      box-shadow: 0 4px 16px rgba(0,0,0,0.2);
      font-family: sans-serif;
      max-width: 320px;
      text-align: center;
      opacity: 0;
      transform: translateX(100%);
      transition: opacity 0.3s ease, transform 0.3s ease;
    `;
    document.body.appendChild(toast);

    const style = document.createElement('style');
    style.id = 'toast-styles';
    style.textContent = `
      @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
      }
      #toast {
        animation: slideIn 0.3s forwards;
      }
    `;
    document.head.appendChild(style);
  }

  toast.textContent = message;
  toast.style.opacity = 1;
  toast.style.transform = 'translateX(0)';
  toast.style.display = 'block';

  setTimeout(() => {
    toast.style.opacity = 0;
    toast.style.transform = 'translateX(100%)';
    setTimeout(() => { toast.style.display = 'none'; }, 300);
  }, 3000);
}
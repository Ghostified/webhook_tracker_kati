// Frontend Logic for the dashboard
// -Loads ticket data via /ticket/{user_id}
// -Displays stats: total , new , updated
// -Supports filtering by Date, time and ID
// -Auto refresges every 10 seconds 
// -shows toast notifications

//Initialize user_id from local storage or generate a new one
let userId = localStorage.getItem('user_id');
if (!userId) {
  userId = 'usr_' + Math.random().toString(36).substr(2,9);
  localStorage.setItem('user_id', userId)
}
window.USER_ID = userId;

//Auto - refresh interval :  10 seconds 
const AUTO_REFRESH_INTERNAL = 10000;

//Track previous counts to detect changes
let lastNewCount = 0;
let lastUpdatedCount = 0;

//wait for DOM to load 
document.addEventListener('DOMContentLoaded', () => {
  //set webhook url in UI
  const webhookUrl = `${window.location.origin}/webhook/${userId}`;
  document.getElementById('webhook-url').textContent = webhookUrl;

  //start loading data
  refreshDashboard();
  setInterval(refreshDashboard, AUTO_REFRESH_INTERNAL);

  //set up event listeners
  document.getElementById('apply-filters').addEventListener('click', refreshDashboard);
  document.getElementById('clear-filters').addEventListener('click', resetFilters);
  document.getElementById('clear-data').addEventListener('click', clearAllData);
})

function resetFilters(){
  document.getElementById('filter-step').value = '';
  document.getElementById('filter-ticket-id').value = '';
  document.getElementById('filter-date-from-date').value = '';
  document.getElementById('filter-date-from-time').value = '';
  document.getElementById('filter-date-to-date').value = '';
  document.getElementById('filter-date-to-time').value = '';
  refreshDashboard();
}

function clearAllData(){
  if(confirm("Are you sure you want to delete All your data?")) {
    fetch(`/clear/${window.USER_ID}`, {method: 'POST'})
    .then(() => {
      showNotification("All Data Cleared");
      refreshDashboard();
    })
    .catch(err => console.error("clear all data failed", err));
  }
}

function refreshDashboard() {
  const fetchTime = Date.now();

  fetch(`/tickets/${window.USER_ID}`)
  .then(res => {
    if(!res.ok) throw new Error (`HTTP ${res.status}`);
    return res.json();
  })
  .then(data => {
    const container = document.getElementById('tickets-container');
    if (!container) return;

    //count metrics
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

    //show Notification
    if (newCount > lastNewCount && lastNewCount >= 0) {
      showNotification(`New Ticket Received  (${newCount} total)`);
    }
    if (updatedCount > lastUpdatedCount && lastUpdatedCount >= 0) {
      showNotification(`Ticket Updated (${updatedCount} total)`);
    }

    lastNewCount = newCount;
    lastUpdatedCount = updatedCount;

    //Update statistics
    document.getElementById('total-count').textContent = total;
    document.getElementById('new-counr').textContent = newCount;
    document.getElementById('updated-count').textContent = updatedCount;

    //update last updated time
    const now = new Date();
    const minsAgo = Math.floor((now - fetchTime)/ 60000);
    document.getElementById('last-updated').textContent = 
    `Last updated : ${minsAgo === 0 ?  'just now' : `${minsAgo} ${minsAgo === 1 ? 'minute' : 'minutes'} ago `}`;

    //render tickets
    renderTickets(container, data);
  })
  .catch(err => {
    console.error("Fetch error", errr);
    container.innerHTML = `<p style="color:red;">Failed to load data.</p>`;
  });
}

// Render ticket list with sorting and filtering
function renderTickets(container, data){
  //convert to array and sort by most recent first 
  const tickets = Object.entries(data)
  .map(([id, t]) => ({id, ...t }))
  .sort((a, b) => new Date(b.received_at) - new Date(a.received_at));

  //Get filter values
  const stepFilter = document.getElementById('filter-step').value.toLowerCase();
  const idFilter = document.getElementById('filter-ticket-id').value.trim().toLowerCase();

  const fromDateStr = document.getElementById('filter-date-from-date').value;
  const fromTimeStr = document.getElementById('filter-date-from-time').value || '00:00';
  const toDateStr = document.getElementById('filter-date-to-date').value;
  const toTimeStr = document.getElementById('filter-date-to-time').value || '23:59';

  const dateFrom = fromDateStr ? new Date(`${fromDateStr}T${fromTimeStr}`) : null;
  const dateTo = toDateStr ? new Date(`${toDateStr}T${toTimeStr}`) : null;

  //Apply Filters
  const filtered = tickets.filter(ticket => {
    if (stepFilter && (ticket.step || '').toLowerCase() !== stepFilter) return false;
    if (idFilter && !String(ticket.id || ticket.ticket_id).toLocaleLowerCase().includes(idFilter)) return false;
  })
    //Apply Filters
  const filtered = tickets.filter(ticket => {
    if (stepFilter && (ticket.step || '').toLowerCase() !== stepFilter) return false;
    if (idFilter && !String(ticket.id || ticket.ticket_id).toLocaleLowerCase().includes(idFilter)) return false;
  })

  //combine date and time inputs into fulltime datetime objects

}
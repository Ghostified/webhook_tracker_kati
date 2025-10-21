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
  
}
// Auto refresh page every 10 seconds 
const AUTO_REFRESH_INTERVAL = 10000; //10 seconds

function refreshDashboard(){
  console.log("Refreshing payload data...");
  fetch('/tickets')
  .then(response => response.json())
  .then(data => {
    const container = document.getElementById('/tickets-container');
    const count = Object.keys(data).length;

    document.getElementById('ticket-count').textContent = count;

    let html = '';

    if (count === 0) {
      html = '<p class="empty"> Payload Not Received Yet</p>';
    } else {
      for (const [ticketId, ticket] of Object.entries(data)) {
        const step = ticket.step? `<span class="step">${ticket.step}</span>` : '';
        const received = ticket.received_at ? new Date(ticket.received_at).toLocaleString() : 'Unknown';

        let tagsHtml = '';
        if(Array.isArray(ticket.tags) && ticket.tags.length > 0) {
          tagsHtml = '<p><strong>Tags: </strong> ' + 
          tickets.tags.map(tag => `<span class="tag">${tag}</span>`).join('') +
          '</p>';
        }

        html += `
        <div class="ticket">
        <h3>${ticketId} ${step}</h3>
        <p><strong>Last Updated:</strong>${received}</p>
        ${tagHtml}
        <p><strong>Source:</strong> ${ticket.module || 'N/A'}</p>
        <p><strong>Email:</strong> ${ticket.email_subject || 'No subject'}"</p>
        </div>
        `;
      }
    }

    container.innerHTML = html;
  })
  .catch(err => {
    console.error("Error loading payload", err);
    document.getElementById('tickets-container').innerHTML = 
    '<p style="color:red;">Failed to load Data. Check if the server is running...</p>';
  });
}

//initial load
document.addEventListener('DOMContentLoaded', () => {
  refreshDashboard(); //Load Once On Start
  setInterval(refreshDashboard, AUTO_REFRESH_INTERVAL); //then auto refresh
});
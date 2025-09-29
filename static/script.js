// Auto refresh page every 10 seconds 
const AUTO_REFRESH_INTERVAL = 10000; //10 seconds

function refreshDashboard(){
  console.log("Refreshing payload data...");
  fetch('/tickets')
  .then(response => response.json())
  .then(data => {
    const container = document.getElementById('tickets-container');
    const countElement = document.getElementById('ticket-count');

    if (!container){
      console.error("Tickets-Container not found in HTML")
      return;
    }

    if (!countElement){
      console.error("Ticket count not found in container ");
      return;
    }

    const count = Object.keys(data).length;

    // document.getElementById('ticket-count').textContent = count;
    countElement.textContent = count;

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
          ticket.tags.map(tag => `<span class="tag">${tag}</span>`).join('') +
          '</p>';
        }

        html += `
        <div class="ticket">
        <h3>${ticketId} ${step}</h3>
        <p><strong>Last Updated:</strong>${received}</p>
        ${tagsHtml}
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
    const container = document.getElementById('tickets-conatainer');
    if (container) {
      container.innerHTML = `
      <p style="color:red;">
      Failed to load Data . <br>
      Check:</br>
      1. Is server running? (<a href="/tickets">tickets</a>)<br>
      2. Any Errors on terminal?</br>
      3. Correct file names?
      </p>
      `;
    }
  });
}

//initial load
document.addEventListener('DOMContentLoaded', () => {
  refreshDashboard(); //Load Once On Start
  setInterval(refreshDashboard, AUTO_REFRESH_INTERVAL);
  
  //Add toast notification element
  const toast = document.getElementById('div');
  toast.id = 'toast';
  toast.style.display = 'none';
  toast.style.position = 'fixed';
  toast.style.top ='20px';
  toast.style.right = '20px';
  toast.style.background = '#27ae60';
  toast.style.color = 'white';
  toast.style.padding = '12px 20px'
  toast.style.boarderRadius = '6px';
  toast.style.zIndex = '1000';
  toast.style.boxshadow = '0 4px 12px rgba(0,0,0,0.2)';
  document.body.appendChild(toast);
});

//use flask to send "new_ticket" event via SSE Later
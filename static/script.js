// Auto refresh page every 10 seconds 
const AUTO_REFRESH_INTERVAL = 10000; //10 seconds

//Track ticket count across refresh
let lastCount = 0; 

//DOMContentLoaded ensures page is ready
document.addEventListener('DOMContentLoaded', () => {
  refreshDashboard(); //LOad Once start
  setInterval(refreshDashboard, AUTO_REFRESH_INTERVAL); //Then autotrefresh
});


function refreshDashboard(){
  console.log("Refreshing payload data...");
  fetch('/tickets')
  .then(response =>  {
    if(!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  })
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

    //show notification if new ticket has arrived 
    if (count > lastCount && lastCount > 0){
      showNotification(`New Ticket Received. Total:${count}`)
    }
    lastCount = count;

    // update ticket count
    countElement.textContent = count;    

    let html = '';

    if (count === 0) {
      html = '<p class="empty"> Payload Not Received Yet</p>';
    } else {
      for (const [ticketId, ticket] of Object.entries(data)) {
        const step = ticket.step
        ? `<span class="step">${ticket.step}</span>`
        : '';

        const received = ticket.received_at
        ? new Date(ticket.received_at).toLocaleString()
        : 'Unknown';

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
    const container = document.getElementById('tickets-container');
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

//resusable toast Notification
    function showNotification(message){
      let toast = document.getElementById('toast');
      if(!toast) {
        toast = Object.assign(document.createElement('div'),{
          id: 'toast',
          style: `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #27ae60;
            color: white;
            padding: 12px 20px;
            border-radius: 6px;
            z-index: 1000;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            font-family: sans-serif; max-width: 300px;
            max-width: 300px;
            text-align: center;
          `
        });
        document.body.appendChild(toast);
      }
      toast.textContent = message;
      toast.style.display = 'block';
      setTimeout(() => toast.style.display = 'none', 3000);
    }

//use flask to send "new_ticket" event via SSE Later
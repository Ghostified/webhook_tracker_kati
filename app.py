
from flask import Flask, request, jsonify
from tickets_tracker import TicketTracker

app = Flask(__name__)
tracker = TicketTracker()  # Create one instance of our tracker

@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.get_json()
    if not payload:
        return jsonify({"error": "No JSON payload"}), 400

    try:
        is_changed, changes = tracker.receive_ticket(payload)
        ticket_id = payload.get('id') or payload.get('ticket_id')

        # Log to console
        if is_changed:
            print(f"\n CHANGES DETECTED in Ticket {ticket_id}:")
            for field, change in changes.items():
                if field != "first_received":
                    print(f"   {field}: '{change['old']}' → '{change['new']}'")
                else:
                    print(f"   {change}")
        else:
            print(f"\n Ticket {ticket_id} updated (no changes)")

        return jsonify({
            "received": True,
            "ticket_id": ticket_id,
            "has_changes": is_changed,
            "changes": changes
        })

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/tickets', methods=['GET'])
def get_tickets():
    tickets = tracker.get_all_tickets()

    #Optional filter by status
    status_filter = request.args.get('step')
    if status_filter:
        filtered_tickets = {}
        for tid, ticket in tickets.items():
            if ticket.get('step') == status_filter:
                filtered_tickets[tid] = ticket
        return jsonify(filtered_tickets)
    
    return jsonify(tickets)

@app.route('/tickets/<ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    ticket = tracker.get_ticket(ticket_id)
    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404
    return jsonify(ticket)

@app.route('/', methods=['GET'])
def home():
    count = len(tracker.get_all_tickets())
    return f"<h1> Ticket Webhook Tracker</h1><p>Total tickets: {count}</p><a href='/tickets'>View All Tickets</a>"

if __name__ == '__main__':
    app.run(port=3000, debug=True)
# from flask import Flask, request, jsonify
# import json
# import os
# from datetime import datetime

# app = Flask(__name__)

# #File to store ticket data
# DB_FILE = "tickets.json"

# #Load existing  tickets from file
# def load_tickets():
#   if os.path.exists(DB_FILE):
#     with open (DB_FILE, 'r') as f:
#       return json.load(f)
#   return {}

# #save ticket to file 
# def save_tickets(tickets):
#   with open(DB_FILE, 'w') as f:
#     json.dump(tickets, f, indent=2)

# #In memory storage ( loaded from file)
# tickets = load_tickets()

# @app.route('/webhook', methods=['POST'])
# def webhook():
#   #Get JSON payload
#   payload = request.json()
#   if not payload: 
#     return jsonify({"error": "No json payload"}), 400
  
#   #Assume the ticket has an id field
#   ticket_id = payload.get('id') or payload.get(ticket_id)
#   if not ticket_id:
#     return jsonify({"error": "Missing ticket id "}), 400
  
#   #Add time stamps
#   payload['received_at'] = datetime.now().isoformat()

#   #Get old version
#   old_ticket = tickets.get(ticket_id)

#   #Find Changes
#   changes = {}
#   if old_ticket:
#     for key, new_value in payload.items():
#       old_value = old_ticket.get(key)
#       if old_value != new_value:
#         changes[key] = {"old": old_value, "new": new_value}
#   else:
#     changes = {"first_received: " "This is the first time this ticket was received"}

#   #Save new version
#   tickets[ticket_id] = payload
#   save_tickets(tickets)

#   #Print changes on  the console
#   if len(changes) > 0 and "first_received" not in changes:
#     print(f"\n CHANGES DETECTED IN Ticket {ticket_id}:")
#     for field, change in changes.items():
#       print(f" {field}: '{change['old']}' transformation '{change['new']}'")
#   else:
#     print(f"\n New Ticket received: {ticket_id}")

#   #Return Response
#   return jsonify({
#     "received": True,
#     "ticket_id": ticket_id,
#     "changes": changes
#     })

# @app.route('/tickets', methods=["GET"])
# def get_tickets():
#   return jsonify(tickets)

# #View Total Count
# @app.route('/', methods=['GET'])
# def home():
#   return f"<h1>Webhook Tracker Running</h1><p>Total Tickets stored: {len(tickets)}</p><a href='/tickets'>View All Tickets</a>"

# if __name__ == '__main__':
#   app.run(port=3000, debug=True)
# app.py
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
    return jsonify(tracker.get_all_tickets())

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
"""
app.py
Main flask application
Handles: 
- Serving the dashboard per user
-Receiving webhooks
-Fetching and clearing ticket data
All data is separated by user_id.
"""

import os
from flask import Flask, request, jsonify, render_template, send_from_directory
from ticket_tracker import TicketTracker 

app = Flask(__name__)
#Serve the main dashboard page
@app.route('/<user_id>')
def dashboard(user_id):
    """
    Serves the dashboard for a sepecific user
    Validates user_id formart to prevent path traversal attcks
    """
    if not is_valid_user_id(user_id):
        return "Invalid User ID", 400
    return render_template('index.html', user_id=user_id)

#Webhook endpoint: Receive ticket data
@app.route('/webhook/<user_id>', methods=['POST'])
def webhook(user_id):
    """
    Accept POST Requests containing ticket updates
    Each user has their own endpoint: /webhook/abc123
    """
    if not is_valid_user_id(user_id):
        return jsonify({"error": "Invalid user ID"}), 400
    
    #create tracker for this user
    tracker = TicketTracker(user_id=user_id)

    #Parse incoming Json
    payload = request.get_json()
    if not payload:
        return jsonify({"error"  : "No JSON Payload"}), 400
    
    try: 
        #Process the ticket
        is_changed, changes = tracker.receive_ticket(payload)
        ticket_id = payload.get('id') or payload.get('ticket_id')

        #Log changes to console
        if is_changed and changes:
            ch_str = ", ".join(changes.keys())
            print(f"User[{user_id}] Ticket[{ticket_id}] changed: {ch_str}")

        return jsonify({
            "received": True,
            "user_id": user_id,
            "ticket_id": ticket_id,
            "has_changes": is_changed,
            "changes":changes
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


#API: get all tickets for a user
@app.route('/tickets/<user_id>')
def get_tickets(user_id):
    """
    Return all the tickets for a given user
    Used to display data o =n the dashboard
    """
    if not is_valid_user_id(user_id):
        return jsonify({"Error": "Invalid user id"}), 400
    
    tracker = TicketTracker(user_id=user_id)
    return jsonify(tracker.get_all_tickets())

#API: Clear all data for a user 
@app.route('/clear/<user_id>', methods=['POST'])
def clear_data(user_id):
    """
    This deletes all  ticket data for a user
    Triggered from thr dashboard UI
    """
    if not is_valid_user_id(user_id):
        return jsonify({"error": "Invalid user Id"}), 400
    
    tracker = TicketTracker(user_id=user_id)
    tracker.clear_all()
    print(f"Cleared data for the user: {user_id}")
    return jsonify({"status": "cleared"})

#Utility ; validate the user_id to prevent security issues
def is_valid_user_id(user_id):
    """
    Simple validation mechnaism , alphanumeric and of reasonable length.
    prevents path trabversal (e.g.. '../../etc/passwrd').
    """
    return user_id.isalnum() and 1 <= len(user_id) <= 50

#Start server
if  __name__=='__main__':
    app.run(port=3000, debug=True)


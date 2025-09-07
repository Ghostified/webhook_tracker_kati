import json
import os
from datetime import datetime
from collections import Counter

class TicketTracker:
  def __init__(self, db_file="tickets.json"):
    self.db_file = db_file
    self.tickets = self.load_tickets()

  def load_tickets(self):
    """Load tickets from Json File"""
    if os.path.exists(self.db_file):
      with open(self.db_file, 'r') as f:
        return json.load(f)
    return{}
  
  def save_tickets(self):
    """Save current tickets to JSON file"""
    with open(self.db_file, 'w') as f:
      json.dump(self.tickets, f , indent=2)

  def receive_ticket(self, payload):
    """
    Receive ticket payload, detect changes , and save
    Returns: (is_changed: bool, changes: dict)
    """
    ticket_id = payload.get('id') or payload.get('ticket_id')
    if not ticket_id:
      raise ValueError("Ticket must have an 'id' or 'ticket_id' ")
    
    #Add timestamp
    payload['received_at'] = datetime.now().isoformat()

    old_ticket = self.tickets.get(ticket_id)
    changes = self._detect_changes(old_ticket, payload)

    #Save the new versions
    self.tickets[ticket_id] = payload
    self.save_tickets()

    is_changed = len(changes) > 0
    return is_changed , changes
  
  def _detect_changes(self, old_ticket, new_ticket):
    """Compare old ticket and new ticket , return dict and diffrences"""
    changes = {}
    if old_ticket is None:
      return{"first_received: " "This is the first time this ticket has been received"}
    
    for key, new_value in new_ticket.items():
      old_value = old_ticket.get(key)

      #skip if both are blank /empty (treat " " and None as the same)
      if self._is_blank(old_value) and self._is_blank(new_value):
        continue

      #Detect Meaningful change
      if old_value != new_value:
        changes[key] = {
          "old": old_value,
          "new": new_value
        }
    return changes
  
  def _is_blank(self, value):
    """Helper function to check if value is none or an empty string"""
    return value is None or value == ""
  
  def get_all_tickets(self):
    """Return all stored tickets"""
    return self.tickets
  
  def get_ticket(self, ticket_id):
    """Get a single ticket  by ID"""
    return self.tickets.get(ticket_id)
  
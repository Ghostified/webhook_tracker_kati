"""
This class manages the storage , retrival , and changes detection of ticket data
Each user has their own file (e,g user_data/user123.json ) for individual isolation
"""

import json
import os
from datetime import datetime
from collections import Counter

class TicketTracker: 
  def __init__(self, user_id="default"):
    """
    Initialize tracker for a specific user
    Create a unique json file per user under 'user/data/'.
    """
    self.user_id = user_id
    self.db_file = f"user_data/{user_id}.json"

    #Ensure the directory exists
    os.makedirs("user_data", exist_ok=True)

    #Load existing tickets from  file
    self.tickets = self.load_tickets()

  def load_tickets(self):
    """
    load ticket data from the user json file
    if file does not exist or is corrupted return an empty dict
    """
    if os.path.exists(self.db_file):
      try:
        with open(self.db_file, "r") as f:
          return json.load(f)
      except (json.JSONDecodeError, PermissionError) as e:
        print(f"Warning: Could not read {self.db_file} : {e}")
        return {}
    return {}
  
  def save_tickets(self):
    """
    Save current tickets to the users JSON File
    Handle errors gracefully
    """
    try:
      with open(self.db_file, "w") as f:
        json.dump(self.tickets, f , indent=2)
    except Exception as e:
      print(f"Error saving data for {self.user_id}: {e}")

  def receive_ticket(self, payload):
    """
    Receive a new or updated ticket
    Detect changes compared to previous version
    Returns: (is_changed: bool , changes : dict)
    """
    #identify the ticket using ticket_id or id
    ticket_id  = payload.get('id') or payload.get('ticket_id')
    if not ticket_id:
      raise ValueError("Ticket must have id or ticket_id")
    
    #Add timestamp when ticket was received
    payload['received_at'] = datetime.now().isoformat()

    #Get previous version (if any exists)
    old_ticket = self.tickets.get(ticket_id)

    #Compare and Detect any meaningful changes in the ticket
    changes = self._detect_changes(old_ticket, payload)

    #After detection store the new version
    self.tickets[ticket_id] = payload
    self.save_tickets()

    #Return wether anything  changed
    is_changed = len(changes) > 0
    return is_changed, changes 
  
  def _detect_changes(self, old_ticket, new_ticket):
    """
    compare two versions of a ticket and return the diffrences
    Ignore internal fields like time
    Treats empty strings and None as equal
    """
    changes = {}

    #If no previous version , this is a new ticket 
    if old_ticket is None:
      return {"first_received": "This is the first time this ticket has been received"}
    
    # Loop through all fields in the new ticket
    for key, new_value in new_ticket.items():
      #skip the meta data we added 
      if key == "received_at":
        continue

      old_value = old_ticket.get(key)

      #Treat None and " " as same 
      if self._is_blank(old_value) and self._is_blank(new_value):
        continue

      #Use deep comparisons for lists/dicts
      if not self._values_equal(old_value, new_value):
        changes[key] = {
          "old": old_value,
          "new": new_value
        }
    return changes
  
  def _is_blank(self, value):
    """Check if value is none or an empty string."""
    return value is None or value == ""
  
  def _values_equal(self, val1, val2):
    """
    Deep comaprison that handles lists (Order - insensitive) and dicts
    Uses json serialization for consistent dict comparison
    """
    if val1 is val2:
      return True
    if val1 is None or val2 in None:
      return False 
    
    # Handle lists: compare content regardless of order 
    if isinstance(val1, list) and isinstance(val2, list):
      return self._unordered_lists_equal(val1, val2)
    
    #Handle dicts : sort keys and compare as json
    if isinstance(val1, dict) and isinstance(val2, dict):
      return json.dumps(val1, sort_keys=True, separators=(',',':')) == \
        json.dumps(val2, sort_keys=True, separators=(',',':'))
    #Default Comparisons
    return val1 == val2
  
  def _unordered_lists_equal(self, list1, list2):
    """
    Compare two lists without caring about item order
    safely handle nested structures like discts and lists
    """
    if len(list1) != len(list2):
      return False
    

    def make_hashable(item):
      if isinstance(item, dict):
        return tuple(sorted((k, make_hashable(v)) for k, v in item.items()))
      elif isinstance(item, list):
        return tuple(make_hashable(i) for i in item)
      return item
    
    try:
      sorted1 = sorted(make_hashable(x) for x in list1)
      sorted2 = sorted(make_hashable(x) for x in list2)
      return sorted1 == sorted2
    except Exception:
      #fallback : direct comparison (order-sensitive)
      return list1 == list2
    
  def get_all_tickets(self):
    """Return all sorted tickets to this user"""
    return self.tickets

  def clear_all(self):
    """
    Remove all tickets for user.
    Deletes the file from disk
    """
    self.tickets = {}
    if os.path.exists(self.db_file):
      os.remove(self.db_file)



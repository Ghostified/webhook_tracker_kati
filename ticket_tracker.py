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
      return{"first_received": "This is the first time this ticket has been received"}
    
    for key, new_value in new_ticket.items():
      old_value = old_ticket.get(key)

      #Skip internal files
      if key == "received_at":
        continue

      #Debug
      # print(f" Comparing {key}: {old_value} vs {new_value} → Equal: {self._values_equal(old_value, new_value)}")


      #skip if both are blank /empty (treat " " and None as the same)
      if self._is_blank(old_value) and self._is_blank(new_value):
        continue

      #Use deep comparison to detect meaningful change (to handle lists, dicts etc)
      if not self._values_equal(old_value, new_value):
        changes[key] = {
          "old": old_value,
          "new": new_value
        }
    return changes
  
  def _is_blank(self, value):
    """Helper function to check if value is none or an empty string"""
    return value is None or value == ""
  
  def _values_equal(self, val1, val2):
    """
    deep comparison that ignores order for list
    Handles strings, numbers, lists and dicts
    """
    #same object or both None
    if val1 is val2:
      return True
    if val1 is None or val2 is None:
      return False
    
    #Handle Lists : compare ads unordered
    if isinstance(val1, list) and isinstance(val2, list):
      return self._unordered_lists_equal(val1,val2)
    
    #Handle Dicts: compare via sorted json
    if isinstance(val1, dict) and isinstance(val2, dict):
      return json.dumps(val1, sort_keys=True, separators=(',', ':')) == \
            json.dumps(val2, sort_keys=True, separators=(',', ':'))
    
    #default comparisons 
    return val1 == val2
  

  def _unordered_lists_equal(self, list1, list2):
    """Compare two lists without order, safely handling strings ,numbers, dicts"""
    if len(list1) != len(list2):
      return False
    
    def make_comparable(item):
      if isinstance(item, dict):
        return tuple(sorted((k, make_comparable(v)) for k, v in item.items()))
      elif isinstance(item, list):
        return tuple(make_comparable(i) for i in item)
      else:
        return item #string numbers etc
      

    try:
      #convert all items to comparable forms
      sorted1 = sorted(make_comparable(x) for x in list1)
      sorted2 = sorted(make_comparable(x) for x in list2)
      return sorted1 == sorted2
    except Exception:
      #fallback: direct comparison (order- sensitive)
      return list1 == list2
    
    
    # def make_hashable(item):
    #   if isinstance(item, dict):
    #     return('dict', tuple(sorted((k, make_hashable(v)) for k, v in item.items())))
    #   elif isinstance(item, self):
    #     return ('list', tuple(make_hashable(i) for i in item))
    #   else:
    #     return('other', item)
      
    # try:
    #   from collections import Counter
    #   hashed1 = [make_hashable(x) for x in list1]
    #   hashed2 = [make_hashable(x) for x in list2]
    #   return Counter(hashed1) == Counter(hashed2)
    # except Exception:
    #   return list1 == list2 #fallback
  
  # def _unordered_lists_equal(self, list1, list2):
  #   """Compare two lists without order , even with dicts inside"""
  #   if len(list1) != len(list2):
  #     return False
    
  #   def make_hashable(item):
  #     if isinstance(item, dict):
  #       return ('__dict__', tuple(sorted(
  #         (k, make_hashable(v)) for k, v in item.items()
  #       )))
  #     elif isinstance(item, list):
  #       return ('__list__', tuple(make_hashable(x) for x in item))
  #     else:
  #       return item #string ,numbers etc. 
      
  #   hashed1 = [make_hashable(item) for item in list1]
  #   hashed2 = [make_hashable(item) for item in list2]

  #   from collections import Counter
  #   return Counter(hashed1) == Counter(hashed2)
    #     return json.dumps(item, sort_keys=True, separators=(',', ':'))
    #   elif isinstance(item, list):
    #     return tuple(make_hashable(x) for x in item)
    #   return item
    
    # hashed1 = [make_hashable(item) for item in list1]
    # hashed2 = [make_hashable(item) for item in list2]

    # return Counter(hashed1) == Counter(hashed2)

  
  def get_all_tickets(self):
    """Return all stored tickets"""
    return self.tickets
  
  def get_ticket(self, ticket_id):
    """Get a single ticket  by ID"""
    return self.tickets.get(ticket_id)
  
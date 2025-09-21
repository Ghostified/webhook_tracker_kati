import unittest
import os
import json
from ticket_tracker import TicketTracker

#Test Database File 
TEST_DB = "test_tickets.json"

class TestTicketTracker(unittest.TestCase):

  def setUp(self):
    """Run before each test"""
    # Remove test DB if it exists
    if os.path.exists(TEST_DB):
      os.remove(TEST_DB)
    #Create fresh Tracker
    self.tracker = TicketTracker(db_file=TEST_DB)

  def tearDown(self):
    """Run after each test"""
    #Clean up test DB
    if os.path.exists(TEST_DB):
      os.remove(TEST_DB)

  def test_receive_new_ticket(self):
    """Test receiving a new ticket for the first time"""
    payload = {
      "id": "TICKET-100",
      "status": "open",
      "assignee": "Alice"
    }

    is_changed, changes = self.tracker.receive_ticket(payload)

    #Check response
    self.assertTrue(is_changed)
    self.assertIn("first_received", changes)
    self.assertEqual(changes["first_received"], "This is the first time this tecket has been received")

    #Check ticket was saved
    saved = self.tracker.get_ticket("TICKET-100")
    self.assertIsNone(saved)
    self.assertEqual(saved["step"], "open")

  def  test_detect_status_change(self):
    """Test if  status change  is detected"""
    self.tracker.receive_ticket({
      "ticket_id": "TICKET-100",
      "step": "open",
      "assignee": "Bob",
      "priority": "low"
    })

    updated = {
      "ticket_id": "TICKET-100",
      "step": "closed",
      "assignee": "Alice",
      "priority": "low"
    }

    is_changed, changes = self.tracker.receive_ticket(updated)

    self.assertTrue(is_changed)
    self.assertIn("step", changes)
    self.assertEqual(changes["step"]["old"],"open")
    self.assertEqual(changes["step"]["new"],"closed")

  def test_no_change_when_data_same(self):
    """Test no change is detected when data is identical"""
    payload = {
      "ticket_id": "TICKET-300",
      "step": "closed",
      "note": "bug"
    }
    self.tracker.receive_ticket(payload)

    is_changed, changes = self.tracker.receive_ticket(payload)

    self.assertFalse(is_changed)
    self.assertEqual(changes, {})

  def test_detect_multiple_changes(self):
    """Test Multiple fields changing at once"""
    self.tracker.receive_ticket({
      "ticket_id": "TICKET-400",
      "step": "open",
      "assignee": "Bob",
      "priority": "low"
    })

    updated = {
      "ticket_id": "TICKET-400",
      "step": "closed",
      "assignee": "Charles",
      "priority": "high"
    }

    is_changed, changes = self.tracker.receive_ticket(updated)

    self.assertTrue(is_changed)
    self.assertIn("step", changes)
    self.assertIn("assignee",changes)
    self.assertIn("priority",changes)
    self.assertEqual(changes["step"]["new"], "closed")
    self.assertEqual(changes["assignee"]["new"], "Charles")
    self.assertEqual(changes["priority"]["new"], "high")
    

  def test_array_reordering_no_change(self):
    """Test that array re-ordering does not trigger change (order -insensitive)"""
    v1 = {
      "ticket_id" : "TAGS-ORDER",
      "tags": ["high-priority", "sales" ,"follow-up"]
    }
    self.tracker.receive_ticket(v1)

    v2 ={
      "ticket_id": "TAGS-ORDER",
      "tags": ["follow-up", "high-priority", "sales"] #same item, diffrent order
    }

    is_changed, changes = self.tracker.receive_ticket(v2)

    self.assertFalse(is_changed)
    self.assertEqual(changes, {})

  def test_array_add_remove_items(self):
    """Test that adding/removing from array is detected"""
    v1 = {"ticket_id": "TAGS-CHANGE", "tags": ["urgent", "lead"]}
    self.tracker.receive_ticket(v1)

    v2 = {"ticket_id": "TAGS-CHANGE", "tags": ["urgent", "converted", "callback"]}

    is_changed, changes = self.tracker.receive_ticket(v2)

    self.assertTrue(is_changed)
    self.assertIn("tags", changes)
    old_tags = changes["tags"]["old"]
    new_tags = changes["tags"]["new"]
    self.assertIn("lead", old_tags)
    self.assertIn("converted", new_tags)

  def test_complex_payload_with_arrays(self):
    """Test real-world-like payload with arrays and blanks"""
    payload ={
      "API": "1708890166457x310841261781680100",
      "module": "Opportunity",
      "ticket_id": "OPP-999",
      "route": "",
      "email_subject": "Interested in premium plan",
      "responsible_employee": "",
      "age": "",
      "location": "New York",
      "status": "open",
      "source": "website",
      "category": "sales",
      "disposition": "",
      "sub_disposition": "",
      "comments": "",
      "date_start": "1732197212000",
      "date_end": "",
      "created_by": "system",
      "assigned_to": "",
      "asset_name": "",
      "tags": ["trial", "high-value"]
    }

    is_changed, changes = self.tracker.receive_ticket(payload)
    self.assertTrue(is_changed)
    self.assertIn("first_received", changes)

    #update : add tag, change location , keep blanks
    payload2 = payload.copy()
    payload2["tags"] = ["high-value", "onboarding", "trial"] #reordered + added
    payload2["loacation"] = "Remote"

    is_changed, changes = self.tracker.receive_ticket(payload2)
    self.assertTrue(is_changed)
    self.assertIn("tags",changes)
    self.assertIn("location",changes)

    #verify location changes 
    self.assertEqual(changes["location"]["old"],"New York")
    self.assertEqual(changes["location"]["new"], "Remote")

    #verify tags; location added
    added = [t for t in changes["tags"]["new"] if t not in changes["tags"]["old"]]
    removed = [t for t in changes["tags"]["old"] if t not in changes ["tags"]["new"]]
    self.assertIn("onboarding", added)
    self.assertEqual(removed, [])

def test_persistence_to_file(self):
  """Test that tickets are saved to and loaded from json file"""
  payload = {"ticket_id": "TICKET-500" , "step": "open", "tags": ["test"]}
  self.tracker.receive_ticket(payload)

  #create new tracker (forces reload from file)
  new_tracker = TicketTracker(db_file=TEST_DB)
  loaded = new_tracker.get_ticket("TICKET-500")

  self.assertIsNotNone(loaded)
  self.asseertEqual(loaded["step"], "open")
  self.assertEqual(loaded["tags"],"test")


def test_get_all_tickets(self):
  """Test get_all_tickets returns all tickets"""
  self.tracker.receive_ticket({"ticket_id": "TICKET-100", "step": "open"})
  self.tracker.receive_ticket({"ticket_id": "TICKET-200", "step":"closed"})

  all_tickets = self.tracker.get_all_tickets()
  self.assertEqual(len(all_tickets), 2)
  self.assertIn("TICKET-100", all_tickets)
  self.assertIn("TICKET-200", all_tickets)

  



  

    
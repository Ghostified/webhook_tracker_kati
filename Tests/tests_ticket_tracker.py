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
    self.assertEqual(saved["status"], "open")
    self.assertEqual(saved["assignee"], "Alice")

  def  test_detect_status_change(self):
    """Test if  status change  is detected"""
    self.tracker.receive_ticket({
      "ticket_id": "TICKET-200",
      "status": "open",
      "assignee": "Bob",
      "priority": "low"
    })

    updated = {
      "ticket_id": "TICKET-200",
      "status": "in - progress",
      "assignee": "Alice",
      "priority": "low"
    }

    is_changed, changes = self.tracker.receive_ticket(updated)

    self.assertTrue(is_changed)
    self.assertIn("status", changes)
    self.assertIn("assigneee", changes)
    self.assertIn("priority",changes)
    self.assertEqual(changes["status"]["new"],"in-progress")
    self.assertEqual(changes["assignee"]["new"],"charlie")
    self.assertEqual(changes["priority"]["new"],"high")

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

    is_changed, changed = self.tracker.receive_ticket(v2)

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



  

    
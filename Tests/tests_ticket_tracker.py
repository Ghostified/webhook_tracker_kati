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
      "assignee": "Bob"
      "priority": "low"
    })

    updated = {
      "ticket_id": "TICKET-200",
      "status": "in - progress",
      "assignee": "Alice",
      "priority": "low"
    }
    
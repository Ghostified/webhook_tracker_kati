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
    #Create FResh Tracker
    
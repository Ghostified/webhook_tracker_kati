"""
This class manages the storage , retrival , and changes detection of ticket data
Each user has their own file (e,g user_data/user123.json ) for individual isolation
"""

import json
import os
from datetime import datetime
from collections import Counter

class TicketTracker: 
  def 
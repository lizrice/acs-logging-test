# Create a simulated log file
import config
import mailhandler
import notify
from log import Log
from messageQueue import Queue

import os
import random
import socket
import sys
import time
import traceback

_too_hot = 75
_just_right = 70
_too_cold = 68

def simulate():
  log = Log()
  hostname = socket.gethostname()
  msgQueue = Queue(account_name = config.AZURE_STORAGE_ACCOUNT_NAME, account_key=config.AZURE_STORAGE_ACCOUNT_KEY, queue_name=config.AZURE_STORAGE_QUEUE_NAME)

  if int(config.SIMULATION_ACTIONS) > 0:
    msg = hostname + ': Attempting to simulate ' + str(config.SIMULATION_ACTIONS) + ' actions'
    log.debug(msg)
    notify.info(msg)
  else:
    msg = hostname + ': Simulating until stopped'
    log.debug(msg)
    notify.info(msg)

  temp = 70;

  _actions = 0
  while int(config.SIMULATION_ACTIONS) == 0 or int(config.SIMULATION_ACTIONS) - _actions > 0:

    change = random.randint(-1, 1)
    if temp <= _too_cold:
      change = 1
    elif temp >= _too_hot:
      change = -1
    msgQueue.enqueue("Change since last reading: " + str(change), level="INFO")

    temp = temp + change
    msgQueue.enqueue("Current temperature: " + str(temp), level="INFO")

    if temp == _just_right:
      msgQueue.enqueue("That's perfect", level="INFO")
    elif temp < _just_right and temp > _too_cold:
      msgQueue.enqueue('Getting a little chilly', level="WARNING")
    elif temp > _just_right and temp < _too_hot:
      msgQueue.enqueue('Getting a touch warm', level="WARNING")
    elif temp <= _too_cold:
      msgQueue.enqueue('Too cold, how did this happen?', level="ERROR")
    elif temp >= _too_hot:
      msgQueue.enqueue('Too hot, how did this happen?', level="ERROR")
    else:
      msgQueue.enqueue('Can''t tell if it''s hot or cold', level="ERROR")

    msgQueue.close()

    _actions = _actions + 1
    time.sleep(int(config.SIMULATION_DELAY))

  msg = hostname + ": Simulated " + str(config.SIMULATION_ACTIONS) + " actions and added them to the queue"
  log.debug(msg)
  notify.info(msg)

def getQueueType():
  return os.environ['ACS_LOGGING_QUEUE_TYPE']

if __name__ == "__main__":
    log = Log()
    log.debug("Started to simulate logs")
    try:
      simulate()
    except:
      e = sys.exc_info()[0]
      hostname = socket.gethostname()
      log.error("Unable to simulate logging")
      notify.error(hostname + ": ACS Logging simulation failed")
      mailhandler.send(hostname + ": ACS Logging simulation failed", "Check logs on " + hostname + " for details")

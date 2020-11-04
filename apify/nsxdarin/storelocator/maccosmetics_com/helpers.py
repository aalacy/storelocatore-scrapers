import requests
import re
import datetime

from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('maccosmetics_com')

hasPout = True
try: 
  import pout


except ImportError: 
  hasPout = False

def prettyPrint(d):
  if hasPout:
    pout.v(d)
  else: 
    logger.info(d)


def printRequestInfo(r, s):
  logger.info('-------------')
  logger.info('-------------')

  logger.info('request headers')
  prettyPrint(r.request.headers)
  logger.info('-------------')

  logger.info('response status code')
  prettyPrint(r.status_code)
  logger.info('-------------')

  logger.info('response headers')
  prettyPrint(r.headers)
  logger.info('-------------')
  
  logger.info('response content')
  try:
    prettyPrint(r.json())
  except ValueError:
    logger.info('  showing first 200 characters')
    prettyPrint(r.text[0:200])
  except:
    raise
  logger.info('-------------')

  logger.info('session cookies')
  prettyPrint(s.cookies.get_dict())

  logger.info('-------------')
  logger.info('-------------')


def getFormattedDateTime():
  today = datetime.date.today()
  return today.strftime('%a+%b+%d+%Y+%X')


def setCookie(session, domain, name, value):
  if domain is None:
    cookie_obj = requests.cookies.create_cookie(name=name, value=value)
  else:
    cookie_obj = requests.cookies.create_cookie(
        domain=domain, name=name, value=value)

  session.cookies.set_cookie(cookie_obj)


def getLivePersonSession():
  lpr = requests.get('https://va.v.liveperson.net/api/js/48719195?&cb=lpCb2316x15742&t=sp&ts=1585968675293&pid=3018057214&tid=558093679&pt=MAC%20Makeup%20Store%20Near%20me%20%7C%20MAC%20Cosmetics%20-%20Official%20Site&u=https%3A%2F%2Fwww.maccosmetics.com%2Fstores&sec=%5B%22MAC%20US%22%2C%22MAC_unknown%22%2C%22abc%22%5D&df=0&os=1&sdes=%5B%7B%22type%22%3A%22ctmrinfo%22%2C%22info%22%3A%7B%22cstatus%22%3A%22maccosmetics.com%22%7D%7D%5D&identities=%5B%7B%22iss%22%3A%22LivePerson%22%2C%22acr%22%3A%220%22%7D%5D')

  livePersonCookie = lpr.headers['Set-Cookie']

  pattern = re.compile('LPVisitorID=(.+?);[\s\S]+?LPSessionID=(.+?);')
  match = pattern.match(livePersonCookie)
  livePersonVisitorID = match.group(1)
  livePersonSessionID = match.group(2)

  return {'livePersonVisitorID': livePersonVisitorID, 'livePersonSessionID': livePersonSessionID}


import csv
import time
import random
import gzip
import http.client as http_client
import ssl
import certifi
import re
import json
import urllib.parse
import us

def get_ssl_context():
  context = ssl.SSLContext(ssl.PROTOCOL_TLS)
  context.load_default_certs(purpose=ssl.Purpose.SERVER_AUTH)
  certs_path = certifi.where()
  context.load_verify_locations(cafile=certs_path)
  context.verify_mode = ssl.CERT_REQUIRED
  context.check_hostname = True
  return context

def request(method, url, body=None): 
  conn = http_client.HTTPSConnection(host_name, context=ssl_context)
  conn.connect()
  if body != None: 
    body = urllib.parse.urlencode(body)
    headers['content-length'] = len(body)
  conn.request(method, url, body=body, headers=headers)
  res = conn.getresponse()
  all_headers = res.getheaders()
  cookies = []
  for header in all_headers:
    if header[0] == 'Set-Cookie': 
      cookie = header[1].split(';')[0]
      cookies.append(cookie)
  global next_cookies_header
  next_cookies_header = "; ".join(cookies)
  content = res.read()
  conn.close()  
  content = gzip.decompress(content)
  content = content.decode('utf-8')
  return content

def get_required_search_values(): 
  # get a couple hidden inputs from the initial locations page
  html = request('GET', '/en/restaurants')
  match = re_location_root_pattern.search(html)
  location_root = match.group(1)
  match = re_request_verification_token_pattern.search(html)
  request_verification_token = match.group(1)
  return {
    "location_root": location_root, 
    "request_verification_token": request_verification_token
  }

def setup_for_posts():
  headers['origin'] = 'https://www.applebees.com'
  headers['referer'] = 'https://www.applebees.com/en/restaurants'
  headers['sec-fetch-dest'] = 'document'
  headers['sec-fetch-mode'] = 'navigate'
  headers['sec-fetch-site'] = 'same-origin'
  headers['sec-fetch-user'] = '?1'
  headers['cookie'] = next_cookies_header
  headers['content-type'] = 'application/x-www-form-urlencoded'

def get_locations_data(search_query, required_search_values): 
  url = '/api/sitecore/Locations/LocationSearchAsync'

  payload = {
    'ResultsPage': '/locations/results',
    'LocationRoot': required_search_values['location_root'],
    'NumberOfResults': 1000,
    'LoadResultsForCareers': False,
    'MaxDistance': 5000,
    'UserLatitude': '',
    'UserLongitude': '',
    'SearchQuery': search_query,
    '__RequestVerificationToken': required_search_values['request_verification_token'],
  }
  content = request('POST', url, payload)
  data = json.loads(content)
  return data

def formatHours(hours): 
  try: 
    formatted = ''
    for entry in hours: 
      if formatted != "": 
        formatted += ", "
      formatted += entry["LocationHourLabel"] + ' ' + entry["LocationHourText"] 
    return formatted
  except:
    raise 

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    required_search_values = get_required_search_values()
    setup_for_posts()
    store_numbers = []
    for state in us.states.STATES: 
      time.sleep(random.random()*10)
      data = get_locations_data(state.abbr, required_search_values)
      for loc in data["Locations"]: 
        try: 
          country_code = loc['Location']['Country']
          if country_code != "US": 
            continue
          store_number = loc['Location']['StoreNumber']
          if store_number not in store_numbers: 
            store_numbers.append(store_number)
            locator_domain = 'https://www.applebees.com'
            page_url = loc['Location']['WebsiteUrl']
            page_url = locator_domain + page_url if page_url else '<MISSING>'
            location_name = loc['Location']['Name']
            street_address = loc['Location']['Street']
            city = loc['Location']['City']
            state = loc['Location']['State']
            zipcode = loc['Location']['Zip']
            phone = loc['Contact']['Phone']
            location_type = 'Store'
            latitude = loc['Location']['Coordinates']['Latitude']
            longitude = loc['Location']['Coordinates']['Longitude']
            hours_of_operation = formatHours(loc['HoursOfOperation']['DaysOfOperationVM'])
            yield [locator_domain, page_url, location_name, street_address, city, state, zipcode, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]
        except: 
          raise

def scrape():
    data = fetch_data()
    write_output(data)

host_name = "www.applebees.com"

headers = {
  'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
  'accept-encoding': 'gzip, deflate, br',
  'accept-language': 'en-US,en;q=0.9,la;q=0.8',
  'cache-control': 'no-cache',
  'pragma': 'no-cache',
  'sec-fetch-dest': 'document',
  'sec-fetch-mode': 'navigate',
  'sec-fetch-site': 'none',
  'upgrade-insecure-requests': '1',
  'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36'
}

ssl_context = get_ssl_context()

re_location_root_pattern = re.compile('LocationSearchAsync[\s\S]+?<input id=\"LocationRoot\"[\s\S]+?value=\"([\w{}-]+?)\"')
re_request_verification_token_pattern = re.compile('LocationSearchAsync[\s\S]+?<input name=\"__RequestVerificationToken\"[\s\S]+?value=\"([\w{}-]+?)\"')

next_cookies_header = ''

scrape()

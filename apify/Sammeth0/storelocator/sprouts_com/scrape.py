from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
import re
from random import randint
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('sprouts_com')




def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():

# Begin scraper

	base_url="https://www.sprouts.com"
	location_url ="https://www.sprouts.com/stores/"
	locs = []
	streets = []
	states=[]
	cities = []
	types=[]
	phones = []
	zips = []
	longs = []
	lats = []
	timing = []
	ids=[]
	pages_url=[]
	urls=[]
	res = []	

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()

	req = session.get(location_url, headers = HEADERS)
	time.sleep(randint(1,2))
	try:
		item = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		logger.info('[!] Error Occured. ')
		logger.info('[?] Check whether system is Online.')

	locations = item.find_all(class_="cell small-6 medium-3 store-states")
	for location in locations:
		pages_url.append(location.a['href'])
	
	for u in pages_url:

		req = session.get(u, headers = HEADERS)
		time.sleep(randint(1,2))
		try:
			item = BeautifulSoup(req.text,"lxml")
			logger.info(u)
		except (BaseException):
			logger.info('[!] Error Occured. ')
			logger.info('[?] Check whether system is Online.')

		stores=item.find_all(class_="cell medium-4 large-3 list-by-state")

		for s in stores:
			urls.append(s.a['href'])

	total_links = len(urls)
	for i, u in enumerate(urls):
		logger.info("Link %s of %s" %(i+1,total_links))

		req = session.get(u, headers = HEADERS)
		time.sleep(randint(1,2))
		try:
			item = BeautifulSoup(req.text,"lxml")
			logger.info(u)
		except (BaseException):
			logger.info('[!] Error Occured. ')
			logger.info('[?] Check whether system is Online.')

		locs.append(item.find('h1').text.strip())
		try:
			streets.append(item.find(class_='store-address').text.strip().split('\n')[-2].strip())
		except:
			streets.append("<MISSING>")
		try:
			cities.append(item.find(class_='store-address').text.strip().split('\n')[-1].split(',')[0].strip())
		except:
			cities.append("<MISSING>")
		try:
			states.append(item.find(class_='store-address').text.strip().split(',')[-1].split(' ')[1])
		except:
			states.append("<MISSING>")
		try:
			zips.append(item.find(class_='store-address').text.strip().split(',')[-1].split(' ')[-1])
		except:
			zips.append("<MISSING>")
		try:
			ids.append(item.find(class_='store-number').text.strip().split('#')[1])
		except:
			ids.append("<MISSING>")
		try:
			phones.append(item.find(class_='store-phone').text.strip())
		except:
			phones.append("<MISSING>")

		types_list=item.find(class_='cell medium-6 store-services').find_all("li")
		loc_type=''
		for t in types_list:
			loc_type=loc_type+' '+t.text.replace('\n',' ')
		types.append(loc_type.strip())
		lats.append(item.find(id='store-map')['lat'])
		longs.append(item.find(id='store-map')['lon'])
		try:
			hours = item.find(id="open-hours").text.replace('\n',' ').strip()
			hours = (re.sub(' +', ' ', hours)).strip()
			timing.append(hours)
		except:
			timing.append("<MISSING>")
		
	return_main_object = []	
	for l in range(len(locs)):
		row = []
		row.append(base_url)
		row.append(locs[l] if locs[l] else "<MISSING>")
		row.append(streets[l].strip() if streets[l] else "<MISSING>")
		row.append(cities[l] if cities[l] else "<MISSING>")
		row.append(states[l] if states[l] else "<MISSING>")
		row.append(zips[l] if zips[l] else "<MISSING>")
		row.append("US")
		row.append(ids[l] if ids[l] else "<MISSING>")
		row.append(phones[l] if phones[l] else "<MISSING>")
		row.append(types[l] if types[l] else "<MISSING>")
		row.append(lats[l] if lats[l] else "<MISSING>")
		row.append(longs[l] if longs[l] else "<MISSING>")
		row.append(timing[l] if timing[l] else "<MISSING>") 
		row.append(urls[l] if urls[l] else "<MISSING>") 
		
		return_main_object.append(row)
	
    # End scraper
	return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

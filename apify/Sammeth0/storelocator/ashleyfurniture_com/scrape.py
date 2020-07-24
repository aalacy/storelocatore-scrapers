from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re 


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()

	# Begin scraper

	base_url="https://www.ashleyfurniture.com"
	location_url ="https://stores.ashleyfurniture.com/store"
	page_urls = []
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
	pages=[]
	pages_url = []

	req = session.get(location_url, headers = HEADERS)
	time.sleep(randint(1,2))
	try:
		item = BeautifulSoup(req.text,"lxml")
	except (BaseException):
		print('[!] Error Occured. ')
		print('[?] Check whether system is Online.')
	
	link=item.find(class_="state-col")
	links=link.find_all("a")
	
	for a in range(len(links)):
		pages_url.append("https://stores.ashleyfurniture.com" + links[a]['href'])
		
	for u in pages_url:
		req = session.get(u, headers = HEADERS)
		time.sleep(randint(1,2))
		try:
			item = BeautifulSoup(req.text,"lxml")
			print(u)
		except (BaseException):
			print('[!] Error Occured. ')
			print('[?] Check whether system is Online.')

		stores=item.find_all(class_="storeName")
		for s in stores:
			pages.append("https://stores.ashleyfurniture.com" + s.find("a")['href'])

	for i, p in enumerate(pages):
		print("Link %s of %s" %(i+1,len(pages)))
		req = session.get(p, headers = HEADERS)
		time.sleep(randint(1,2))
		try:
			item = BeautifulSoup(req.text,"lxml")
			print(p)
		except (BaseException):
			print('[!] Error Occured. ')
			print('[?] Check whether system is Online.')

		loc = item.find('h1').text.strip().split(',')[0]
		if "coming soon" in loc.lower():
			continue
		page_urls.append(p)
		locs.append(loc)
		streets.append(item.find(class_='address').text.strip())
		cities.append(item.find(class_='city-postal-code').text.split(',')[0])
		states.append(item.find(class_='city-postal-code').text.split(',')[1].strip()[:3].strip())
		zips.append(item.find(class_='city-postal-code').text.split(',')[1].strip()[3:].strip())
		ids.append(str(p).split('/')[-2])
		try:
			phones.append(item.find_all(class_='phone')[-1].text.strip())
		except:
			phones.append("<MISSING>")
		try:
			hours = item.find(id='storeHours').text.replace('\n',' ').replace('  ',' ').strip()
		except:
			hours = "<MISSING>"
		timing.append(hours)
		types.append("<MISSING>")
		lats.append(item.find(id='location-details')['data-lat'])
		longs.append(item.find(id='location-details')['data-lng'])

	return_main_object = []
	for l in range(len(locs)):
		row = []
		row.append(base_url)
		row.append(page_urls[l])
		row.append(locs[l] if locs[l] else "<MISSING>")
		row.append(streets[l] if streets[l] else "<MISSING>")
		row.append(cities[l] if cities[l] else "<MISSING>")
		row.append(states[l] if states[l] else "<MISSING>")
		row.append(zips[l] if zips[l] else "<MISSING>")
		row.append("US")
		row.append(ids[l] if ids[l] else "<MISSING>")
		row.append(phones[l] if phones[l] else "<MISSING>")
		row.append(types[l])
		row.append(lats[l] if lats[l] else "<MISSING>")
		row.append(longs[l] if longs[l] else "<MISSING>")
		row.append(timing[l] if timing[l] else "<MISSING>")
		
		return_main_object.append(row)
	
    # End scraper
	return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

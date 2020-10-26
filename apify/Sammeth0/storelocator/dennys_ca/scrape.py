from sgrequests import SgRequests
from bs4 import BeautifulSoup

from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import csv
import time
from random import randint

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def get_driver():
	options = Options() 
	options.add_argument('--headless')
	options.add_argument('--no-sandbox')
	options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36")
	options.add_argument('--disable-dev-shm-usage')
	options.add_argument('--window-size=1920,1080')
	return webdriver.Chrome('chromedriver', chrome_options=options)

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

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()

	base_url="https://www.dennys.ca"
	location_url ="https://www.dennys.ca/locations/"
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
	
	driver = get_driver()
	driver.get(location_url)
	time.sleep(3)
	links=driver.find_elements_by_class_name('locations-list__item')
	for l in links:
		pages.append(l.find_element_by_tag_name("a").get_attribute('href'))

	driver.close()
	time.sleep(3)

	for i, p in enumerate(pages):
		print("Link %s of %s" %(i+1,len(pages)))
		print(p)

		req = session.get(p, headers = HEADERS)
		time.sleep(randint(1,2))
		try:
			base = BeautifulSoup(req.text,"lxml")
		except (BaseException):
			print('[!] Error Occured. ')
			print('[?] Check whether system is Online.')

		locs.append(base.find('h1').text.strip())
		streets.append(base.find(class_='trailer--half address').find_all('dd')[-1].div.text)
		city_line = base.find(class_='trailer--half address').find_all('dd')[-1].find_all('div')[1].text.strip().replace('\n',' ')
		cities.append(city_line.split(',')[0].strip())
		states.append(city_line.split(',')[1].replace("&","and").strip())
		zips.append(base.find(class_='trailer--half address').find_all('dd')[-1].find_all('div')[-1].text.strip())
		try:
			phone = base.find(class_='trailer--half address').a.text.strip()
			if not phone:
				phone = "<MISSING>"			
			phones.append(phone)
		except:
			phones.append("<MISSING>")

		# Maps
		try:
			map_link = base.find('a', string='Get Directions')['href']
			req = session.get(map_link, headers = HEADERS)
			time.sleep(randint(1,2))
			maps = BeautifulSoup(req.text,"lxml")
		except (BaseException):
			print('[!] Error Occured. ')
			print('[?] Check whether system is Online.')

		try:
			raw_gps = maps.find('meta', attrs={'itemprop': "image"})['content']
			latitude = raw_gps[raw_gps.find("=")+1:raw_gps.find("%")].strip()
			longitude = raw_gps[raw_gps.find("-"):raw_gps.find("&")].strip()

			if len(latitude) < 5:
				latitude = "<MISSING>"
				longitude = "<MISSING>"				
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"
		lats.append(latitude)
		longs.append(longitude)

		try:
			hours = base.find(class_="hours").text.replace("\n\n\n"," ").replace("\n","").strip()
		except:
			try:
				hours = base.find(class_='trailer--half address').find_all('dd')[1].text.strip()
				if "pm" not in hours and "am" not in hours and "hours" not in hours:
					hours = "<MISSING>"
			except:
				hours = "<MISSING>"
		timing.append(hours)

	return_main_object = []	
	for l in range(len(locs)):
		row = []
		row.append(base_url)
		row.append(locs[l] if locs[l] else "<MISSING>")
		row.append(streets[l] if streets[l] else "<MISSING>")
		row.append(cities[l] if cities[l] else "<MISSING>")
		row.append(states[l] if states[l] else "<MISSING>")
		row.append(zips[l] if zips[l] else "<MISSING>")
		row.append("CA")
		row.append("<MISSING>")
		row.append(phones[l] if phones[l] else "<MISSING>")
		row.append("<MISSING>")
		row.append(lats[l] if lats[l] else "<MISSING>")
		row.append(longs[l] if longs[l] else "<MISSING>")
		row.append(timing[l])
		row.append(pages[l] if pages[l] else "<MISSING>") 
		
		return_main_object.append(row)
	try:
		driver_page.close()
	except:
		pass
    # End scraper
	return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

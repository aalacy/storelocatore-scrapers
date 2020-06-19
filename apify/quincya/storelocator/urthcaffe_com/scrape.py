from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import re
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def get_driver():
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Chrome('chromedriver', chrome_options=options)


def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://www.urthcaffe.com/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)

	try:
		base = BeautifulSoup(req.text,"lxml")
		print("Got today page")
	except (BaseException):
		print('[!] Error Occured. ')
		print('[?] Check whether system is Online.')

	items = base.find(class_="pm-map-wrap pm-location-search-list").find_all(class_="row")

	driver = get_driver()
	time.sleep(2)
	
	data = []
	for item in items:
		locator_domain = "urthcaffe.com"
		location_name = item.find("h4").text.strip()
		print (location_name)
		location_type = "<MISSING>"

		raw_data = str(item.find("section").find('p').a).replace("<p>","").replace("</p>","").replace("</a>","")\
					.replace("<!-- -->","").replace("</span>","").replace("\xa0"," ").split('<br/>')
		if len(raw_data) > 2:
			street_address = (raw_data[0][raw_data[0].rfind(">")+1:] + " " + raw_data[1][raw_data[1].rfind(">") +1:]).replace("  "," ")			
		else:
			street_address = raw_data[0][raw_data[0].rfind(">") +1 :].strip()
		city = raw_data[-1][:raw_data[-1].find(',')].strip()
		state = raw_data[-1][raw_data[-1].find(',')+1:raw_data[-1].rfind(' ')].strip()
		zip_code = raw_data[-1][raw_data[-1].rfind(' ')+1:].strip()
		country_code = "US"

		store_number = "<MISSING>"
		try:
			phone = re.findall("[[(\d)]{5} [\d]{3}-[\d]{4}", str(item.text))[0]
		except:
			phone = "<MISSING>"

		hours = item.find(class_='hours').get_text(separator=u' ').replace("\n"," ").replace("\xa0","").strip()
		hours_of_operation = re.sub(' +', ' ', hours)

		if "NOW OPEN" in hours_of_operation:
			hours_of_operation = hours_of_operation[:hours_of_operation.find("NOW OPEN")].strip()

		gmaps_link = item.find("section").find('p').a['href']
		driver.get(gmaps_link)
		time.sleep(7)

		try:
			map_link = driver.current_url
			at_pos = map_link.rfind("@")
			latitude = map_link[at_pos+1:map_link.find(",", at_pos)].strip()
			longitude = map_link[map_link.find(",", at_pos)+1:map_link.find(",", at_pos+15)].strip()
		except:
			latitude = "<INACCESSIBLE>"
			longitude = "<INACCESSIBLE>"

		data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

	try:
		driver.close()
	except:
		pass

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()

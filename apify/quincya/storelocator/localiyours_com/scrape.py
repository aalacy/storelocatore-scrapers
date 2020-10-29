from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import re
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('localiyours_com')



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
	
	base_link = "https://www.localiyours.com/"

	user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
	HEADERS = {'User-Agent' : user_agent}

	session = SgRequests()
	req = session.get(base_link, headers = HEADERS)

	try:
		base = BeautifulSoup(req.text,"lxml")
		logger.info("Got today page")
	except (BaseException):
		logger.info('[!] Error Occured. ')
		logger.info('[?] Check whether system is Online.')

	content = base.find('div', attrs={'class': 'pm-map-wrap pm-location-search-list'})
	items = content.findAll('div', attrs={'class': 'col-xs-12'})

	driver = get_driver()
	
	data = []
	for item in items:
		locator_domain = "localiyours.com"
		location_name = item.find('h4').text

		raw_data = str(item.find('p')).replace("<p>","").split('<br/>')
		raw_data.pop(-1)
		raw_data.pop(-1)
		
		street_address = ""
		if len(raw_data) == 2:
			street_address = raw_data[0][raw_data[0].find("span>")+5:raw_data[0].rfind("<!")]
		else:
			for row in raw_data[:-2]:
				row = row.replace("<!-- -->","").replace("\xa0", " ")
				next_address = row[row.rfind("<span>")+6:]
				street_address = street_address + " " + next_address

		street_address = street_address.replace("</span>", "").replace("  ", " ").strip()

		city = raw_data[-1][:raw_data[-1].find(',')].strip()
		state = raw_data[-1][raw_data[-1].find(',')+1:raw_data[-1].rfind(' ')].strip()
		zip_code = raw_data[-1].replace("</a>","")[raw_data[-1].rfind(' ')+1:].strip()
		country_code = "US"
		store_number = "<MISSING>"
		phone = item.findAll('p')[1].text.strip()
		location_type = "<MISSING>"

		hours_of_operation = item.find('div', attrs={'class': 'hours'}).text.replace("\xa0", " ").replace("pmF","pm F").replace("pmS","pm S")
		hours_of_operation = re.sub(' +', ' ', hours_of_operation)

		try:
			map_link = item.find('a')['href']
			driver.get(map_link)
			time.sleep(6)
			raw_gps = driver.current_url
			start_point = raw_gps.find("@") + 1
			latitude = raw_gps[start_point:raw_gps.find(',',start_point)]
			long_start = raw_gps.find(',',start_point)+1
			longitude = raw_gps[long_start:raw_gps.find(',',long_start)]
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

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
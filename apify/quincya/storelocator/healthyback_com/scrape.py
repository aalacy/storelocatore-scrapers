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
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "email"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():

	base_link = "https://www.healthyback.com/store-locator"

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

	content = base.find('div', attrs={'class': 'abs-blocks-2columns'})
	items = content.findAll('tr')

	driver = get_driver()
	data = []
	for item in items:
		locator_domain = "healthyback.com"
		location_name = item.find('h3').text.strip()
		print (location_name)
		
		lines = item.findAll('p')
		location_type = lines[0].text.strip()
		raw_line = str(lines[-1]).replace('<p>',"").replace('\n',"").replace("</a>","").replace("\xa0","").strip().split('<br/>')[-3]

		street_address = item.find('a').text.strip()
		city = raw_line[:raw_line.rfind(',')].strip()
		state = raw_line[raw_line.rfind(',')+1:raw_line.rfind(' ')].strip()
		zip_code = raw_line[raw_line.rfind(' ')+1:].strip()
		country_code = "US"
		store_number = "<MISSING>"
		phone = re.findall("[[\d]{3}-[\d]{3}-[\d]{4}", item.text.strip())[0]

		try:
			map_link = item.find('a')['href']
			driver.get(map_link)
			time.sleep(5)
			raw_gps = driver.current_url
			start_point = raw_gps.find("@") + 1
			latitude = raw_gps[start_point:raw_gps.find(',',start_point)]
			long_start = raw_gps.find(',',start_point)+1
			longitude = raw_gps[long_start:raw_gps.find(',',long_start)]
		except:
			latitude = "<MISSING>"
			longitude = "<MISSING>"

		hours_of_operation = ""
		hours = base.find(class_="column main").find_all("p")[1:3]
		for hour in hours:
			hours_of_operation = (hours_of_operation + " " + hour.get_text(separator=u' ').replace("\n"," ").replace("\xa0","").strip()).strip()

		email = item.findAll('a')[-1].text.strip()

		data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation, email])
	driver.close()
	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()

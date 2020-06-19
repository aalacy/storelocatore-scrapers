from bs4 import BeautifulSoup
import csv
import re
import time
from random import randint

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def get_driver():
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome('chromedriver', chrome_options=options)

def write_output(data):
	with open('data.csv', mode='w') as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "featured_services"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
	
	base_link = "https://www.selectphysicaltherapy.com/contact/find-a-location/"

	driver = get_driver()
	time.sleep(2)

	driver.get(base_link)

	more_link = driver.find_element_by_css_selector(".component.load-more.col-xs-12.load-more-tabs")

	# Need to load entire page list 
	while True:
		try:
			print("Loading more data ...")
			more_link.click()
			time.sleep(randint(3,5))
		except:
			break

	try:
		base = BeautifulSoup(driver.page_source,"lxml")
		print("Got today page")
	except (BaseException):
		print('[!] Error Occured. ')
		print('[?] Check whether system is Online.')

	items = base.find(class_="search-result-list").find_all("li", recursive=False)

	data = []
	for item in items:
		locator_domain = "selectphysicaltherapy.com"
		location_name = item.find(class_="loc-result-card-name").text.strip()
		print (location_name)
		location_type = item.find(class_="loc-result-card-logo").img['src']
		raw_data = str(item.find('div', attrs={'class': 'loc-result-card-address-container'}).a).replace("<a>","").replace("</a>","").split('<br/>')

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
			phone = item.find(class_="loc-result-card-phone-container").text.strip()
		except:
			phone = "<MISSING>"

		hours = item.find(class_='mobile-container field-businesshours').get_text(separator=u' ').replace("\n"," ").replace("\xa0","").strip()
		hours_of_operation = re.sub(' +', ' ', hours)

		if not hours_of_operation:
			hours_of_operation = "<MISSING>"
		
		latitude = item['data-latitude']		
		longitude = item['data-longitude']

		if len(latitude) < 5 or len(longitude) < 6:
			g_link = item.find('div', attrs={'class': 'loc-result-card-address-container'}).a['href']
			latitude = g_link[g_link.rfind("=")+1:g_link.rfind(",")]
			longitude = g_link[g_link.rfind(",")+1:]

		services = item.find(class_='mobile-container loc-service-list').get_text(separator=u' ').replace("\n"," ").replace("\xa0","").strip()
		feat_services = re.sub(' +', ' ', services)

		if not feat_services:
			feat_services = "<MISSING>"

		data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation, feat_services])

	try:
		driver.close()
	except:
		pass

	return data

def scrape():
	data = fetch_data()
	write_output(data)

scrape()

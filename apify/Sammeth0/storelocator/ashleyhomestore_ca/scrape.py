import requests
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import csv
import time 
import re 

def get_driver():
	options = Options()
	options.add_argument('--headless')
	options.add_argument('--no-sandbox')
	options.add_argument('--disable-dev-shm-usage')
	options.add_argument('--window-size=1920,1080')
	options.add_argument("user-agent= 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'")
	return webdriver.Chrome('chromedriver', options=options)

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

	base_url="https://ashleyhomestore.ca"
	location_url ="https://ashleyhomestore.ca/apps/store-locator"
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
	driver_page = get_driver()
	driver.get(location_url)
	time.sleep(5)	
	
	locations=driver.find_elements_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[1]/div[4]/ul/li')
	for l in locations:
		try:
			locs.append(l.find_element_by_xpath('./a/span[1]').text.split(' (')[0])
		except:
			locs.append(l.find_element_by_xpath('./a/span[1]').text)
		print(locs)
		print(len(locs))
		streets.append(l.find_element_by_class_name('address').text)
		print(streets)
		try:
			cities.append(l.find_element_by_class_name('city').text)
		except:
			cities.append("<MISSING>")
		print(cities)
		states.append(l.find_element_by_class_name('prov_state').text)
		print(states)
		zips.append(l.find_element_by_class_name('postal_zip').text)
		print(zips)
		try:
			ids.append(l.find_element_by_xpath('./a/span[1]').text.split(' (')[1].replace(')',''))
		except:
			ids.append("<MISSING>")

		print(ids)
		try:
			phones.append(l.find_element_by_class_name('phone').text)
		except:
			phones.append("<MISSING>")
		print(phones)
		l.find_element_by_xpath('./a').click()
		time.sleep(2)
		try:
			timing.append(l.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[1]/div[3]/div/div/div[1]/div[3]/div/div[4]/div/div/div/div/div/div/div/span[7]').text.replace('\n',' '))
		except:
			timing.append("<MISSING>")
		print(timing)


			
						
	return_main_object = []	
	for l in range(len(locs)):
		row = []
		row.append(base_url)
		row.append(locs[l])
		row.append(streets[l])
		row.append(cities[l])
		row.append(states[l])
		row.append(zips[l])
		row.append("CA")
		row.append(ids[l])
		row.append(phones[l])
		row.append("<MISSING>")
		row.append("<MISSING>")
		row.append("<MISSING>")
		row.append(timing[l]) 
		row.append(location_url)
		
		return_main_object.append(row)
	
    # End scraper
	driver.quit()
	return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

import requests
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import pandas as pd 
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
	options.add_argument("user-agent= 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36'")
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

	base_url="http://www.pigglywiggly.com"
	location_url ="http://www.pigglywiggly.com/store-locations"
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
	pages=[]
	
	
	driver = get_driver()
	driver_page = get_driver()
	time.sleep(3)
	driver.get(location_url)
	
	locations=driver.find_elements_by_tag_name("a")
	for a in range(12,len(locations)-18):
		pages_url.append(locations[a].get_attribute('href'))
		
	for u in pages_url:
		driver_page.get(u)
		time.sleep(3)
		stores=driver_page.find_elements_by_xpath("/html/body/div[1]/div[3]/div[2]/div[2]/div/div[2]/div/ul/li")
		for s in stores:
			pages.append(u)
			locs.append(s.find_element_by_xpath('.//div[1]/div/div/div[1]/span[1]').text)
			streets.append(s.find_element_by_xpath('.//div[1]/div/div/div[1]/div[1]').text)
			cities.append(s.find_element_by_class_name('locality').text)
			states.append(s.find_element_by_xpath('.//div[1]/div/div/div[1]/span[2]').text)
			zips.append(s.find_element_by_xpath('.//div[1]/div/div/div[1]/span[3]').text[:5])
			try:
				phones.append(s.find_element_by_xpath('.//div[2]/span').text)
			except:
				phones.append("<MISSING>")
			try:
				types.append(s.find_element_by_xpath('.//div[3]/span/a').text.split('.')[1].split('.')[2])
			except:
				types.append("<MISSING>")
			lat=float(str(s.find_element_by_xpath('.//div[1]/div/div/div[2]/div/a').get_attribute('href')).split('?q=')[1].split('+')[0])
			try:
				if lat<=90:
					lats.append(lat)
				else:
					lats.append("<MISSING>")
			except:
				lats.append("<MISSING>")
			try:
				long=float(str(s.find_element_by_xpath('.//div[1]/div/div/div[2]/div/a').get_attribute('href')).split('+')[1])
				if long<=180:
					longs.append(long)
				else:
					longs.append("<MISSING>")
			except:
				longs.append("<MISSING>")
			
						
	return_main_object = []	
	for l in range(len(locs)):
		row = []
		row.append(base_url)
		row.append(locs[l] if locs[l] else "<MISSING>")
		row.append(streets[l] if streets[l] else "<MISSING>")
		row.append(cities[l] if cities[l] else "<MISSING>")
		row.append(states[l] if states[l] else "<MISSING>")
		row.append(zips[l] if zips[l] else "<MISSING>")
		row.append("US")
		row.append("<MISSING>")
		row.append(phones[l] if phones[l] else "<MISSING>")
		row.append(types[l] if types[l] else "<MISSING>")
		row.append(lats[l] if lats[l] else "<MISSING>")
		row.append(longs[l] if longs[l] else "<MISSING>")
		row.append("<MISSING>") 
		row.append(pages[l] if pages[l] else "<MISSING>") 
		
		return_main_object.append(row)
	
    # End scraper
	return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

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
	driver_page = get_driver()
	driver.get(location_url)
	time.sleep(3)
	
	links=driver.find_elements_by_class_name("btn-primary location-results__btn")
	for l in links:
		pages.append(l.find_element_by_tag_name("a").get_attribute('href'))
	print(pages)
		
	for u in pages:
		driver_page.get(u)
		time.sleep(3)
		stores=driver_page.find_elements_by_class_name("Directory-listItem")
		for s in stores:
			pages.append(s.find_element_by_tag_name("a").get_attribute('href'))
			
		print(pages)
			
	for p in pages:
		driver_page.get(p)
		time.sleep(5)
		locs.append(driver_page.find_element_by_xpath('/html/body/div[1]/div/main/div/main/div/div/h1').text)
		print(locs)
		streets.append(driver_page.find_element_by_xpath('/html/body/div[1]/div/main/div/main/div/div/div[1]/div[2]/span[2]').text)
		print(streets)
		cities.append(driver_page.find_element_by_xpath('/html/body/div[1]/div/main/div/main/div/div/div[1]/div[2]/span[3]/span').text)
		print(cities)
		states.append(driver_page.find_element_by_xpath('/html/body/div[1]/div/main/div/main/div/div/div[1]/div[2]/span[4]').text)
		print(states)
		zips.append(driver_page.find_element_by_xpath('/html/body/div[1]/div/main/div/main/div/div/div[1]/div[2]/span[5]').text)
		print(zips)
		ids.append(str(p).split('/')[-1])
		print(ids)
		try:
			phones.append(driver_page.find_element_by_xpath('/html/body/div[1]/div/main/div/main/div/div/div[2]/div[1]/div[2]/div/span').text)
		except:
			phones.append("<MISSING>")
		print(phones)
		try:
			timing.append(driver_page.find_element_by_xpath('/html/body/div[1]/div/main/div/main/div/div/div[1]/div[3]/div/div').text)
		except:
			timing.append("<MISSING>")
		print(timing)
		lats.append(driver_page.find_element_by_xpath('/html/head/meta[18]').get_attribute('content'))
		print(lats)
		longs.append(driver_page.find_element_by_xpath('/html/head/meta[19]').get_attribute('content'))
		print(longs)
			
						
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
		row.append(ids[l] if ids[l] else "<MISSING>")
		row.append(phones[l] if phones[l] else "<MISSING>")
		row.append("<MISSING>")
		row.append(lats[l] if lats[l] else "<MISSING>")
		row.append(longs[l] if longs[l] else "<MISSING>")
		row.append(timing[l] if timing[l] else "<MISSING>")
		row.append(pages[l] if pages[l] else "<MISSING>") 
		
		return_main_object.append(row)
	
    # End scraper
	return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

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

	base_url="https://www.marcustheatres.com/"
	location_url ="https://www.marcustheatres.com/theatre-locations"
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
	#link=driver.find_elements_by_class_name('theatre-listing__info')
	link=driver.find_elements_by_xpath('/html/body/div/div/section/section/div[1]/div[3]/section')
	for i in link:
		locs.append(i.text.split('\n')[1].split(',')[0])
		streets.append(i.find_element_by_class_name('theatre-listing__info--address').text.split('\n')[0])
		cities.append(i.find_element_by_class_name('theatre-listing__info--address').text.split('\n')[1].split(',')[0])
		states.append(i.text.split(', ')[1].split(' ')[0])
		zips.append(i.text.split(', ')[1].split(' ')[1].split('\n')[0])
		try:
			phones.append(i.find_element_by_xpath('/html/body/div/div/section/section/div[1]/div[3]/section').text.split('\n')[5].split('\n')[0])
		except:
			phones.append("<MISSING>")
		types.append(i.find_element_by_tag_name('p').text)
		loc_page=i.find_element_by_tag_name('a').get_attribute('href')
		pages.append(loc_page)
		driver_page.get(loc_page)
		time.sleep(5)
		lat_long_link=driver_page.find_element_by_xpath('/html/body/div/div/section/section/div[2]/div[1]/div/div[1]/a').get_attribute('href')
		lats.append(lat_long_link.split('loc:')[1].split('+')[0])
		longs.append(lat_long_link.split('+')[1])			
						
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

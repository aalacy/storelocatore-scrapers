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
	link=driver.find_element_by_class_name('locations-list__items')
	links=link.find_elements_by_tag_name("a")
	for l in links:
		pages.append(l.get_attribute('href'))		
			
	for p in pages:
		driver_page.get(p)
		time.sleep(3)
		locs.append(driver_page.find_element_by_xpath('/html/body/div/section/div[1]/div/h1').text.replace('â€“',''))
		streets.append(driver_page.find_element_by_xpath('/html/body/div/main/article/section[1]/div/div/div[2]/div/div[1]/dl/dd/div[1]').text)
		cities.append(driver_page.find_element_by_xpath('/html/body/div/main/article/section[1]/div/div/div[2]/div/div[1]/dl/dd/div[2]').text.split(',')[0])
		states.append(driver_page.find_element_by_xpath('/html/body/div/main/article/section[1]/div/div/div[2]/div/div[1]/dl/dd/div[2]').text.split(',')[1])
		zips.append(driver_page.find_element_by_xpath('/html/body/div/main/article/section[1]/div/div/div[2]/div/div[1]/dl/dd/div[3]').text)
		try:
			phones.append(driver_page.find_element_by_xpath('/html/body/div/main/article/section[1]/div/div/div[1]/dl/dd/a').text)
		except:
			phones.append("<MISSING>")
		lat_long_link=driver_page.find_element_by_xpath('/html/body/div/main/article/section[1]/div/div/div[2]/div/div[1]/a').get_attribute('href')
		driver_page.get(lat_long_link)
		time.sleep(3)
		lats.append(driver_page.find_element_by_xpath('/html/head/meta[8]').get_attribute('content').split('center=')[1].split('%2C')[0])
		longs.append(driver_page.find_element_by_xpath('/html/head/meta[8]').get_attribute('content').split('%2C')[1].split('&zoom')[0])			
						
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
		row.append("<MISSING>")
		row.append(pages[l] if pages[l] else "<MISSING>") 
		
		return_main_object.append(row)
	
    # End scraper
	return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

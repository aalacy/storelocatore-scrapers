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

	base_url="https://stores.ashleyfurniture.com"
	location_url ="https://stores.ashleyfurniture.com/store"
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
	driver.get(location_url)
	time.sleep(3)
	
	link=driver.find_element_by_class_name("state-col")
	links=link.find_elements_by_tag_name("a")
	
	for a in range(len(links)):
		pages_url.append(links[a].get_attribute('href'))
		print(pages_url)
		
	for u in pages_url:
		driver_page.get(u)
		time.sleep(3)
		stores=driver_page.find_elements_by_xpath("/html/body/div[1]/div[2]/div/div[1]/div/div[4]/div")
		for s in stores:
			pages.append(s.find_element_by_tag_name("a").get_attribute('href'))
			print(pages)
			
	for p in pages:
		driver_page.get(p)
		time.sleep(3)
		locs.append(driver_page.find_element_by_xpath('/html/body/div[1]/div[2]/div/div[1]/div/div[2]/div/h1').text.split(',')[0])
		print(locs)
		streets.append(driver_page.find_element_by_xpath('/html/body/div[1]/div[2]/div/div[1]/div/div[3]/div[1]/div/div[2]/div[1]/p[1]').text)
		print(streets)
		cities.append(driver_page.find_element_by_xpath('/html/body/div[1]/div[2]/div/div[1]/div/div[3]/div[1]/div/div[2]/div[1]/p[2]').text.split(',')[0])
		print(cities)
		states.append(driver_page.find_element_by_xpath('/html/body/div[1]/div[2]/div/div[1]/div/div[2]/div/h1/span').text.split(',')[1])
		print(states)
		zips.append(driver_page.find_element_by_xpath('/html/body/div[1]/div[2]/div/div[1]/div/div[3]/div[1]/div/div[2]/div[1]/p[2]').text[:5])
		print(zips)
		ids.append(str(p).split('/')[-2])
		print(ids)
		try:
			phones.append(driver_page.find_element_by_xpath('/html/body/div[1]/div[2]/div/div[1]/div/div[3]/div[1]/div/div[2]/div[3]/a').text)
		except:
			phones.append("<MISSING>")
		print(phones)
		timing.append(driver_page.find_element_by_xpath('/html/body/div[1]/div[2]/div/div[1]/div/div[3]/div[1]/div/div[2]/div[4]').text.replace('\n',' '))
		print(timing)
		types.append(driver_page.find_element_by_xpath('/html/body/div[1]/div[2]/div/div[1]/div/div[2]/div/h1').text.split(',')[0].split(' ')[2])

		lats.append(driver_page.find_element_by_xpath('/html/body/div[1]/div[2]/div/div[1]/div/div[3]').get_attribute('data-lat'))
		print(lats)
		longs.append(driver_page.find_element_by_xpath('/html/body/div[1]/div[2]/div/div[1]/div/div[3]').get_attribute('data-lng'))
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
		row.append(types[l] if types[l] else "<MISSING>")
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

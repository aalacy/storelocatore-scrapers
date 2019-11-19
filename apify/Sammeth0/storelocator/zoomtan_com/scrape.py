import requests
#from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import pandas as pd 
from selenium.webdriver.support.ui import Select
import csv
import time 

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

	base_url="http://www.zoomtan.com"
	location_url ="http://www.zoomtan.com/tanning-salon-locations"
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
	data = []
	
	driver = get_driver()
	time.sleep(3)
	driver.get(location_url)

	select = Select(driver.find_element_by_tag_name('select'))
	for index in range(1,len(select.options)):
		select = Select(driver.find_element_by_tag_name('select'))
		select.select_by_index(index)
		time.sleep(10)
		select_city = Select(driver.find_element_by_name('cityselect'))
		for index_c in range(1,len(select_city.options)):
			select_city = Select(driver.find_element_by_name('cityselect'))
			select_city.select_by_index(index_c)
			time.sleep(5)
			urls=driver.find_elements_by_xpath('/html/body/div[1]/section[2]/div/div[1]/div[3]/a')
			for url in urls:
				page_url=url.get_attribute('href')
				driver_page= get_driver()
				driver_page.get(page_url)
				time.sleep(3)
				locs.append(driver_page.find_element_by_xpath("/html/body/div[1]/div[5]/div/div[1]/div[1]/div/div[1]/div/h3[1]").text)
				streets.append(driver_page.find_element_by_xpath("/html/body/div[1]/div[5]/div/div[1]/div[1]/div/div[1]/div/p[1]/a").text
				.replace('\n',' '))
				cities.append(page_url.split('-')[4].split('-')[0])
				states.append(page_url.split('/')[4].split('-')[0])
				zips.append(page_url.split('-')[5].split('/')[0])
				ids.append(page_url.split('/')[5].split('/')[0])
				phones.append(driver_page.find_element_by_xpath("/html/body/div[1]/div[5]/div/div[1]/div[1]/div/div[1]/div/p[2]/a").text)
				lats.append(str(driver_page.find_element_by_xpath("/html/body/div[1]/div[5]/div/div[1]/div[1]/div/div[1]/div/p[1]/a").get_attribute('href')).split('/')[6].split(',')[0])
				longs.append(str(driver_page.find_element_by_xpath("/html/body/div[1]/div[5]/div/div[1]/div[1]/div/div[1]/div/p[1]/a").get_attribute('href')).split(',')[1])
				timing.append(driver_page.find_element_by_xpath("/html/body/div[1]/div[5]/div/div[1]/div[1]/div/div[2]/p").text
				.replace('\u2003','').replace('\u2002','').replace('\n',' '))
		
		
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
		row.append(page_url[l])
		
		data.append(row)
	
    # End scraper
	return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

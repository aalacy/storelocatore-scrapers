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

	base_url="https://www.dennys.com"
	location_url ="https://locations.dennys.com/index.html"
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
	link=[]
	sub_pages=[]
	
	driver = get_driver()
	driver_page = get_driver()
	driver_link = get_driver()
	driver_sub_page=get_driver()
	driver.get(location_url)
	time.sleep(5)
	
	links=driver.find_elements_by_class_name("Directory-listItem")
	for l in links:
		if l.get_attribute("data-count")!="(1)":
			link.append(l.find_element_by_tag_name("a"))
		else:
			pages.append(l.find_element_by_tag_name("a"))
	
	for a in range(len(link)):
		if link[a].get_attribute("data-count")!="(1)":
			pages_url.append(link[a].get_attribute('href'))
		else:
			pages.append(link[a].get_attribute('href'))
		
	for u in pages_url:
		driver_link.get(u)
		time.sleep(11)
		stores=driver_link.find_elements_by_class_name("Directory-listItem")
		for s in stores:
			if s.find_element_by_tag_name("a").get_attribute("data-count")=="(1)":
				pages.append(s.find_element_by_tag_name("a").get_attribute('href'))
			else:
				driver_sub_page.get(s.find_element_by_tag_name("a").get_attribute('href'))
				time.sleep(5)
				stores_pages=driver_sub_page.find_elements_by_class_name("Directory-listTeaser")
				for sp in stores_pages:
					pages.append(sp.find_element_by_tag_name("a").get_attribute('href'))
		s_b= driver_link.find_elements_by_class_name('Directory-listTeaser')		
		if s_b:
			for b in s_b:
				pages.append(b.find_element_by_xpath('//*[@id="main"]/div/div[3]/div/section/div[2]/ul/li[1]/article/h2/a').get_attribute('href'))
					
	for p in pages:
		driver_page.get(p)
		time.sleep(3)
		locs.append(driver_page.find_element_by_xpath('/html/body/main/div/div[3]/div/div/div/div[1]/div[1]/address/div[1]/span').text)
		streets.append(driver_page.find_element_by_xpath('/html/body/main/div/div[3]/div/div/div/div[1]/div[1]/address/div[1]/span').text)
		cities.append(str(p).split('/')[-2])
		states.append(str(p).split('/')[-3])
		try:
			zips.append(driver_page.find_element_by_xpath('/html/body/main/div/div[3]/div/div/div/div[1]/div[1]/address/div[2]/span[2]').text)
		except:
			zips.append(driver_page.find_element_by_xpath('/html/body/main/div/div[3]/div/div/div/div[1]/div[1]/address/div[3]/span[2]').text)
		ids.append(str(p).split('/')[-1])
		try:
			phones.append(driver_page.find_element_by_xpath('/html/body/main/div/div[3]/div/div/div/div[1]/div[2]/div/div[2]/div[1]').text)
		except:
			phones.append("<MISSING>")
		try:
			timing.append(driver_page.find_element_by_xpath('/html/body/main/div/div[3]/div/div/div/div[2]/div[2]/div/div/table/tbody').text.replace('\n',' '))
		except:
			timing.append("<MISSING>")
		types.append(driver_page.find_element_by_xpath('/html/body/main/div/div[1]/div/div/div[1]/h1/span/span[1]').text)
		lats.append(driver_page.find_element_by_xpath('/html/body/main/div/div[3]/div/div/div/div[1]/div[1]/span/meta[1]').get_attribute('content'))
		longs.append(driver_page.find_element_by_xpath('/html/body/main/div/div[3]/div/div/div/div[1]/div[1]/span/meta[2]').get_attribute('content'))
						
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

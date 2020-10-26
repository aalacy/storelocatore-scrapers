import requests
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
	pages_url=[]
	
	
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
			# locations=driver.find_elements_by_xpath('/html/body/div[1]/section[2]/div/div[1]/div[3]/a')
			# for s in locations:
				# locs.append(s.find_element_by_xpath('//*[@id="locationitem"]/h5').text)
				# streets.append(str(s.find_element_by_xpath('//*[@id="locationitem"]').text).split('\n\n')[1].split('\n')[0].replace('\n',' '))

			urls=driver.find_elements_by_xpath('/html/body/div[1]/section[2]/div/div[1]/div[3]/a')
			for url in urls:
				page_url=url.get_attribute('href')
				pages_url.append(page_url)
				print(pages_url)
				driver_page= get_driver()
				driver_page.get(page_url)
				time.sleep(3)
				
				try:
					locs.append(driver_page.find_element_by_xpath("/html/body/div[1]/div[5]/div/div[1]/div[1]/div/div[1]/div/h3[1]").text)
				except:
					continue
				try:
					streets.append(driver_page.find_element_by_xpath("/html/body/div[1]/div[5]/div/div[1]/div[1]/div/div[1]/div/p[1]/a").text.split('\n')[0])
				except:
					streets.append("<MISSING>")
				try:
					cities.append(page_url.split('-')[4].split('-')[0])
				except:
					cities.append("<MISSING>")
				try:
					states.append(driver_page.find_element_by_xpath("/html/body/div[1]/div[5]/div/div[1]/div[1]/div/div[1]/div/p[1]/a").text.split(',')[1].split(' ')[1])
				except:
					states.append("<MISSING>")
				try:
					zips.append(page_url.split('-')[5].split('/')[0])
				except:
					zips.append("<MISSING>")
				try:
					ids.append(page_url.split('/')[5].split('/')[0])
				except:
					ids.append("<MISSING>")
				try:
					phones.append(driver_page.find_element_by_xpath("/html/body/div[1]/div[5]/div/div[1]/div[1]/div/div[1]/div/p[2]/a").text)
				except:
					phones.append("<MISSING>")				
				try:	
					lats.append(str(driver_page.find_element_by_xpath("/html/body/div[1]/div[5]/div/div[1]/div[1]/div/div[1]/div/p[1]/a").get_attribute('href')).split('/')[6].split(',')[0])
				except:
					lats.append("<MISSING>")				
				try:	
					longs.append(str(driver_page.find_element_by_xpath("/html/body/div[1]/div[5]/div/div[1]/div[1]/div/div[1]/div/p[1]/a").get_attribute('href')).split(',')[1])
				except:
					longs.append("<MISSING>")				
				try:	
					timing.append(driver_page.find_element_by_xpath("/html/body/div[1]/div[5]/div/div[1]/div[1]/div/div[2]/p").text
					.replace('\u2003','').replace('\u2002','').replace('\n',' '))
				except:
					timing.append("<MISSING>")
	
				
	return_main_object = []	
	for l in range(len(locs)):
		row = []
		row.append(base_url)
		row.append(locs[l])
		row.append(streets[l])
		row.append(cities[l])
		row.append(states[l])
		row.append(zips[l])
		row.append("US")
		row.append(ids[l])
		row.append(phones[l])
		row.append("<MISSING>")
		row.append(lats[l])
		row.append(longs[l])
		row.append(timing[l]) 
		row.append(pages_url[l])
		
		return_main_object.append(row)
	
    # End scraper
	return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

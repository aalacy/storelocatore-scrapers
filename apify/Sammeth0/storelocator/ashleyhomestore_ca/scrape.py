from bs4 import BeautifulSoup
from sgselenium import SgSelenium
import csv
import time 
import re
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('ashleyhomestore_ca')



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

	driver = SgSelenium().chrome()
	time.sleep(2)

	driver.get(location_url)
	time.sleep(5)

	base = BeautifulSoup(driver.page_source,"lxml")
	all_scripts = base.find_all('script')
	for script in all_scripts:
		if "markersCoord" in str(script):
			script = script.text.strip()
			start_pos = script.find("Coords.push")
			script = script[start_pos:script.find("});\n",start_pos)+2]
			break
	coords = re.findall(r'lat: [0-9]{2,3}\.[0-9]+, lng: -[0-9]{2,3}\.[0-9]+,', script)
	
	locations=driver.find_element_by_class_name('addresses').find_elements_by_tag_name('li')
	for i, l in enumerate(locations):
		try:
			loc = l.find_element_by_xpath('./a/span[1]').text.split(' (')[0]
			logger.info(loc)
			locs.append(loc)
		except:
			locs.append(l.find_element_by_xpath('./a/span[1]').text)
		streets.append(l.find_element_by_class_name('address').text)
		try:
			cities.append(l.find_element_by_class_name('city').text)
		except:
			cities.append("<MISSING>")
		states.append(l.find_element_by_class_name('prov_state').text)
		zips.append(l.find_element_by_class_name('postal_zip').text)
		try:
			ids.append(l.find_element_by_xpath('./a/span[1]').text.split(' (')[1].replace(')',''))
		except:
			ids.append("<MISSING>")

		try:
			phones.append(l.find_element_by_class_name('phone').text)
		except:
			phones.append("<MISSING>")
		try:
			l.find_element_by_xpath('./a').click()
			time.sleep(2)
		except:
			ActionChains(driver).send_keys(Keys.ESCAPE).perform()
			time.sleep(2)
			l.find_element_by_xpath('./a').click()
			time.sleep(2)

		longs.append(coords[i].split("lng")[-1][2:-1].strip())
		lats.append(coords[i].split("lng")[0][4:-2].strip())

		try:
			hours = driver.find_element_by_id("store_map").find_element_by_class_name("hours").text.replace("\n"," ")
			if ".ca" in hours:
				hours = hours[hours.rfind(".ca")+3:].strip()
			timing.append(hours)
		except:
			timing.append("<MISSING>")

		try:
			link = l.find_element_by_class_name("store_website").find_element_by_tag_name("a").get_attribute("href")
			pages.append(link)
		except:
			pages.append(location_url)

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
		row.append(lats[l])
		row.append(longs[l])
		row.append(timing[l])
		row.append(pages[l])
		
		return_main_object.append(row)
	
    # End scraper
	driver.quit()
	return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import csv
import time
from random import randint


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def get_driver():
	options = Options() 
	options.add_argument('--headless')
	options.add_argument('--no-sandbox')
	options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36")
	options.add_argument('--disable-dev-shm-usage')
	options.add_argument('--window-size=1920,1080')
	return webdriver.Chrome('chromedriver', chrome_options=options)

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
	driver.get(location_url)
	time.sleep(3)
	links=driver.find_elements_by_class_name('locations-list__item')
	for l in links:
		pages.append(l.find_element_by_tag_name("a").get_attribute('href'))

	driver.close()
	time.sleep(3)

	driver_page = get_driver()
	for i, p in enumerate(pages):
		print("Link %s of %s" %(i+1,len(pages)))
		print(p)
		driver_page.get(p)
		time.sleep(randint(2,4))
		try:
			element = WebDriverWait(driver_page, 30).until(EC.presence_of_element_located(
				(By.CSS_SELECTOR, ".trailer--half.address")))
			time.sleep(randint(1,2))
		except:
			try:
				driver_page.get(p)
				element = WebDriverWait(driver_page, 30).until(EC.presence_of_element_located(
					(By.CSS_SELECTOR, ".trailer--half.address")))
			except:
				print('[!] Error Occured. ')
				print('[?] Check whether system is Online.')

		locs.append(driver_page.find_element_by_xpath('/html/body/div/section/div[1]/div/h1').text.replace('â€“',''))
		streets.append(driver_page.find_element_by_xpath('/html/body/div/main/article/section[1]/div/div/div[2]/div/div[1]/dl/dd[3]/div').text)
		cities.append(driver_page.find_element_by_xpath('/html/body/div/main/article/section[1]/div/div/div[2]/div/div[1]/dl/dd/div[2]').text.split(',')[0].strip())
		states.append(driver_page.find_element_by_xpath('/html/body/div/main/article/section[1]/div/div/div[2]/div/div[1]/dl/dd/div[2]').text.replace("&","and").split(',')[1].strip())
		zips.append(driver_page.find_element_by_xpath('/html/body/div/main/article/section[1]/div/div/div[2]/div/div[1]/dl/dd/div[3]').text)
		try:
			phones.append(driver_page.find_element_by_css_selector(".trailer--half.address").find_element_by_tag_name("a").text.strip())
		except:
			phones.append("<MISSING>")
		try:
			raw_gps = driver_page.find_element_by_xpath("//*[(@title='Open this area in Google Maps (opens a new window)')]").get_attribute("href")
			lats.append(raw_gps[raw_gps.find("=")+1:raw_gps.find(",")].strip())
			longs.append(raw_gps[raw_gps.find(",")+1:raw_gps.find("&")].strip())
		except:
			lats.append("<MISSING>")
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
		row.append("CA")
		row.append("<MISSING>")
		row.append(phones[l] if phones[l] else "<MISSING>")
		row.append("<MISSING>")
		row.append(lats[l] if lats[l] else "<MISSING>")
		row.append(longs[l] if longs[l] else "<MISSING>")
		row.append("<MISSING>")
		row.append(pages[l] if pages[l] else "<MISSING>") 
		
		return_main_object.append(row)
	try:
		driver_page.close()
	except:
		pass
    # End scraper
	return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

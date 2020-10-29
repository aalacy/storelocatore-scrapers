import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
from selenium.webdriver.support.ui import Select
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('calibercollision_com')




options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("user-agent= 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'")

#driver = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver = webdriver.Chrome("chromedriver", options=options)
#driver2 = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver2 = webdriver.Chrome("chromedriver", options=options)
#driver3 = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver3 = webdriver.Chrome("chromedriver", options=options)

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def parse_geo(url):
    lat = re.findall(r'\@(-?[\d\.]*)', url)[0]
    try:
        lon = re.findall(r'\,(--?[\d\.]*)', url)[0]
    except:
        lon = url.split(lat+",")[1].split(",")[0]
    return lat, lon


def fetch_data():
    data=[]
    count=0
    driver.get("https://calibercollision.com/locate-a-caliber-collision-center")
    time.sleep(10)
    select = Select(driver.find_element_by_id('stateSelect'))
    for index in range(1, len(select.options)):
        select = Select(driver.find_element_by_tag_name('select'))
        select.select_by_index(index)
        time.sleep(3)
        locs = driver.find_elements_by_css_selector('div.loc-result > a')
        #logger.info("locs..........", locs)
        for loc in locs:
            url = loc.get_attribute('href')
            logger.info(url)
            driver2.get(url)
            time.sleep(1)
            try:
                location_name = driver2.find_element_by_css_selector('h1.cg-black.caps').text
            except:
                location_name = driver2.find_element_by_css_selector('h1.cg-orange.caps').text
            street_addr = driver2.find_element_by_css_selector('p.mb-0 > span:nth-child(1)').text
            state_city_zip = driver2.find_element_by_css_selector('p.mb-0 > span:nth-child(2)').text
            city = state_city_zip.split(",")[0]
            try:
                state = state_city_zip.split(",")[1].split(" ")[-2]
                zipcode = state_city_zip.split(",")[1].split(" ")[-1]
            except:
                state = state_city_zip.split(",")[2].split(" ")[-2]
                zipcode = state_city_zip.split(",")[2].split(" ")[-1]            
            phone = driver2.find_element_by_css_selector('div.absolute.phone > a').get_attribute('href').split("tel:")[1]
            hours_of_op = driver2.find_element_by_css_selector('span.d-block.pt-3.italic.newtime').text.replace("\n", " ")
            geomap = driver2.find_element_by_xpath("//a[contains(@href,'maps.google.com')]").get_attribute('href')
            driver3.get(geomap)
            time.sleep(5)
            lat, lon = parse_geo(driver3.current_url)
            data.append([
                'https://calibercollision.com',
                url,
                location_name,
                street_addr,
                city,
                state,
                zipcode,
                'US',
                '<MISSING>',
                phone,
                '<MISSING>',
                lat,
                lon,
                hours_of_op
            ])
            count=count+1
            logger.info(count)

    time.sleep(3)
    driver.quit()
    driver2.quit()
    driver3.quit()
    return data


def scrape():
        data = fetch_data()
        write_output(data)
        return data
    
data=scrape()






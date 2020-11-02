import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('cosmoprofbeauty_com')



options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
#driver = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver = webdriver.Chrome("chromedriver", options=options)
#driver2 = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver2 = webdriver.Chrome("chromedriver", options=options)
#driver3 = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver3 = webdriver.Chrome("chromedriver", options=options)
#driver4 = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver4 = webdriver.Chrome("chromedriver", options=options)

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def parse_geo(url):
    a=re.findall(r'&daddr=(-?[\d\.]*,(--?[\d\.]*))',url)[0]
    lat = a[0].split(",")[0]
    lon = a[0].split(",")[1]
    return lat, lon


def fetch_data():
    # Your scraper here
    count=0
    data=[]
    driver.get("https://stores.cosmoprofbeauty.com/")
    time.sleep(10)
    stores = driver.find_elements_by_css_selector('ul.browse.mb-30.mb-xs-0 > li > div.map-list-item.is-single > a')
    name = [stores[i].get_attribute('href') for i in range(0, len(stores))]
    for i in range(0,len(name)):
            driver2.get(name[i])
            page_url = name[i]
            #logger.info(page_url)
            time.sleep(1)
            stores1 = driver2.find_elements_by_css_selector('div.map-list-item.is-single > a')
            name_sub = [stores1[m].get_attribute('href') for m in range(0, len(stores1))]
            for j in range(0,len(name_sub)):
                    driver3.get(name_sub[j])
                    page_url = name_sub[j]
                    #logger.info(page_url)
                    time.sleep(1)
                    store_view_details = driver3.find_elements_by_css_selector('div.map-list-links.mt-20 > a:nth-child(1)')
                    store_view_details_lnks = [store_view_details[n].get_attribute('href') for n in range(0, len(store_view_details))]
                    for k in range(0,len(store_view_details_lnks)):
                        driver4.get(store_view_details_lnks[k])
                        time.sleep(1)
                        page_url = store_view_details_lnks[k]
                        logger.info(page_url)
                        location_name = driver4.find_element_by_css_selector('span.location-name').text
                        if location_name == "":
                            location_name ='<MISSING>'
                            store_id = '<MISSING>'
                        else:
                            store_id = location_name.split("#")[1]
                        street_addr = driver4.find_element_by_css_selector('p.address > span:nth-child(1)').text
                        state_city_zip = driver4.find_element_by_css_selector('p.address > span:nth-child(3)').text
                        #logger.info(state_city_zip)
                        city = state_city_zip.split(",")[0]
                        state = state_city_zip.split(",")[1].split(" ")[1]
                        #logger.info(state)
                        zipcode1 = state_city_zip.split(",")[1].split(" ")[2]
                        try:
                            zipcode2 = state_city_zip.split(",")[1].split(" ")[3]
                            zipcode = zipcode1 + zipcode2
                        except:
                            zipcode = zipcode1
                        if len(zipcode)==5:
                            country = 'US'
                        else:
                            country = 'CA'
                        phone = driver4.find_element_by_css_selector('a.phone.ga-link').text
                        hours_of_op = driver4.find_element_by_css_selector('div.hours').text.replace("\n", " ")
                        geomap = driver4.find_element_by_css_selector('a.directions.ga-link').get_attribute('href')
                        #logger.info(geomap)
                        latitude , longitude = parse_geo(geomap)
                        #logger.info(latitude, longitude)
                        data.append([
                            'https://stores.cosmoprofbeauty.com/',
                            page_url,
                            location_name,
                            street_addr,
                            city,
                            state,
                            zipcode,
                            country,
                            store_id,
                            phone,
                            '<MISSING>',
                            latitude,
                            longitude,
                            hours_of_op
                        ])
                        count = count + 1
                        logger.info(count)

    time.sleep(3)
    driver.quit()
    driver2.quit()
    driver3.quit()
    driver4.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

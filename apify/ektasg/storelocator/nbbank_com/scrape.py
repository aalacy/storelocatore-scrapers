import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('nbbank_com')



options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--disable-plugins")
options.add_argument("--no-experiments")
options.add_argument("--disk-cache-dir=null")

#driver = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver = webdriver.Chrome("chromedriver", options=options)
#driver2 = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver2 = webdriver.Chrome("chromedriver", options=options)


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def parse_geo(url):
    lon = re.findall(r'\,(--?[\d\.]*)', url)[0]
    lat = re.findall(r'\@(-?[\d\.]*)', url)[0]
    return lat, lon


def fetch_data():
        data = []
        driver.get("https://nbbank.com/locations/")
        time.sleep(10)

        stores = driver.find_elements_by_xpath("//tr[contains(@class,'data_item_detail_row data_type_61_detail_row')]")
        for store in stores:
            location_name = store.find_element_by_css_selector('td.field_display.field_display_single_line_text.field_display_field_id_451').text
            logger.info(location_name)
            address= store.find_element_by_css_selector('div.address_display').text.replace('View on Map','')
            address_split = address.splitlines()
            country = "US"
            state_city_zip = address_split[-2]
            city = state_city_zip.split(",")[0]
            state = state_city_zip.split(",")[1].split(" ")[-2]
            zipcode = state_city_zip.split(",")[1].split(" ")[-1]
            if len(address_split)==3:
                street_addr = address_split[0]
            elif len(address_split)==4:
                street_addr = address_split[0] + " " + address_split[1]
            geomap = store.find_element_by_css_selector('div.address_display > a').get_attribute('href').split('&url=')[1]
            geomap= geomap.replace("%3A%2F%2F","://").replace("%2F%3Fq%3D","/?q=").replace("%2B" ,"+")
            driver2.get(geomap)
            time.sleep(10)
            lat,lng = parse_geo(driver2.current_url)
            phone = store.find_element_by_css_selector('td.field_display.field_display_single_line_text.field_display_field_id_453').text
            drive_hours =store.find_element_by_xpath("//td[contains(@data-title, 'Drive-Up Hours: ')]").get_attribute('innerHTML').replace('<br>', " ").replace("&amp;", " ")
            hours_of_op = "Lobby Hours: " + store.find_element_by_css_selector('td.field_display.field_display_multi_line_text.field_display_field_id_455').text + " " + \
                            " Drive-Up Hours: " + drive_hours
            data.append([
                'https://nbbank.com/',
                location_name,
                street_addr,
                city,
                state,
                zipcode,
                country,
                '<MISSING>',
                phone,
                '<MISSING>',
                lat,
                lng,
                hours_of_op
            ])

        time.sleep(5)
        driver.quit()
        driver2.quit()
        return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()





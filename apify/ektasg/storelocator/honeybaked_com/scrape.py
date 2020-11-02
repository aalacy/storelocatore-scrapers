import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('honeybaked_com')



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
    # Your scraper here
    count=0
    data=[]
    driver.get("http://locator.honeybaked.com/")
    time.sleep(5)
    stores = driver.find_elements_by_css_selector('div.storeLocLink.col-xs-12.col-sm-4.col-md-3 > p > a')
    name = [stores[i].get_attribute('href') for i in range(0, len(stores))]
    for i in range(0,len(name)):
            driver2.get(name[i])
            page_url = name[i]
            logger.info(page_url)
            time.sleep(5)
            locations = driver2.find_elements_by_css_selector('div.srchResultRow.row')
            i=2
            while i < len(locations):
                info = locations[i].find_element_by_css_selector('div.colResult1.col-xs-12.col-sm-3').text.splitlines()
                if len(info) == 5:
                    street_addr = info[0] + info[1]
                    city = info[2].split(",")[0]
                    state = info[2].split(",")[1].split(" ")[1]
                    zipcode = info[2].split(",")[1].split(" ")[-1]
                    phone = info[3].split('PH) ')[1]
                elif len(info) ==4:
                    if 'PH) ' in info[2]:
                        street_addr = info[0]
                        city = info[1].split(",")[0]
                        state = info[1].split(",")[1].split(" ")[1]

                        zipcode = info[1].split(",")[1].split(" ")[-1]
                        try:
                            phone = info[2].split('PH) ')[1]
                        except:
                            phone = '<MISSING>'
                    elif 'PH) ' in info[3]:
                        street_addr = info[0] + info [1]
                        city = info[2].split(",")[0]
                        state = info[2].split(",")[1].split(" ")[1]

                        zipcode = info[2].split(",")[1].split(" ")[-1]
                        try:
                            phone = info[3].split('PH) ')[1]
                        except:
                            phone = '<MISSING>'
                    else:
                        street_addr = info[0]
                        city = info[1].split(",")[0]
                        state = info[1].split(",")[1].split(" ")[1]

                        zipcode = info[1].split(",")[1].split(" ")[-1]
                        phone = '<MISSING>'
                elif len(info) ==3:
                    if 'PH) ' in info[2]:
                        street_addr = info[0]
                        city = info[1].split(",")[0]
                        state = info[1].split(",")[1].split(" ")[1]

                        zipcode = info[1].split(",")[1].split(" ")[-1]
                        phone = info[2].split('PH) ')[1]
                    else:
                        street_addr = info[0] + info[1]
                        city = info[2].split(",")[0]
                        state = info[2].split(",")[1].split(" ")[1]

                        zipcode = info[2].split(",")[1].split(" ")[-1]
                        phone = '<MISSING>'
                elif len(info) ==2:
                    street_addr = info[0]
                    city = info[1].split(",")[0]
                    state = info[1].split(",")[1].split(" ")[1]
                    zipcode = info[1].split(",")[1].split(" ")[-1]
                    if zipcode == "":
                        zipcode = '<MISSING>'
                    phone = '<MISSING>'
                location_name = "HoneyBaked of " + city
                hours_of_op = locations[i].find_element_by_css_selector('div.colResult3.col-xs-12.col-sm-3').text.replace("\n"," ")

                try:
                    store_id = locations[i].find_element_by_css_selector('div.colResult4.col-xs-12.col-sm-3 > a:nth-child(1)').get_attribute('href').split("/")[-1]

                    if bool(re.search(r'\d',store_id)) == False:
                        store_id = '<MISSING>'

                except:
                    store_id = '<MISSING>'
                geomap = locations[i].find_element_by_css_selector('div.colResult2.col-xs-12.col-sm-3 > div.visible-xs > p > a').get_attribute('href')
                driver3.get(geomap)
                time.sleep(10)
                latitude, longitude = parse_geo(driver3.current_url)

                data.append([
                            'https://www.honeybaked.com/',
                            page_url,
                            location_name,
                            street_addr,
                            city,
                            state,
                            zipcode,
                            'US',
                            store_id,
                            phone,
                            '<MISSING>',
                            latitude,
                            longitude,
                            hours_of_op
                ])
                count = count + 1
                logger.info(count)
                i=i+2


    time.sleep(3)
    driver.quit()
    driver2.quit()
    driver3.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('krispykrunchy_com')



options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1920,1080')
options.add_argument("user-agent= 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'")

#driver = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver = webdriver.Chrome("chromedriver", options=options)
#driver2 = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver2 = webdriver.Chrome("chromedriver", options=options)


def parse_geo(url):
    try:
        lon = re.findall(r'\,(--?[\d\.]*)', url)[0]
    except:
        try:
            lon = re.findall(r'\,(-?[\d\.]*)', url)[0]
        except:
            lon = '<MISSING>'
    try:
        lat = re.findall(r'\@(-?[\d\.]*)', url)[0]
    except:
        lat ='<MISSING>'
    return lat, lon


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)




def fetch_data():

    data = []
    count=0
    driver.get("https://www.krispykrunchy.com/locations/")
    time.sleep(10)
    state_list = ['alabama','Alaska','Arizona','Arkansas','California','Colorado','Connecticut','Delaware','Florida','Georgia'
                  ,'Hawaii','Idaho','Illinois','Indiana','Iowa','Kansas','Kentucky','Louisiana','Maine','Maryland','Massachusetts',
                  'Michigan','Minnesota','Mississippi','Missouri','Montana','Nebraska','Nevada','New Hampshire','New Jersey',
                  'New Mexico','New York','North Carolina','North Dakota','Ohio','Oklahoma','Oregon','Pennsylvania','Rhode Island',
                  'South Carolina','South Dakota','Tennessee','Texas','Utah','Vermont','Virginia','Washington','West Virginia',
                  'Wisconsin','Wyoming']
    loc_names=[]
    for state in state_list:
        elem = driver.find_element_by_id('tb-state')
        elem.clear()
        elem.send_keys(state)
        driver.find_element_by_xpath("//button[@id='btn-search']").click()
        time.sleep(2)
        stores = driver.find_elements_by_css_selector('div.store-item')
        if len(stores)>0:
            for store in stores:
                info = store.find_element_by_css_selector('div:nth-child(2)').text.splitlines()
                #logger.info(info)
                location_name = info[0]
                if location_name in loc_names:
                    pass
                else:
                    loc_names.append(location_name)
                    street_addr = info[1]
                    if street_addr == "" or street_addr == " ":
                        street_addr = '<MISSING>'
                    if 'DO NOT USE' in street_addr:
                        street_addr = '<MISSING>'
                    state_city_zip = info[2]
                    city = state_city_zip.split(",")[0]
                    try:
                        state = state_city_zip.split(",")[1].split(" ")[-2]
                        zipcode = state_city_zip.split(",")[1].split(" ")[-1]
                    except:
                        state = state_city_zip.split(",")[2].split(" ")[-2]
                        zipcode = state_city_zip.split(",")[2].split(" ")[-1]
                    phone = store.find_element_by_css_selector('a.store-item-phone').text
                    if phone == "":
                        phone = '<MISSING>'
                    store_id = store.find_element_by_css_selector('a.store-item-link').get_attribute('href').split('store-')[1]
                    store_link = store.find_element_by_css_selector('a.store-item-link').get_attribute('href')
                    driver2.get(store_link)
                    time.sleep(1)
                    geomap = driver2.find_element_by_xpath("//a[contains(@href, 'maps.google.com')]").get_attribute('href')
                    driver2.get(geomap)
                    time.sleep(5)
                    lat,lon = parse_geo(driver2.current_url)
                    data.append([
                         'https://www.krispykrunchy.com/',
                          "https://www.krispykrunchy.com/locations/",
                          location_name,
                          street_addr,
                          city,
                          state,
                          zipcode,
                          'US',
                          store_id,
                          phone,
                          '<MISSING>',
                          lat,
                          lon,
                          '<MISSING>'
                        ])
                    count=count+1
                    logger.info(count)
        else:
            pass


    time.sleep(3)
    driver.quit()
    driver2.quit()
    return data


def scrape():
    data = fetch_data()
    write_output(data)

scrape()

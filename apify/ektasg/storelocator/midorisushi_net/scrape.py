import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('midorisushi_net')




options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
#driver = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver = webdriver.Chrome("chromedriver", options=options)

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url" , "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def parse_geo(url):
    a=re.findall(r'\&sll=(-?[\d\.]*,(--?[\d\.]*))',url)[0]
    lat = a[0].split(",")[0]
    lon = a[0].split(",")[1]
    return lat, lon


def fetch_data():
    # Your scraper here
    count=0
    data=[]
    driver.get("http://midorisushi.net/locations.html?20190601")
    page_url = "http://midorisushi.net/locations.html?20190601"
    time.sleep(10)

    hours_of_op = driver.find_element_by_css_selector('div.time').text.replace("\n", " ")

    driver.switch_to.frame(0)
    time.sleep(3)

    location_name = [];    phone = [];    lat = [];    lng = [];    street_addr = [];    zipcode = [];    state = [];    city = []

    loc_names = driver.find_elements_by_css_selector('h1')
    geomaps = driver.find_elements_by_xpath("//a[contains(@href, 'maps.google.com')]")
    total_info = driver.find_element_by_css_selector('td.menu').text.splitlines()

    for i in range(0,len(total_info)):
        if total_info[i] == 'click here for map':
            list1 = total_info[0:i]
            list2 = total_info[i+3 : -1]
            break;

    street_addr.append(list1[1])
    street_addr.append(list2[1])
    phone.append(list1[4])
    phone.append(list2[4])
    zipcode.append(list1[2].split(" ")[-1])
    zipcode.append(list2[2].split(" ")[-1])
    state.append(list1[2].split(" ")[-2])
    state.append(list2[2].split(" ")[-2])
    city.append(list1[2].split(",")[0])
    city.append(list2[2].split(",")[0])

    for i in range(0,len(loc_names)):
        location_name.append(loc_names[i].text)
        lati,lngi = parse_geo(geomaps[i].get_attribute('href'))
        lat.append(lati)
        lng.append(lngi)

    for i in range(0,len(location_name)):
        data.append([
                'http://midorisushi.net/',
                page_url,
                location_name[i],
                street_addr[i],
                city[i],
                state[i],
                zipcode[i],
                'US',
                '<MISSING>',
                phone[i],
                '<MISSING>',
                lat[i],
                lng[i],
                hours_of_op
            ])
        count = count + 1
        logger.info(count)


    time.sleep(3)
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
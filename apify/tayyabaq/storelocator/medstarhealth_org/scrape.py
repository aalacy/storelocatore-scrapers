import csv,requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re, time
from bs4 import BeautifulSoup
from lxml import html
import usaddress

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome('chromedriver', chrome_options=options)
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            if row:
                writer.writerow(row)

def fetch_data():
    data=[]; location_name=[];address_stores=[]; city=[];street_address=[]; zipcode=[]; state=[]; latitude=[]; longitude=[]; hours_of_operation=[]; phone=[]
    #Driver
    driver = get_driver()
    url="https://www.medstarhealth.org/mhs/our-locations/"
    driver.get(url)
    time.sleep(5)
    r = requests.get(url)
    tree = html.fromstring(r.content)
    soup = BeautifulSoup(r.content, 'html.parser')
    script = soup.findAll("script")
    for n in range(0,len(script)):
        if 'lng' in script[n].text:
            latitude=re.findall(r'LatLng\((-?[\d\.]*),', script[n].text)
            longitude=re.findall(r'(--?[\d\.]*)\)', script[n].text)
    pages=driver.find_elements_by_xpath("//a[contains(@href,'javascript:wpgmp_filter_locations')]")
    last_page=(pages[-2].text)
    for n in range(0,20):
        location = driver.find_elements_by_xpath("//a[contains(@href,'javascript:open_current_location')]")
        location_text = [location[n].text for n in range(0,len(location))]
        stores = driver.find_elements_by_class_name('wpgmp_locations_content')
        for n in range(0,len(location)):
            location_name.append(location_text[n])
            try:
                tagged=usaddress.tag(stores[n].text)[0]
                try:
                    street_address.append(tagged['AddressNumber']+' '+tagged['StreetName']+' '+tagged['StreetNamePostType']+', '+tagged['OccupancyType']+' '+tagged['OccupancyIdentifier'])
                except:
                    street_address.append(tagged['AddressNumber']+' '+tagged['StreetName']+' '+tagged['StreetNamePostType'])
                city.append(tagged['PlaceName'])
                zipcode.append(tagged['ZipCode'])
                state.append(tagged['StateName'])
            except:
                a=stores[n].text.split(",")[:-1]
                street_address.append(','.join(a))
                try:
                    tagged=usaddress.tag(stores[n].text.split(",")[-2])[0]
                    city.append(tagged['PlaceName'])
                except:
                    tagged=usaddress.tag(stores[n].text.split(",")[-1])[0]
                    city.append('<INACCESSIBLE>')
                try:
                    zipcode.append(tagged['ZipCode'])
                except:
                    zipcode.append('<MISSING>')
                try:
                    state.append(tagged['StateName'])
                except:
                    state.append(stores[n].text.split(",")[-2])
        try:
            driver.find_element_by_link_text('Next').click()
            time.sleep(6)
        except:
                   break
    for n in range(0,len(location_name)):
        data.append([
            'https://www.medstarhealth.org',
            location_name[n],
            street_address[n],
            city[n],
            state[n],
            zipcode[n],
            'US',
            '<MISSING>',
            '<INACCESSIBLE>',
            '<MISSING>',
            latitude[n],
            longitude[n],
            '<MISSING>'
        ])
    return data

def scrape():
    data = fetch_data()
    write_output(data)
scrape()

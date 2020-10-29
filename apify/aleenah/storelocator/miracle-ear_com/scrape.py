import csv
from sgselenium import SgSelenium
import re
import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('miracle-ear_com')



driver = SgSelenium().chrome()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def parse_geo(url):
    lon = re.findall(r'destination=[-?\d\.]*\,([-?\d\.]*)', url)[0]
    lat = re.findall(r'destination=(-?[\d\.]*)', url)[0]
    return lat, lon

def fetch_data():
    # Your scraper here
    locs = []
    street = []
    states=[]
    cities = []
    countries=[]
    phones = []
    zips = []
    long = []
    lat = []
    timing = []
    types=[]
    page_url=[]
    state_links=[]

    url="https://www.miracle-ear.com/stores-near-me"
    driver.get(url)
    div=driver.find_elements_by_class_name("E32-text-container-100")[0]
    div=div.find_element_by_class_name("row")
    ast=div.find_elements_by_tag_name("a")
    #driver.close()

    for a in ast:
        state_links.append(a.get_attribute("href"))

    for sl in state_links:
        driver.get(sl) #state page
        divss=driver.find_elements_by_class_name("metro-store-details")

        for div in divss:
            url=div.find_element_by_tag_name("a").get_attribute("href")
            page_url.append(url)
    logger.info(len(page_url))
    i=1
    for url in page_url:
            logger.info(i)
            i+=1
            driver.get(url)
            divs=driver.find_element_by_tag_name("main")
            divs=divs.find_element_by_xpath('//div[@class="container-fluid store-info-main"]')
            locs.append(divs.find_element_by_xpath('//div[@class="row store-bar"]').text)
            addr = divs.find_element_by_xpath('//div[@class="detail-address"]').text
            if addr !="":
                addr=addr.split("\n")
                street.append(addr[0])
                addr=addr[1].split(",")
                cities.append(addr[0])
                addr=addr[1].strip().split(" ")
                states.append(addr[0])
                zips.append(addr[1])
            else: 
                street.append("<MISSING>")
                states.append("<MISSING>")
                zips.append("<MISSING>")
                cities.append("<MISSING>")
            p = divs.find_element_by_xpath('//div[@class="detail-shop"]').find_element_by_tag_name("p").text
            try:
                phones.append(re.findall(r'([0-9\-\(\) ]+)', p)[0].strip())
            except:
                phones.append("<MISSING>")
            try:
                divs.find_element_by_xpath('//i[@class="am-icon-jade-arrow-right am-icon"]').click()
                days=divs.find_element_by_xpath('//div[@class="ds-list-week"]').find_elements_by_class_name("ds-single-day")
                tim=""
                for day in days:
                    tim+=day.text + " "
                tim=tim.strip().replace("\n"," ")
                if tim=="":
                    tim="<MISSING>"
                timing.append(tim)

            except:
                timing.append("<MISSING>")
            try:
                cord = divs.find_element_by_xpath('//div[@class="detail-link"]').find_element_by_tag_name("a").get_attribute("href")
                la,lo=parse_geo(cord)
                lat.append(la)
                long.append(lo)
            except:
                lat.append("<MISSING>")
                long.append("<MISSING>")

    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://www.miracle-ear.com")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append("US")
        row.append("<MISSING>")  # store #
        row.append(phones[i])  # phone
        row.append("<MISSING>")  # type
        row.append(lat[i])  # lat
        row.append(long[i])  # long
        row.append(timing[i])  # timing
        row.append(page_url[i])  # page url

        all.append(row)
    return (all)

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

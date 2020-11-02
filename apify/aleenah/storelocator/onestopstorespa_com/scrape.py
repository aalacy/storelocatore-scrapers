import csv
from sgselenium import SgSelenium
import re
import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('onestopstorespa_com')



driver = SgSelenium().chrome()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    all=[]
    driver.get('https://www.onestopstorespa.com/our-locations')
    time.sleep(5)
    iframes=driver.find_elements_by_tag_name('iframe')

    logger.info(len(iframes))
    #
    for frame in iframes:
        #if frame.get_attribute('aria-label')=="Google Maps":
        driver.switch_to.frame(frame)
            #logger.info(str(frame))

        links=driver.find_elements_by_tag_name('a')
        if len(links)==0:
            driver.switch_to.default_content()
            continue

        addr=re.findall(r'destination=(.*)',links[0].get_attribute('href'))[0].replace('%20',' ').split(',')
        logger.info(addr)
        driver.switch_to.default_content()
        del addr[-1]
        zip=re.findall(r'[\d]{5}',addr[-1])
        if len(zip)==0:
            state=addr[-1].strip()
            zip="<MISSING>"

        else:
            zip=zip[0]
            state=addr[-1].replace(zip,'').strip()
        del addr[-1]
        city=addr[-1].strip()
        del addr[-1]
        street= ', '.join(addr)
        loc=city

        all.append([
            "https://www.onestopstorespa.com/our-locations",
            loc,
            street,
            city,
            state,
            zip,
            "US",
            "<MISSING>",  # store #
            "<MISSING>",  # phone
            "<MISSING>",  # type
            "<MISSING>",  # lat
            "<MISSING>",  # long
            "<MISSING>",  # timing
            "https://www.onestopstorespa.com/our-locations"])


    return all


def scrape():
    data = fetch_data()
    write_output(data)

scrape()

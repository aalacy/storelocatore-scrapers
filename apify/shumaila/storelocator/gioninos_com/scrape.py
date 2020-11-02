import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('gioninos_com')




def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--disable-notifications")
    return webdriver.Chrome('chromedriver', chrome_options=options)
    #return webdriver.Chrome('/Users/Dell/local/chromedriver', chrome_options=options)


def fetch_data():
    # Your scraper here
    data = []
    p = 1
    url = 'https://www.gioninos.com/Locations'
    driver1 = get_driver()
    driver1.get(url)
    time.sleep(2)
    soup = BeautifulSoup(driver1.page_source, "html.parser")
    driver1.quit()
    divlist = soup.findAll('a',{'class': 'Muli-Regular legal-link'})
    logger.info(len(divlist))
    pattern = re.compile(r'\s\s+')
    p = 1
    for link in divlist:
        link = "https://www.gioninos.com" + link['href']
        logger.info(link)
        driver = get_driver()
        driver.get(link)
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        #divlist = soup.findAll('script')
        script = str(soup)
        #logger.info(script)
        start = script.find('"LocationId"')
        start = script.find(':', start) + 1
        end = script.find(',', start)
        store = script[start:end]

        start = script.find('"Description"')
        start = script.find(':', start) + 2
        end = script.find('"', start)
        title = script[start:end]

        start = script.find('"Address1"')
        start = script.find(':', start) + 2
        end = script.find('"', start)
        street = script[start:end]

        start = script.find('"City"')
        start = script.find(':', start) + 2
        end = script.find('"', start)
        city = script[start:end]

        start = script.find('"State"')
        start = script.find(':', start) + 2
        end = script.find('"', start)
        state = script[start:end]

        start = script.find('"Zip"')
        start = script.find(':', start) + 2
        end = script.find('"', start)
        pcode = script[start:end]

        start = script.find('"Phone"')
        start = script.find(':', start) + 2
        end = script.find('"', start)
        phone = script[start:end]

        start = script.find('"Latitude"')
        start = script.find(':', start) + 1
        end = script.find(',', start)
        lat = script[start:end]

        start = script.find('"Longitude"')
        start = script.find(':', start) + 1
        end = script.find(',', start)
        longt = script[start:end]

        divsr = soup.findAll('div', {'class': 'col-xs-4'})
        divsl = soup.findAll('div', {'class': 'col-xs-8'})
        #divlist = divlist[1]
        hours = ""

        for n in range(0,len(divsr)):
            right = divsr[n].text
            right = right.replace("\n", "")
            right = re.sub(pattern,"",right)
            left = divsl[n].text
            left = left.replace("\n", "")
            left = re.sub(pattern,"",left)
            hours = hours + " " + right + left + "|"

        hours = hours[1:len(hours)-1]
        if len(phone) < 6:
            phone = "<MISSING>"

        #logger.info(store)
        #logger.info(title)
        #logger.info(street)
        #logger.info(city)
        #logger.info(state)
        #logger.info(pcode)
        #logger.info(phone)
        #logger.info(lat)
        #logger.info(longt)
        #logger.info(hours)
        #logger.info(p)
        #logger.info("...........................")
        p += 1
        data.append([
            'https://www.gioninos.com/',
            link,
            title,
            street,
            city,
            state,
            pcode,
            'US',
            store,
            phone,
            "<MISSING>",
            lat,
            longt,
            hours
        ])


    return data


def scrape():
        data = fetch_data()
        write_output(data)

scrape()

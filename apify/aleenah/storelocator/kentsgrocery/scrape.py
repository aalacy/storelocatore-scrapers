import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
from sgselenium import SgSelenium
import time

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


session = SgRequests()
driver = SgSelenium().chrome()

all=[]
def fetch_data():
    # Your scraper here

    res=session.get("https://kentsgrocery.com/")
    soup = BeautifulSoup(res.text, 'html.parser')
    lis = soup.find('ul', {'class': 'dropdown-menu'}).find_all('li')

    for li in lis:
        url="https://kentsgrocery.com"+li.find('a').get('href')

        driver.get(url)

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        loc = soup.find('span', {'id': 'theStoreName'}).text.strip()
        print(soup.find('div', {'id': 'mapContain'}).find('iframe').get('src'))
        long,lat=re.findall(r'!2d(-?[\d\.]+)!3d(-?[\d\.]+)',soup.find('div', {'id': 'mapContain'}).find('iframe').get('src'))[0]
        #print(soup.find('div', {'id': 'storeInfoContain'}).text)
        try:
            phone,street,state,zip,tim=re.findall(r'Phone Number(.*)Fax Number.*Store Address(.*), (.*) (.*)(Pharmacy Hours.*)Email',soup.find('div', {'id': 'storeInfoContain'}).text)[0]
        except:
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            phone, street, state, zip,tim  = re.findall(r'Phone Number(.*)Fax Number.*Store Address(.*), (.*) (.*)(Pharmacy Hours.*)Email',soup.find('div', {'id': 'storeInfoContain'}).text)[0]
            #print(soup.find('div', {'id': 'storeHours'}).text)
            #tim=soup.find('div', {'id': 'storeHours'}).text
        tim=tim.replace('Hours','Hours ').replace('PM','PM ')
        city=loc.replace('Kent\'s','').strip()
        street=street.replace(city,'')
        #
        #print(city,street,state,zip,tim)

        all.append([
            "https://kentsgrocery.com",
            loc,
            street,
            city,
            state.strip(),
            zip,
            "US",
            "<MISSING>",  # store #
            phone,  # phone
            "<MISSING>",  # type
            lat,  # lat
            long,  # long
            tim,  # timing
            url])

    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

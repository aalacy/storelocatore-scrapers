import csv
import re
from bs4 import BeautifulSoup
from sgselenium import SgSelenium
import time

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

driver = SgSelenium().chrome()

def fetch_data():
    # Your scraper here
    locs = []
    street = []
    states=[]
    cities = []
    types=[]
    phones = []
    zips = []
    long = []
    lat = []
    timing = []
    ids=[]
    page_url=[]

    #res=requests.get("https://stevibs.com/locations-all/")
    driver.get("https://stevibs.com/locations-all/")
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    divs=soup.find('div',{'class':'all-locations-wrapper1'})
    divs=divs.find_all('div',{'class':'location-card'})

    for div in divs:
        locs.append(div.find('a',{'class':'location-link'}).text.strip())
        acs=div.find_all('span',{'class':'location-card-address'})
        street.append(acs[0].text.strip())
        addr=acs[1].text
        addr=addr.split(",")
        cities.append(addr[0].strip())
        states.append(re.findall(r'[A-Z]{2}',addr[1])[0])
        num = re.findall(r'[0-9\-\)\( ]+',addr[1].strip())[0].strip()
        z=re.findall(r'[0-9]{5}',num)[0]
        zips.append(z)
        phones.append(re.sub(z,"",num))
        url=div.find('a',{'class':'button alt'}).get("href")
        driver.get(url)
        page_url.append(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        time.sleep(0.1)
        coord = soup.find('a', {'class':'contact-item'}).get('href')
        try:
            lat.append(re.findall('destination=([-?\d\.]*)',coord)[0])
        except:
            lat.append("<MISSING>")
        try:
            long.append(re.findall('destination=[-?\d\.]*\,([-?\d\.]*)',coord)[0])
        except:
            long.append("<MISSING>")
        timing.append(soup.find('span', {'id':'single-sidebar'}).find_all('p')[2].text)

    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://stevibs.com")
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
        row.append( page_url[i])  # page url

        all.append(row)
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

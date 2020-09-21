import csv
import time
from sgselenium import SgSelenium
from bs4 import BeautifulSoup

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

    all=[]
    driver.get("http://greshampetroleum.com/locations")
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    #print(soup)
    locs = soup.find_all('div',{'class':'storepoint-name'})
    addrs=soup.find_all('div',{'class':'storepoint-address'})
    phones=soup.find_all('a',{'class':'storepoint-sidebar-phone'})


    print(len(locs))

    for i in range(len(locs)):
        phone =phones[i].text
        addr = addrs[i].text
        addr = addr.split(',')
        loc=locs[i].text

        sz = addr[-1].strip().split(" ")
        state = sz[0]
        zip = sz[1].split("-")[0]

        addr=addr[0]
        city=loc.split('-')[-1].strip()
        street=addr.replace('&nbsp;','').replace(city,'').strip()


        all.append([
            "http://greshampetroleum.com",
            loc,
            street,
            city,
            state,
            zip,
            "US",
            "<MISSING>",  # store #
            phone,  # phone
            "<MISSING>",  # type
            "<MISSING>",  # lat
            "<MISSING>",  # long
            "<MISSING>",  # timing
            "http://greshampetroleum.com/locations"])

    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

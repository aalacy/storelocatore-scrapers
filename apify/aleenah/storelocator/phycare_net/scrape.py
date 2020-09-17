import csv
from sgselenium import SgSelenium
from bs4 import BeautifulSoup
from sgrequests import SgRequests
import re


driver = SgSelenium().chrome()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

session = SgRequests()

def fetch_data():
    # Your scraper here

    driver.get("https://www.urgentteam.com/locations/?address=&lat=&lng=&brand=physicians-care")
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    stores=soup.find_all('circle')
    #stores=driver.find_elements_by_tag_name('circle')
    print(len(stores))


    all = []
    tims=soup.find_all('div',{'class':'m-location__hours m-location-hours'})
    for store in stores:
        addr= store.get('address').split('<br>')
        street=addr[0].strip().strip(',')
        addr=addr[1].split(',')
        city=addr[0]
        addr=addr[1].strip().split(' ')
        zip=addr[-1]
        del addr[-1]
        state=' '.join(addr)
        tim=tims[stores.index(store)].text.replace('M-F','Mon-Friday')
        driver.get(store.get('url'))
        print(store.get('url'))
        soup= BeautifulSoup(driver.page_source, 'html.parser')
        #print(soup)
        lat,long=re.findall(r'"latitude":(.*),"longitude":([^}]+)',str(soup))[0]


        row = []
        row.append("https://www.urgentteam.com/locations/?address=&lat=&lng=&brand=physicians-care")
        row.append(store.get('name'))
        row.append(street)
        row.append(city)
        row.append(state)
        row.append(zip)
        row.append("US")
        row.append("<MISSING>")  # store #
        row.append(store.get('phone'))  # phone
        row.append("<MISSING>")  # type
        row.append(lat)  # lat
        row.append(long)  # long
        row.append(tim)  # timing
        row.append(store.get('url'))  # page url

        all.append(row)
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

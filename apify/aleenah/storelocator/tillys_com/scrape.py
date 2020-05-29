import csv
from sgselenium import SgSelenium
import re
from bs4 import BeautifulSoup

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
    lon = re.findall(r'll=[-?\d\.]*\,([-?\d\.]*)', url)[0]
    lat = re.findall(r'll=(-?[\d\.]*)', url)[0]
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
    ids=[]


    driver.get("https://www.tillys.com/stores")
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    script = soup.find('script', {'type': 'application/json'})
    datas = script.text.split("},{")
    for tex in datas:
        l=re.findall(r'.*"name":"([^"]*)"', tex)[0]
        if "Coming Soon!" in l:
            continue
        locs.append(l)
        street.append(re.findall(r'.*"address1":"([^"]*)"', tex)[0])
        cities.append(re.findall(r'.*"city":"([^"]*)"', tex)[0])
        lat.append(re.findall(r'.*"latitude":(-?[\d\.]*)', tex)[0].strip())
        long.append(re.findall(r'.*"longitude":(-?[\d\.]*)', tex)[0].strip())
        try:
            phones.append(re.findall(r'.*"phone":"([^"]*)"', tex)[0].strip())
        except:
            phones.append("<MISSING>")
        zips.append(re.findall(r'.*"postalCode":"([^"]*)"', tex)[0].strip())
        states.append(re.findall(r'.*"stateCode":"([^"]*)"', tex)[0].strip())
        ids.append(re.findall(r'.*"id":"([^"]*)"', tex)[0])
        timing.append("<MISSING>")



    driver.get("https://www.tillys.com/store-list")
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    divs= soup.find_all('div',{'class':'col-6 col-sm-3 sl__stores-list_item'})

    i=1
    for div in divs:
        span = div.find('span', {'itemprop': 'branchCode'})
        time = div.find('time', class_="visually-hidden")
        try:

            timing[ids.index(span.text)]=time.text.replace("\n"," ").strip().strip(">")
        except:
            k=0




    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://www.tillys.com")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append("US")
        row.append(ids[i])  # store #
        row.append(phones[i])  # phone
        row.append("<MISSING>")  # type
        row.append(lat[i])  # lat
        row.append(long[i])  # long
        row.append(timing[i])#timing
        row.append("https://www.tillys.com/stores")#page url

        all.append(row)
    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

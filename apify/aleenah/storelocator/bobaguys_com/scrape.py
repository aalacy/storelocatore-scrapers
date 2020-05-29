import csv
import re
from bs4 import BeautifulSoup
import requests

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

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
    urls=["http://www.bobaguys.com/locations","http://www.bobaguys.com/los-angeles","http://www.bobaguys.com/new-york-locations"]
    for url in urls:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        divs = soup.find_all('div', {'class': 'row sqs-row'})
        del divs[0]
        del divs[0]
        del divs[-1]
        del divs[-1]
        for div in divs:
            tdivs = div.find_all('div', {'class': 'col sqs-col-6 span-6'})
            lc=tdivs[0].find("div").get("data-block-json")
            lat.append(re.findall(r'"mapLat":(-?[\d\.]*)',lc)[0])
            long.append(re.findall(r'"mapLng":(-?[\d\.]*)',lc)[0])
            locs.append(re.findall(r'"addressTitle":"([^"]*)"', lc)[0])
            street.append(re.findall(r'"addressLine1":"([^"]*)"', lc)[0])
            addr=re.findall(r'"addressLine2":"([^"]*)"', lc)[0].replace(",","")
            if addr=="":
                addr=re.findall(r'St\.(.*)Monday',tdivs[1].text)[0]
            print(addr)
            z=addr.split(" ")[-1].strip()
            s=addr.split(" ")[-2].strip()
            zips.append(z)

            states.append(s.upper())
            cities.append(addr.replace(z,"").replace(s,"").strip())
            timing.append(re.findall(r'Monday.*pm|Monday.*PM',tdivs[1].text)[0].replace('\xa0',""))
            page_url.append(url)

    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("http://www.bobaguys.com")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append("US")
        row.append("<MISSING>")  # store #
        row.append("<MISSING>")  # phone
        row.append("<MISSING>")  # type
        row.append(lat[i])  # lat
        row.append(long[i])  # long
        row.append(timing[i])  # timing
        row.append(page_url[i])  # page url

        all.append(row)
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

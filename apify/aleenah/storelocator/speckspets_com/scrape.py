import csv
import re
from bs4 import BeautifulSoup
import requests
import time

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
    urls=[]
    res=requests.get("https://www.speckspets.com/Our-Locations_ep_50-1.html")
    soup = BeautifulSoup(res.text, 'html.parser')
    tim=soup.find('div',{'class':'content'}).find('p').text.strip()
    tds=soup.find('table',{'class':'location-table'}).find_all('td')
    del tds[-1]
    del tds[-1]
    for td in tds:
        ps=td.find_all('p')
        locs.append(ps[0].text)
        add=ps[1].text.split("\n")
        phones.append(add[2].strip())
        addr=add[0].split(",")
        street.append(add[1].strip()+", "+addr[0])
        cities.append(addr[1].strip())
        addr=addr[2].strip().split(" ")
        states.append(addr[0])
        zips.append(addr[1])
        timing.append(tim)
        href=ps[1].find('a').get("href")
        lat.append(re.findall(r'!3d(-?[\d\.]*)',href)[0])
        long.append(re.findall(r'!4d(-?[\d\.]*)',href)[0])

    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://www.speckspets.com")
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
        row.append("https://www.speckspets.com/Our-Locations_ep_50-1.html")  # page url

        all.append(row)
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

import csv
import re
from bs4 import BeautifulSoup
from sgrequests import SgRequests

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

    res=session.get("https://fastraccafe.com/locations/")
    soup = BeautifulSoup(res.text, 'html.parser')
    trs= soup.find('table',{'class',"locationsTable"}).find('tbody').find_all('tr')
    print(len(trs))
    for tr in trs:
        check= tr.find('td',{'class':'store-links'}).text.lower()
        if "coming soon" in check:
            continue
        locs.append(tr.find('td',{'class':'store'}).find('h3').text.strip())
        span = tr.find('td',{'class':'store'}).find('span')
        lat.append(span.get('data-lat').strip())
        long.append(span.get('data-lng').strip())
        ps=tr.find('td',{'class':'store'}).find_all('p')
        street.append(ps[0].text.strip())
        addr=ps[1].text.split(",")
        cities.append(addr[0].strip())
        #print(addr)
        addr=addr[1].strip().split("\n")
        states.append(addr[0])
        zips.append(addr[1])
        info= tr.find('td',{'class':'store-info'}).text.split("\n")
        tim=""
        for i in info:
            if "hours" in i.lower() or "drive thru" in i.lower():
                tim+=i+" "
        timing.append(tim)
        phones.append(tr.find('td',{'class':'store-tel'}).text.strip())
        a=tr.find('td',{'class':'store-links'}).find_all('a')
        if len(a)<2:
            ids.append("<MISSING>")
        else:
            id=re.findall(r'SiteID=([\d]+)',a[1].get('href'))
            if id==[]:
                ids.append("<MISSING>")
            else:
                ids.append(id[0])
    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://fastraccafe.com")
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
        row.append(timing[i])  # timing
        row.append("https://fastraccafe.com/locations/")  # page url

        all.append(row)
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

import csv
import re
from bs4 import BeautifulSoup
import requests
from pyzipcode import ZipCodeDatabase

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

    res = requests.get("https://www.gretchenscottdesigns.com")
    soup = BeautifulSoup(res.text, 'html.parser')
    #print(soup)
    sa = soup.find('div', {'class': 'f_block f_block3'}).find_all("a")

    for a in sa:
        page_url.append(a.get("href"))
        locs.append(a.text)

    for url in page_url:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        # print(soup)
        sa = soup.find('div', {'class': 'grid12-7'}).find_all("h3")
        tex=""
        for a in sa:
            tex+=a.text

        addr= re.findall(r'(.*[0-9]{5})',tex)[0]
        tex = tex.replace(addr, "")
        ad = addr.split(",")[-1]
        addr=addr.replace(ad,"")
        z=re.findall(r'([0-9]{5})',ad)[0]
        states.append(ad.replace(z,"").strip())
        zips.append(z)

        zcdb = ZipCodeDatabase()
        z = zcdb[z]
        c=z.place
        addr = addr.replace(",", "").strip()
        if c in addr:
            cities.append(c)
            street.append(addr.replace(c,""))
        else:
            c=addr.split(" ")[-1]
            cities.append(c)
            street.append(addr.replace(c,""))

        p = re.findall(r'([\+ \)\(0-9\-]+)',tex)
        if p ==[]:
            phones.append("<MISSING>")
        else:
            phones.append(p[0])
            tex=tex.replace(p[0],"")
        timing.append(tex)

    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://www.gretchenscottdesigns.com")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append("US")
        row.append("<MISSING>")  # store #
        row.append(phones[i])  # phone
        row.append("<MISSING>")  # type
        row.append("<MISSING>")  # lat
        row.append("<MISSING>")  # long
        row.append(timing[i])  # timing
        row.append(page_url[i])  # page url

        all.append(row)
    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

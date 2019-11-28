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

    res=requests.get("https://www.aloyoga.com/pages/stores")
    soup = BeautifulSoup(res.text, 'html.parser')
    ps = soup.find_all('p', {'class': 'subtitle m-b-1'})

    for p in ps:
        l=p.text.strip()

        if "STORE " not in l:
            l=l.replace("STORE","STORE ")
        if  "FLAGSHIP" in l:
            types.append("FLAGSHIP")
            if " FLAGSHIP" not in l:
               l=l.replace("FLAGSHIP"," FLAGSHIP")
        else:
            types.append("<MISSING>")
        #print(l)
        locs.append(l)
    divs = soup.find_all('div',{'class','contact-address p-t-0 store-address'})
    for div in divs:
        cols = div.find_all('div', {'class': 'col-md-4 col-12'})
        addr=re.sub("[ ]+"," ",cols[0].text.replace("ADDRESS","")).strip().replace("\n","").replace(",","")
        #print(addr)
        z= re.findall(r'[0-9]{5}',addr)[-1]
        addr=addr.replace(z,"").strip()
        zips.append(z)
        s= re.findall(r'[A-Z]{2}',addr)[-1]
        addr=addr.replace(s,"").strip()
        states.append(s)
        zcdb =ZipCodeDatabase()
        z=zcdb[z]
        c=z.place
        if c in addr:
            cities.append(c)
            street.append(addr.replace(c,"").strip())
        else:
            c = addr.split(" ")
            c= c[-2]+" "+c[-1]
            cities.append(c)
            street.append(addr.replace(c, "").strip())
        phones.append(cols[1].text.replace("PHONE","").strip())
        timing.append(cols[2].text.replace("HOURS","").replace("\n"," ").strip())

    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://www.aloyoga.com")
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
        row.append("https://www.aloyoga.com/pages/stores")  # page url

        all.append(row)
    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
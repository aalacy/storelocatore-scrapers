import csv
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
    urls=[]
    res=requests.get("https://www.parkland.ca/en/contact-us")
    soup = BeautifulSoup(res.text, 'html.parser')
    cols=soup.find_all('div',{'class':'columns'})
    del cols[0]
    
    for col in cols:
        divs=col.find_all('div')
        
        for div in divs:

            tex=div.text
            if tex=="":
                continue
            tex=tex.strip().replace("\xa0", " ").split("\n")
            locs.append(tex[0])
            street.append(tex[1])
            addr=tex[2].split(",")
            cities.append(addr[0])
            addr=addr[1].strip().split("  ")
            print(addr)
            states.append(addr[0])
            zips.append(addr[1])
            try:
                phones.append(tex[3].strip())
            except:
                phones.append("<MISSING>")

            print(tex)
    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://www.parkland.ca/en/contact-us")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append("CA")
        row.append("<MISSING>")  # store #
        row.append(phones[i])  # phone
        row.append("<MISSING>")  # type
        row.append("<MISSING>")  # lat
        row.append("<MISSING>")  # long
        row.append("<MISSING>")  # timing
        row.append("https://www.parkland.ca/en/contact-us")  # page url

        all.append(row)
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

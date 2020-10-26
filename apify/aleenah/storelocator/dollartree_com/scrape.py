import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json

import os

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

session = SgRequests()
"""proxy_password = os.environ["PROXY_PASSWORD"]
proxy_url = "http://auto:{}@proxy.apify.com:8000/".format(proxy_password)
proxies = {
        'http': proxy_url,
        'https': proxy_url
    }
"""

def fetch_data():
    # Your scraper here

    page_url = []

    res=session.get("https://www.dollartree.com/locations/")
    soup = BeautifulSoup(res.text, 'html.parser')
    sls = soup.find('div', {'class': 'content_area'}).find_all('a')
    print("sls: ",len(sls))
    count=0
    for sl in sls:
        res = session.get(sl.get('href'))
        #print(sl.get('href'))
        soup = BeautifulSoup(res.text, 'html.parser')
        cls = soup.find('div', {'class': 'content_area'}).find_all('a')
        #print("cls",len(cls))
        for cl in cls:
            res = session.get(cl.get('href'))
            #print(cl.get('href'))

            soup = BeautifulSoup(res.text, 'html.parser')
            #print(soup)
            pls = soup.find_all('div', {'itemprop': 'address'})
            #print("pls: ",len(pls))

            for p in pls:
                p=p.find('a')
                page_url.append(p.get('href'))
                count+=1
            #print(len(page_url))
    print(count)
    key_set=set([])
    all =[]
    for url in page_url:
        #print(url)
        res = session.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        data = soup.find_all('script', {'type': 'application/ld+json'})[1].contents
        js=json.loads("".join(data))
        addr=js["address"]
        timl=js["openingHoursSpecification"]
        tim=""
        for l in timl:
            tim+= l["dayOfWeek"][0]+": "+l["opens"]+" - "+l["closes"]+" "
        #print(url)
        #print(js)
        p=js["telephone"]
        if p.strip()=="":
            p="<MISSING>"
        key=addr["streetAddress"]+addr["addressLocality"]+addr["addressRegion"]+addr["postalCode"]
        if key in key_set:
            continue
        key_set.add(key)
        all.append([
        "https://www.dollartree.com",
        js["containedIn"],
        addr["streetAddress"],
        addr["addressLocality"],
        addr["addressRegion"],
        addr["postalCode"].split("-")[0],
        addr["addressCountry"],
        js["@id"],  # store #
        p.strip(),  # phone
        js["@type"],  # type
        js["geo"]["latitude"],  # lat
        js["geo"]["longitude"],  # long
        tim.strip(),  # timing
        url])

    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

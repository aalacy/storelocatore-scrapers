import csv
import re
from bs4 import BeautifulSoup
import requests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('commoncentsstores_com')



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

    res=requests.get("http://www.commoncentsstores.com/locations.html")
    #logger.info(res)
    soup = BeautifulSoup(res.text, 'html.parser')
    #logger.info(soup)
    divs = soup.find_all('div', {'class': 'col-sm-4 col-xs-11 bottom25'})
    for div in divs:
        page_url.append("http://www.commoncentsstores.com"+div.find('a').get('href'))

    for url in page_url:
        logger.info(url)
        
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        div = soup.find('div', {'class': 'map bottom30'})
        try:
            la = re.findall(r':\[\[(-?[\d\.]+),',div.text)[0]
        except:
            la="<MISSING>"
        try:
            lo = re.findall(r':\[\[-?[\d\.]+,(-?[\d\.]+),', div.text)[0]
        except:
            lo = "<MISSING>"

        lat.append(la)
        long.append(lo)
        div = soup.find('div', {'class': 'col-sm-4 col-sm-offset-1 col-xs-12'}).find('div', {'class': 'bottom30'})
        #logger.info(div.text)
        tex=div.text.strip()
        l = tex.split("\n")[0]
        locs.append(l)
        tex=tex.replace(l,"").strip()
        #logger.info(tex)
        ty=re.findall(r'(.*)Address',tex,re.DOTALL)[0].strip()
        if ty=="":
            ty="<MISSING>"
        types.append(ty)
        ids.append(re.findall(r'locations/([\d]+)\-',url)[0])
        addr = re.findall(r'Address(.*)Phone', tex, re.DOTALL)
        if addr==[]:
            addr=re.findall(r'Address(.*[\d]{5})',tex,re.DOTALL)
        addr=addr[0].strip()
        addr=addr.split("\n")
        street.append(addr[0])
        addr=addr[1].split(",")
        cities.append(addr[0])
        addr=addr[1].strip().split(" ")
        states.append(addr[0])
        zips.append(addr[1])
        #logger.info(tex)
        ph=re.findall(r'Phone\n([\(\)\- 0-9]+)Phone',tex,re.DOTALL)
        if ph!=[]:
            phones.append(ph[0].strip())

        else:
            phones.append("<MISSING>")

    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("http://www.commoncentsstores.com")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append("US")
        row.append(ids[i])  # store #
        row.append(phones[i])  # phone
        row.append(types[i])  # type
        row.append(lat[i])  # lat
        row.append(long[i])  # long
        row.append("<MISSING>")  # timing
        row.append(page_url[i])  # page url
        all.append(row)
    return all
def scrape():
    data = fetch_data()
    write_output(data)
scrape()

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

    res=session.get("https://www.finewineandgoodspirits.com/webapp/wcs/stores/servlet/FindStoreView?storeId=10051&langId=-1&catalogId=10051&pageNum=1&listSize=1000&category=&city=&zip_code=&county=All+Stores&storeNO=")
    soup = BeautifulSoup(res.text, 'html.parser')

    divs= soup.find_all('div', {'class': 'tabContentRow'})
    for div in divs:
        ids.append(div.find('span', {'class': 'boldMaroonText'}).text.strip())
        lat.append(div.find('input', {'name': 'latitude'}).get('value'))
        long.append(div.find('input', {'name': 'longitude'}).get('value'))
        addr=div.find('input', {'name': 'googleAddress'}).get('value')
        add=addr.split(",")
        s=add[-1].strip()
        del add[-1]
        c=add[-1].strip()
        del add[-1]
        states.append(s)
        cities.append(c)

        street.append(", ".join(add))
        ph=div.find('input', {'name': 'storePhone'}).get('value').strip()
        if ph=="":
            phones.append("<MISSING>")
        else:
            phones.append(ph)
        addr=div.find('input', {'name': 'displayAddress'}).get('value').split("<br>")
        z=re.findall(r'([0-9]{5})',addr[-3])
        #print(addr[-3])
        #print(z)
        if z==[]:
            zips.append("<MISSING>")
        else:
            zips.append(z[0])
        timing.append(div.find('div', {'class': 'columnHoursOfOprn'}).text.strip().replace('\n\n\n',', ').replace('\n',": ").strip(","))
        locs.append(addr[0].strip())
        ty=div.find('div', {'class': 'columnTypeOfStore'}).text.strip()
        t=re.findall(r'[a-zA-Z ]+',ty)

        if t!=[]:
            types.append(ty)
        else:
            types.append("<MISSING>")
    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://www.finewineandgoodspirits.com")
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
        row.append(timing[i])  # timing
        row.append("https://www.finewineandgoodspirits.com/webapp/wcs/stores/servlet/FindStoreView?storeId=10051&langId=-1&catalogId=10051&pageNum=1&listSize=1000&category=&city=&zip_code=&county=All+Stores&storeNO=")  # page url

        all.append(row)
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

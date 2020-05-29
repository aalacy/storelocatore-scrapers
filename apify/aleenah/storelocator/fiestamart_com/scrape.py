import csv
import re
from sgrequests import SgRequests
from bs4 import BeautifulSoup

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

    headers={
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36'}
    res=session.get("https://www.fiestamart.com/wp-json/store_locations/all",headers=headers)
    #print(res)
    #print(res.json())
    stores=res.json()['locations']

    for store in stores:
        ids.append(store['id'])
        locs.append(store['name'])
        ph=store['phone'].strip()
        if ph=="":
            phones.append("<MISSING>")
        else:
            phones.append(ph)
        zips.append(store['postal'])
        lat.append(store['lat'])
        long.append(store['lng'])
        street.append(store['address'])
        cities.append(store['city'])
        states.append(re.findall(r'([A-Z]{2})',store['state'])[0])
        page_url.append("https://www.fiestamart.com/store/"+store['address'].strip().replace(".","").replace(" ","-")+"_store-"+store['id'])

    for url in page_url:
        #print(url)
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'max-age=0',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'                   }
        res=session.get(url,headers=headers)
        #print(res)
        soup = BeautifulSoup(res.text, 'html.parser')
        #print(soup,"**********")
        #div=soup.find('div',{'class':'store-info-wrapper'})
        tim =soup.find('div',{'class':'hours'}).text.replace("\n"," ").strip()
        if tim=="":
            timing.append("<MISSING>")
        else:
            timing.append(tim)

        ty=soup.find_all('script', {'type': 'application/ld+json'})[1].string

        types.append(re.findall(r'"@type": "([^"]*)",',ty)[0])

    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://www.fiestamart.com")
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
        row.append(page_url[i])  # page url

        all.append(row)
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

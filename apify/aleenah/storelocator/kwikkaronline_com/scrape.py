import csv
import re
import sgzip
import requests
from pyzipcode import ZipCodeDatabase
from bs4 import BeautifulSoup
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('kwikkaronline_com')



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

    headers = {
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9',
    'content-length': '212',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://kwikkaronline.com',
    'referer': 'https://kwikkaronline.com/store-locator/',
                       'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
   'x-requested-with': 'XMLHttpRequest',
    }
    zip_codes=sgzip.for_radius(50)
    zcdb = ZipCodeDatabase()
    key_set = set([])
    for zip in zip_codes:
        #zip= 77001
        logger.info(zip)
        try:
            zall= zcdb[zip]
        except:
            continue
        res = requests.post("https://kwikkaronline.com/wp-admin/admin-ajax.php",
                       headers=headers,
                       data='action=locate&address='+str(zip)+'&formatted_address=Addison%2C+TX+75001%2C+USA&locatorNonce=a1c3d6f397&distance=50&latitude='+str(zall.latitude)+'&longitude='+str(zall.longitude)+'&unit=miles&geolocation=false&allow_empty_address=false')
        logger.info(res)
        results=res.json()['results']
        if results != None:
            for result in results:

                out = result['output']
                st=re.findall(r'<div class="ab-address-1">(.*)</div>\n<div class="ab-address-2">',out,re.DOTALL)[0]

                addr=re.findall(r'<div class="ab-city-state-zip-code">(.*)</div>\n<div class="ab-phone-number">',out,re.DOTALL)[0]
                addr=addr.split(",")
                c=addr[0]
                addr=addr[1].strip().split(" ")
                s=addr[0]
                z=addr[1]
                key = c+s+z+st
                if key not in key_set:
                    key_set.add(key)
                    states.append(s)
                    zips.append(z)
                    street.append(st)
                    cities.append(c)
                    ids.append(result['id'])
                    locs.append(result['title'])
                    page_url.append(result['permalink'])
                    lat.append(result['latitude'])
                    long.append(result['longitude'])
                    ph=re.findall(r'<div class="ab-phone-number">(.*)</div>\n<div class="ab-show-on-map">',out,re.DOTALL)
                    if ph==[]:
                        phones.append("<MISSING>")
                    else:
                        ph=ph[0].strip()
                        if ph=="":
                            phones.append("<MISSING>")
                        else:
                            phones.append(ph)

    for url in page_url:
        logger.info(url)
        res= requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        tim = soup.find('div', {'class': 'store-hours'}).text.replace('\n',"").strip()
        logger.info("tim",tim)
        if tim =="":
            timing.append("<MISSING>")
        else:
            timing.append(tim)
    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://kwikkaronline.com/")
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
        row.append(page_url[i])  # page url

        all.append(row)
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

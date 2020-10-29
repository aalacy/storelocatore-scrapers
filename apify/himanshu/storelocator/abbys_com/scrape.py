import csv
from bs4 import BeautifulSoup as bs
import re
import json
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('abbys_com')


session = SgRequests()


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url = "http://abbys.com/"
    addresses = []
    headers = {
    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    'cache-control': "no-cache",
    'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
    'postman-token': "25729062-62d5-eddb-3b85-abe21430b650"
    }
    # header = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5',
    #           'Content-type': 'application/x-www-form-urlencoded'}

    soup = bs(session.get("https://abbys-pizza-locations.securebrygid.com/zgrid/themes/10350/portal/index.jsp", headers=headers).text,'lxml')
    for index,dt in enumerate(soup.find_all("ul",{"class":"state-group"})):
        for q in dt.find_all("li",{"class":"state-group-item"}):
            addr = list(q.stripped_strings)
            location_name = list(q.stripped_strings)[0]
            street_address = list(q.stripped_strings)[1]
            city = addr[2].split(",")[0]
            state = addr[2].split(",")[1].strip().split()[0]
            zipcode = addr[2].split(",")[1].strip().split()[-1]
            phone = addr[3]
            page_url = q.find("a",text=re.compile("Order Online"))['href']
            latitude=''
            longitude=''
            if len(q.find("a",text=re.compile("Directions"))['href'].split("sll=")[-1].split("&sspn")) != 1:
                latitude = (q.find("a",text=re.compile("Directions"))['href'].split("sll=")[-1].split("&sspn")[0].split(",")[0])
                longitude = (q.find("a",text=re.compile("Directions"))['href'].split("sll=")[-1].split("&sspn")[0].split(",")[-1])
            hours_of_operation = " ".join(addr[4:][:-2])
            store = []
            store.append("https://abbys.com/")
            store.append(location_name if location_name else '<MISSING>')
            store.append(street_address if street_address else '<MISSING>')
            store.append(city if city else '<MISSING>')
            store.append(state if state else '<MISSING>')
            store.append(zipcode if zipcode else '<MISSING>')
            store.append("US")
            store.append( '<MISSING>')
            store.append(phone if phone else '<MISSING>')
            store.append('<MISSING>')
            store.append(latitude if latitude else '<MISSING>')
            store.append(longitude if longitude else '<MISSING>')
            store.append(hours_of_operation if hours_of_operation else '<MISSING>')
            store.append(page_url if page_url else '<MISSING>')
            # logger.info("===", str(store))
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            yield  store
    

   


def scrape():
    data = fetch_data()
    write_output(data)

scrape()    

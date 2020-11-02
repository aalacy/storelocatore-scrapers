import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('samsung_com__us__samsung-experience-store')


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://www.samsung.com/us/samsung-experience-store"
    r = session.get(base_url+"/locations/")
    soup=BeautifulSoup(r.text,'lxml')
    return_main_object = []
    main=soup.find_all('div',{"class":"container info-component"})
    for data in main:
        page_url = data.find("a",text=re.compile("GO TO THE STORE"))['href']
        name=data.find('h2',{"class":"info-component-header"}).text.strip()
        mct=list(data.find('h3',{"class":"title"}).stripped_strings)
        address=" ".join(mct[:-1])
        city=mct[-1].split(',')[0]
        state=mct[-1].split(',')[1].strip().split()[0]
        zip=mct[-1].split(',')[1].strip().split()[-1]
        phone = data.find("a",{"class":"phone-number"}).text.strip()
        m=list(data.find('div',{"class":"column-content"}).stripped_strings)
        lt=data.find('div',{"class":"column-content"}).find('a',{"class":"header-cta"})['href'].split('@')[1].split(',')
        lat=lt[0]
        lng=lt[1]
        del m[0]
        del m[-1]
        del m[-1]
        del m[1]
        del m[0]
        hour=' '.join(m).strip()
        store=[]
        store.append(base_url)
        store.append(name)
        store.append(address)
        store.append(city)
        store.append(state)
        store.append(zip)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("samsung-experience-store")
        store.append(lat)
        store.append(lng)
        store.append(hour.replace("In-store shopping hours: ",'').replace("Curbside pickup or repairs by appointment only.",'').replace("In-store shopping hours: ",''))
        store.append(page_url)
        # logger.info(store)
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)
scrape()

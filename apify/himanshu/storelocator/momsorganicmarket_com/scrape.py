import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('momsorganicmarket_com')




session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://momsorganicmarket.com"
    r = session.get(base_url)
    soup=BeautifulSoup(r.text,'lxml')
    return_main_object = []
    main=soup.find('li',{"id":"menu-item-372"}).find_all('a')
    del main[0]
    for atag in main:
        link = atag['href']
        logger.info(link)
        r1 = session.get(link)
        soup1=BeautifulSoup(r1.text,'lxml')
        main1=soup1.find_all('div',{'class':"et_pb_blurb_container"})
        for dt in main1:
            name=dt.h1.text.strip()
            try:
                lt=dt.find('h4',{"class":"et_pb_module_header"}).find('a')['href'].split('@')
                lat=''
                lng=''
                if len(lt)>1:
                    lat=lt[1].split(',')[0].strip()
                    lng=lt[1].split(',')[1].strip()
            except:
                lat="<MISSING>"
                lng="<MISSING>"
            raw_address = dt.find('div',{"class":"et_pb_blurb_description"}).find_all("p")[1].text
            if "Learn More" in raw_address:
                continue
            if name in raw_address:
                city = name
                address = raw_address[:raw_address.find(name)].strip()
            else:
                address = " ".join(raw_address.split()[:-3])
                city = raw_address.split()[-3].replace(",","")
            ct=raw_address.split(',')
            state=ct[-1].strip().split(' ')[0].strip()
            zip=ct[-1].strip().split(' ')[1].strip()
            phone= dt.find('div',{"class":"et_pb_blurb_description"}).find_all("p")[2].text.strip()
            hour= dt.find('div',{"class":"et_pb_blurb_description"}).find_all("p")[3].text.strip()
            country="US"
            store=[]
            store.append(base_url)
            store.append(link)
            store.append(name if name else "<MISSING>")
            store.append(address if address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zip if zip else "<MISSING>")
            store.append(country if country else "<MISSING>")
            store.append("<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append(lat if lat else "<MISSING>")
            store.append(lng if lng else "<MISSING>")
            store.append(hour if hour else "<MISSING>")
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

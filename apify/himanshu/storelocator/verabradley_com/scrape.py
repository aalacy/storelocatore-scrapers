import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('verabradley_com')




session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://www.verabradley.com"
    i=1
    return_main_object = []
    output=[]
    while i>0:
        r = session.get(base_url+'/us/selfservice/FindStore?zip=&address=&city=&state=&curpage='+str(i))
        soup=BeautifulSoup(r.text,'lxml')
        logger.info(i)
        if soup.find('div',{'class':"storefinder-results"})==None:
            i=0
        else:
            i=i+1
            main=soup.find('div',{'class':"storefinder-results"}).find_all('div',{'class':'store-result'})
            for loc in main:
                name=loc.find('span',{"itemprop":"name"}).text.strip()
                address=loc.find('span',{"itemprop":"addressLocality"}).text.strip()
                ct=loc.find_all('span',{"itemprop":"addressRegion"})
                city=ct[0].text.strip()
                state=ct[1].text.strip()
                hour=''
                zip=''
                phone=''
                if loc.find('div',{"class":'store-hours'})!=None:
                    hour=' '.join(list(loc.find('div',{"class":'store-hours'}).stripped_strings)).strip()
                if loc.find('span',{"itemprop":"postalCode"})!=None:
                    zip=loc.find('span',{"itemprop":"postalCode"}).text.strip()
                if loc.find('span',{"itemprop":"telephone"})!=None:
                    phone=loc.find('span',{"itemprop":"telephone"}).text.replace('Phone: ','').strip()
                lat=loc['data-lat'].strip()
                lng=loc['data-long'].strip()
                country="<MISSING>"
                if len(zip)==5:
                    country="US"
                if len(zip)==7:
                    country="CA"
                store=[]
                store.append(base_url)
                store.append(name if name else "<MISSING>")
                store.append(address if address else "<MISSING>")
                store.append(city if city else "<MISSING>")
                store.append(state if state else "<MISSING>")
                store.append(zip if zip else "<MISSING>")
                store.append(country if country else "<MISSING>")
                store.append("<MISSING>")
                store.append(phone if phone else "<MISSING>")
                store.append("Verabradley")
                store.append(lat if lat else "<MISSING>")
                store.append(lng if lng else "<MISSING>")
                store.append(hour if hour else "<MISSING>")
                # if zip not in output:
                #     output.append(zip)
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

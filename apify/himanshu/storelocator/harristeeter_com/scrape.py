import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
import unicodedata
import html5lib
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w',newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    addressess =[]
    url = "https://locations.harristeeter.com/"
    sup = bs(session.get(url).text,'html5lib')
    for td in sup.find("div",{"id":"state_list"}).find_all("li"):
        link = bs(session.get(td.find("a")['href']).text,'html5lib')
        for href in link.find_all("div",{"class":"city_item"}):
            sub_page = bs(session.get(href.find("a")['href']).text,'html5lib')
            for pag_url in sub_page.find("div",{"id":"locations"}).find_all("a",{"linktrack":re.compile("Location page")}):
                page_urls = pag_url['href']
                store_sup = bs(session.get(page_urls).text,'html5lib')
                data = json.loads(store_sup.find_all("script",{"type":"application/ld+json"})[-1].text.strip().replace("// if the location file does not have the hours separated into open/close for each day, remove the below section",''))
                location_name = data['name']
                street_address = data['address']['streetAddress']
                city = data['address']['addressLocality']
                state = data['address']['addressRegion']
                zipp = data['address']['postalCode']
                lat = data['geo']['latitude']
                lng = data['geo']['longitude']
                phone  = data['telephone']
                hours =''
                for h in data['openingHoursSpecification']:
                    hours = hours + " "+" ".join(h['dayOfWeek']) + " "+h['opens'] + "-"+ h['closes']+","
                store = []
                store.append("https://www.harristeeter.com/")
                store.append(location_name if location_name else "<MISSING>") 
                store.append(street_address if street_address else "<MISSING>")
                store.append(city if city else "<MISSING>")
                store.append(state)
                store.append(zipp if zipp else "<MISSING>")
                store.append("US")
                store.append("<MISSING>") 
                store.append(phone if phone else "<MISSING>")
                store.append("<MISSING>")
                store.append(lat if lat else "<MISSING>")
                store.append(lng if lng else "<MISSING>")
                store.append(hours.rstrip(","))
                store.append(page_urls if page_urls else "<MISSING>")
                for i in range(len(store)):
                    if type(store[i]) == str:
                        store[i] = ''.join((c for c in unicodedata.normalize('NFD', store[i]) if unicodedata.category(c) != 'Mn'))
                store = [x.replace("–","-") if type(x) == str else x for x in store]
                if str(store[2]+store[-1]) in addressess:
                    continue
                addressess.append(str(store[2]+store[-1]))
                yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()

import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('julesthincrust_com')


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
    header = {'User-agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'}
    address = []
    base_url = "http://julesthincrust.com/"
    loacation_url = base_url+'locations/'
    r = session.get(loacation_url, headers = header)
    soup = BeautifulSoup(r.text,"lxml")
    
    ck = soup.find("section",{"class": "section locations"}).find_all('div',{'class':'location-state'})
    # logger.info(ck)
    for target_list in ck:
    #    locator_domain = base_url
       location_name1 = target_list.find_all('div',{'class':'card'})
       for i in location_name1:
            location_name = (i.find('h1').text)
            street_address1 = i.find_all('div',{'class':'details'})
            for k in street_address1:
                state = (k.find_all("p")[1].text.split(",")[-1].strip().split(" ")[0])
                zipp = (k.find_all("p")[1].text.split(",")[-1].strip().split(" ")[-1])
                city = k.find_all("p")[1].text.split(",")[0]
                street_address = k.find_all("p")[0].text
                phone = k.find_all("p")[-1].text
            hours = i.find_all('div',{'class':'hours'})
            hours_of_operation=''
            for t in hours:
                hours_of_operation =hours_of_operation+ ' '+ " ".join(list(t.stripped_strings)).strip()
            page_url = ''
            url = i.find_all('ul',{'class':'ordering'})
            for h in url:
                page_url = (h.find("li").find("a")['href'])
            store = []
            store.append(base_url if base_url else "<MISSING>")
            store.append(location_name if location_name else "<MISSING>") 
            store.append(street_address if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zipp if zipp else "<MISSING>")
            store.append("US")
            store.append("<MISSING>") 
            store.append(phone if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append(hours_of_operation if hours_of_operation else "<MISSING>")
            store.append(page_url if page_url else "<MISSING>")
            if store[2] in address :
                continue
            address.append(store[2])
            yield store 
def scrape():
    data = fetch_data()
    write_output(data)

scrape()

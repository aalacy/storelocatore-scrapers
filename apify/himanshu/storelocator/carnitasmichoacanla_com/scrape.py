import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('carnitasmichoacanla_com')





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
  
    base_url= "https://carnitasmichoacanla.com/locations/"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    data = soup.find_all("div",{"class":"entry-content"})
    # logger.info(data)
    name_store=[]
    store_detail=[]
    return_main_object=[]
    hours =[]
    phone_no =[]
    latitude =[]
    longitude =[]
    for i in data:

        phone1= i.find_all("p")

        for phone in phone1:
            if len(list(phone.stripped_strings)) ==1:
                if len(list(phone.stripped_strings)[0].split(","))==1:
                    if "Find a location near you:" in list(phone.stripped_strings)[0].split(","):
                        pass
                    else:
                        phone_no.append(list(phone.stripped_strings)[0].split(",")[0])


        time = i.find_all("table",{"class":"WgFkxc"})
        for t in time:
          hours.append(" ".join(list(t.stripped_strings)))

        
        a= (i.find_all('p'))
        for a1 in a:
            if a1.a != None:
                latitude.append(a1.a['href'].split("@")[1].split("z")[:1][0].split(',')[0])
                longitude.append(a1.a['href'].split("@")[1].split("z")[:1][0].split(',')[1])

        st = i.find_all("strong")
        for j in st:
            tem_var =[]
            street_address=j.text.split(',')[0]
            name_store.append(street_address)
            tem_var.append(street_address)
            city = j.text.split(',')[1]
            tem_var.append(city)
            state =  j.text.split(',')[2].split( )[0]
            tem_var.append(state)
            zipcode =  j.text.split(',')[2].split( )[1]
            tem_var.append(zipcode)
            store_detail.append(tem_var)
            
    hours.insert(10,"<MISSING>")
    
    for i in range(len(name_store)):
        store = list()
        store.append("https://carnitasmichoacanla.com/")
        store.append('<MISSING>')
        store.extend(store_detail[i])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone_no[i])
        store.append("<MISSING>")
        store.append(latitude[i])
        store.append(longitude[i])
        store.append(hours[i])
        store.append('https://carnitasmichoacanla.com/locations/')
        # logger.info(hours[i])
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()





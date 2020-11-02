import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url= "http://www.quikmartstores.com/store-locations/"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    k = (soup.find_all("table",{"border":"0","cellpadding":"10","cellspacing":"0"}))
    
    # name1 = soup.find("div",{"id":"navigation"}).find_all("a")[1:4]



    street_address =[]
    phone=[]
    store_no1 =[]

    for i in k:
        tem_var=[]
        
        a= i.find_all('a')
        td = i.find_all("td")
        store_no1 = (list(td[0].stripped_strings)[1:])
        phone=(list(td[3].stripped_strings)[1:])
        for a1 in a:
            street_address.append(a1.text)

   
    for i in range(len(street_address)):
        store = list()
        store.append("http://www.quikmartstores.com")
        store.append("<MISSING>")
        store.append(street_address[i])
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("US")
        store.append(store_no1[i])
        store.append(phone[i])
        store.append("quikmartstores")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        return_main_object.append(store)


  
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()



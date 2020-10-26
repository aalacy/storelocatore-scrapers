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
    base_url= "https://www.sanfelipenc.com/locations"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    phone =[]
    hours =[]
    lat=[]
    log=[]
    k = soup.find_all("div",{"class":"sqs-block-content"})
    k1 = (soup.find_all("div",{"class":"sqs-block map-block sqs-block-map"}))
    for k2 in k1:
        lat.append(json.loads(k2.attrs["data-block-json"])["location"]['mapLat'])
        log.append(json.loads(k2.attrs["data-block-json"])["location"]['mapLng'])
        # print(json.loads(k2.attrs["data-block-json"])["location"]['mapLng'])
    for i in k:
        
        p =i.find_all('p')
        for j in p:
            tem_var=[]
            if len(list(j.stripped_strings))!=1 :
                store_name.append(list(j.stripped_strings)[0])
                street_address = (list(j.stripped_strings)[1])
                city = list(j.stripped_strings)[2].split(',')[0]
                state =list(j.stripped_strings)[2].split(',')[1].split( )[0]
                zipcode = list(j.stripped_strings)[2].split(',')[1].split( )[1]
                phone = " ".join(list(j.stripped_strings)[3:])
               

                tem_var.append(street_address)
                tem_var.append(city)
                tem_var.append(state)
                tem_var.append(zipcode)
                tem_var.append("US")
                tem_var.append("<MISSING>")
                tem_var.append(phone)
                tem_var.append("sanfelipenc")
                store_detail.append(tem_var)     


    for i in range(len(store_name)):
        store = list()
        store.append("https://www.sanfelipenc.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        store.append(lat[i])
        store.append(log[i])
        store.append("<MISSING>")
        return_main_object.append(store)
  
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()



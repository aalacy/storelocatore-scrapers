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
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
  
    base_url= "https://graffitijunktion.com/locations/"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    data = soup.find_all("div",{"class":"wpb_text_column"})
    phone =[]
    street_address=[]
    store_name=[]
    store_detail=[]
    return_main_object=[]
    lat=[]
    lng=[]
    hours =[]
    k  = soup.find_all("script")
    for i in k:
        if "var map" in i.text:
            k1 = json.loads(i.text.split("maps(")[1].replace(').data("wpgmp_maps");});',''))
            for i in k1['places']:
                lat.append(i['location']['lat'])
                lng.append(i['location']['lng'])
                # print(i['location']['lng'])
    # exit()
    data1 = soup.find_all("h2",{"style":"font-weight:bold;"})
    for d in data1:
        store_name.append(d.text)
        

    for target_list in data:
        tem_var =[]
        if target_list.find('div',{'class':'wpb_wrapper'}).p != None:
            street_address = list(target_list.find('div',{'class':'wpb_wrapper'}).stripped_strings)[1].split(',')[0]
            city = list(target_list.find('div',{'class':'wpb_wrapper'}).stripped_strings)[1].split(',')[1]
            state = list(target_list.find('div',{'class':'wpb_wrapper'}).stripped_strings)[1].split(',')[2].split( )[0]
            zipcode =  list(target_list.find('div',{'class':'wpb_wrapper'}).stripped_strings)[1].split(',')[2].split( )[1]
            phone = list(target_list.find('div',{'class':'wpb_wrapper'}).stripped_strings)[3]
            hours1= list(target_list.find('div',{'class':'wpb_wrapper'}).stripped_strings)[5]

            tem_var.append(street_address)
            tem_var.append(city)
            tem_var.append(state)
            tem_var.append(zipcode)
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("<MISSING>")            
            hours.append(hours1)            
            store_detail.append(tem_var)
            
        
    for i in range(len(store_name)):
        store = list()
        store.append("https://graffitijunktion.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        store.append(lat[i])
        store.append(lng[i])
        store.append(hours[i])
        store.append('<MISSING>')
        return_main_object.append(store) 
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()



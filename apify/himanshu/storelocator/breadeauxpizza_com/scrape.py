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
    base_url= "https://breadeauxpizza.com/find-a-breadeaux/"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    phone1 =[]
    # data = soup.find_all("div",{"class":"view-content"})
    data = soup.find("tbody")

    for d in  data:
        tr = d.find_all("td",{"class":"wpgmza_table_address"})
        names = d.find_all("td",{"class":"wpgmza_table_title"})
        phone = d.find_all("td",{"class":"wpgmza_table_description"})

        for p in phone:
            phone1.append(p.text.replace("Order Online Now!","").replace("We do not offer online ordering at the moment. Please call us at ","").replace(" and we will help you with your order.","").replace("\n","").strip())

        for name in names:
            store_name.append(name.text)

        for tr1 in tr:
            tem_var =[]
            if len(tr1.text.split(',')) ==2:
                street_address = tr1.text.split(',')[0]

                state =  tr1.text.split(',')[1].split( )[0]
                zipcode =  tr1.text.split(',')[1].split( )[1]

                tem_var.append(street_address)
                tem_var.append(state)
                tem_var.append(zipcode)
                store_detail.append(tem_var)

            elif len(tr1.text.split(',')) ==3:
                street_address = tr1.text.split(',')[0]
               
                state =  tr1.text.split(',')[2].split( )[0]
                zipcode =  tr1.text.split(',')[2].split( )[1]

                tem_var.append(street_address)
                tem_var.append(state)
                tem_var.append(zipcode)
                store_detail.append(tem_var)
            else:

                street_address1 = tr1.text.strip()
                street_address = " ".join(street_address1.split(' ')[:-2])

                state = street_address1.split(' ')[-2]
                zipcode = street_address1.split(' ')[-1]
                tem_var.append(street_address)
               
                tem_var.append(state)
                tem_var.append(zipcode)
                store_detail.append(tem_var)
                
            
             
              
    for i in range(len(store_detail)):
        store_detail[i].insert(1,store_name[i])

    
    for i in range(len(store_name)):
        store = list()
        store.append("https://breadeauxpizza.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone1[i])
        store.append("breadeauxpizza")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


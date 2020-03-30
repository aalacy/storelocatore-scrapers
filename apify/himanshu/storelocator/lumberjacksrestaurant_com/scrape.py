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
    base_url= "http://www.lumberjacksrestaurant.com/locations/"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    phone =[]
    hours =[]
    mk= []
    for id,x in enumerate(soup.find_all('script')):
        if id == 57:

            for vn in json.loads(x.text.strip().split('map_locations = ')[1].split('\nvar global_map_settings =')[0].replace('null,','').replace(',null','').replace(';','')):
                mk.append(vn['lat']+','+vn['lng'])

    k = soup.find_all("div",{"class":"motopress-code-obj"})

    for i in k:
        span = i.find_all("span")
        p = i.find_all("p")
        if p !=[]:
            for p1 in p:
               
                if "Hours:" in p1:
                    hours.append(" ".join(list(p1.stripped_strings)[1:]))
        
        for j in span:
            # print(j)
            tem_var =[]
            if list(j.stripped_strings) != []:
                if "Grass Valley" in list(j.stripped_strings):
                    pass
                else:
                    store_name.append(list(j.stripped_strings)[0].capitalize())
                    street_address = list(j.stripped_strings)[1]
                    city = list(j.stripped_strings)[2].split(",")[0]
                    state =list(j.stripped_strings)[2].split(",")[1].split( )[0]
                    zipcode = list(j.stripped_strings)[2].split(",")[1].split( )[1]
                    phone.append(list(j.stripped_strings)[-1])
   
    
                    tem_var.append(street_address)
                    tem_var.append(city)
                    tem_var.append(state)
                    tem_var.append(zipcode)
                    tem_var.append("US")
                    tem_var.append("<MISSING>")

                    store_detail.append(tem_var)

    hours.insert(8,"Sun - Sat 7 am to 3 pm")
    m = 0
    for i in range(len(store_name)):
        store = list()
        store.append("http://www.lumberjacksrestaurant.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        store.append(phone[i])
        store.append("<MISSING>")

        store.append(mk[m].split(',')[0])
        store.append(mk[m].split(',')[1])


        store.append(hours[i])
        store.append(base_url)
        return_main_object.append(store)
        m+=1

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()



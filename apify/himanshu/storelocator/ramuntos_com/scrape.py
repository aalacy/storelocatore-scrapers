import csv
import requests
from bs4 import BeautifulSoup
import re
import json


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
    base_url= "https://ramuntos.com/locations/"
    r = requests.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    lat =[]
    log =[]
    hours =[]
    k=(soup.find_all("div",{"class":"entry-content"}))

    for i in k:

          
        lat1  =  i.find_all("div",{"class":"et_pb_map_pin"})
        # print(lat1)
        for j in lat1:
            # lat = j['data-lat']
            # lng = j['data-lng']
  
            # print(lat2.arttrs['data-center-lat'])
            # print(lat2.attrs['data-lat'])
            # for j in lat2:
            #     print(j.attrs["data-lat"])
            lat.append(j['data-lat'])
            log.append(j['data-lng'])
            # print(j.attrs['data-center-lng'])
        
        p  =  i.find_all("div",{"class":"et_pb_text_inner"})
        for p1 in p:
            tem_var =[]


            if len(list(p1.stripped_strings)) != 1:
                data = list(p1.stripped_strings)
                stopwords = "(Jiffy Mart)"
                new_words = [word for word in data if word not in stopwords]
                stopwords = "Jiffy Mart Website"
                new_words1 = [word for word in new_words if word not in stopwords]
                stopwords = "www.ramuntos.com/bennington-vt"
                new_words2 = [word for word in new_words1 if word not in stopwords]

           
                

                if "232 Grove Street, Brandon, VT 05733" in  (new_words) or "89 VT Rte. 103, Chester, VT 05143" in (new_words):
                    street_address = new_words2[1].split(",")[0]
                    city =new_words2[1].split(",")[1]
                    state = new_words2[1].split(",")[2].split( )[0]
                    zipcode = new_words2[1].split(",")[2].split( )[1]

                    hours.append(new_words2[2])
                    phone = new_words2[-1]


                    tem_var.append(street_address)
                    tem_var.append(city)
                    tem_var.append(state)
                    tem_var.append(zipcode)
                    tem_var.append("US")
                    tem_var.append("<MISSING>")
                    tem_var.append(phone)
                    tem_var.append("ramuntos")
                    
                    store_detail.append(tem_var)

                    store_name.append(new_words2[0])

                else:
                    store_name.append(new_words2[0])
                    street_address = new_words2[1]
                    city =  new_words2[2].split(',')[0]
                    state = new_words2[2].split(',')[1].split( )[0]
                    zipcode = new_words2[2].split(',')[1].split( )[1]
                    if (new_words2[-1].split("Phone:\xa0"))[0]:
                        phone = (new_words2[-1].split("Phone:\xa0")[0].replace("Phone: ",""))
                    else:
                        phone = (new_words2[-1].split("Phone:\xa0")[1])

                    hours.append(" ".join(new_words2[3:-1]).replace("Phone:",""))

                    tem_var.append(street_address)
                    tem_var.append(city)
                    tem_var.append(state)
                    tem_var.append(zipcode)
                    tem_var.append("US")
                    tem_var.append("<MISSING>")
                    tem_var.append(phone)
                    tem_var.append("ramuntos")
                   
                    store_detail.append(tem_var)   
   
   
    for i in range(len(store_name)):
        store = list()
        store.append("https://ramuntos.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        store.append(lat[i])
        store.append(log[i])
        store.append(hours[i])
        return_main_object.append(store) 

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()



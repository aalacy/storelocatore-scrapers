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
    base_url= "https://www.membersccu.org/hours-and-locations"
    r = requests.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    
    k= soup.find_all("div",{"class":"liner"})

    for i in k:
        p = i.find_all("div",{"class":"listbox"})
        for j in p:
            tem_var =[]
            v= (list(j.stripped_strings)[6:])
            stopwords = "* Available to members only"
            new_words = [word for word in v if word not in stopwords]
            
            stopwords = "Self-Serve Lobby Coin Machine"
            new_words1 = [word for word in new_words if word not in stopwords]

            stopwords ="Fax:"
            new_words2 = [word for word in new_words1 if word not in stopwords]

    
            patt = re.compile(r'[0-9-\(\) ]+$')

            if patt.match(new_words2[0]):
                del new_words2[0]

            hours = (" ".join(new_words2).replace("Coin Machine Available",""))
            phone =list(j.stripped_strings)[5]
            zipcode = list(j.stripped_strings)[3].split(',')[1].split( )[1]
            state = list(j.stripped_strings)[3].split(',')[1].split( )[0]
            city = list(j.stripped_strings)[3].split(',')[0]
            street_address = list(j.stripped_strings)[2]
            store_name.append(list(j.stripped_strings)[1])

            tem_var.append(street_address)
            tem_var.append(city)
            tem_var.append(state.strip())
            tem_var.append(zipcode.strip())
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("membersccu")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append(hours)
            store_detail.append(tem_var)

   
    for i in range(len(store_name)):
        store = list()
        store.append("https://www.membersccu.org")
        store.append(store_name[i])
        store.extend(store_detail[i])
     
        return_main_object.append(store) 

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

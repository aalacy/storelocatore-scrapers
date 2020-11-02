import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import ast


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
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    base_url= "https://www.coasthotels.com/contact-us/"
    r = session.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    
    zip1 =[]
    state =[]
    city=[]
    st1=[]
    phone =[]
    store_name=[]
    return_main_object =[]
   
    stores = soup.find_all("div",{"class":"page-content-main-left"})
    stores1 = soup.find_all("div",{"class":"page-content-main-right"})

    for i in stores1:
        st = i.find_all("address")
        for j in st:
            stopwords =','
            v= (list(j.stripped_strings))
            new_words = [word for word in v if word not in stopwords]
            zip1.append(new_words[-1].split(',')[1].split( )[1])
            state.append(new_words[-1].split(',')[1].split( )[0])
            city.append(new_words[-1].split(',')[0])
            st1.append(new_words[-2])
     
         
        phone1 =  i.find_all("div",{"class":"phone"})
        for j in phone1:
            phone.append(list(j.stripped_strings)[0].replace("Tel: ","").replace("or 587-774-1614",""))
            


    for i in stores:
        streetAddress =  i.find_all("span",{"itemprop":"streetAddress"})
        addressLocality =  i.find_all("span",{"itemprop":"addressLocality"})
        addressRegion =  i.find_all("span",{"itemprop":"addressRegion"})
        postalCode =  i.find_all("span",{"itemprop":"postalCode"})
        phone1 =  i.find_all("div",{"class":"phone"})

        l =  i.find_all("li",{"class":"last"})
        for j in l:
            phone2 = j.find_all("div",{"class":"phone"})[0]
   

        h =  i.find_all("h4")

        for j in h:
            store_name.append(list(j.stripped_strings)[0])

        for j in phone1:
            phone.append(list(j.stripped_strings)[0].replace("Tel: ",""))

        for j in postalCode:
            zip1.append(list(j.stripped_strings)[0])

        for j in addressRegion:
            state.append(list(j.stripped_strings)[0])

        for j in addressLocality:
            city.append(list(j.stripped_strings)[0])

            
        for index,j in enumerate(streetAddress):
            if "2100 Oak Drive" in list(j.stripped_strings):
                st1.append("2100 Oak Drive")
            else:
                st1.append(list(j.stripped_strings)[0])

        

    for i in range(len(store_name)):
        store = list()
        store.append("https://www.coasthotels.com")
        store.append(store_name[i])
        store.append(st1[i])
        store.append(city[i])
        store.append(state[i])
        store.append(zip1[i])
        if len(zip1[i])==6 or len(zip1[i])==7:
            store.append("CA")
        else:
            store.append("US")

        store.append("<MISSING>")
        store.append(phone[i])
        store.append("coasthotels")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


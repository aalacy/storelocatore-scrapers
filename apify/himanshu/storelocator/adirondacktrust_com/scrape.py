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
    base_url= "https://www.adirondacktrust.com/about/locations/"
    r = session.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    
    hours1 =[]
    
    store_name=[]
    store_detail=[]
    return_main_object=[]

    st2=[]
    city2=[]
    state2=[]
    zip2 =[]
    phone1=[]
    k = (soup.find_all("div",{"class":"address-location"}))

    for i in k:
        v= (list(i.stripped_strings))
        hours =''
        if "Hours:" in v:
            store_name.append(v[0])
            hours1.append(" ".join(v[:-3][2:]).replace("Phone: ","").replace("(518) 458-1800","").replace("(518) 584-5300",""))
            zip1 = v[-2].split(",")[-1].split( )[-1]
            state = " ".join(v[-2].split(",")[-1].split( )[:-1])
            state2.append(state)
            city = v[-2].split(",")[-2].replace("33 Marion Ave. ","")
            phone1.append("<MISSING>")
            city2.append(city)
            zip2.append(zip1)
            st= (v[-2].split(',')[0].replace("Saratoga Springs",""))
            st2.append(st)
           
        else:
            
            if "VIEW DETAILS" in i.text:
                p = i.find_all("a")
         
                
                base_url1= p[-1]['href']
                r = session.get(base_url1,headers=headers)
                soup1= BeautifulSoup(r.text,"lxml")
                k1 = (soup1.find_all("div",{"class":"row"}))
                time = '' 
                for k2 in k1:
                    v1 = (k2.find_all("p",{"class":""}))
                    
                    for v2 in v1[-2:]:
                        if "Lobby" in list(v2.stripped_strings) or "Drive-Thru" in list(v2.stripped_strings):
                            time = time +' '+" ".join(list(v2.stripped_strings))
                           
                hours1.append(time)
         
            store_name.append(v[0])
            phone =v[2]
            phone1.append(phone)
    
            if len(v[4].split(',')) ==2:
                street_address = v[4].split(',')[0]
                st2.append(street_address)
                zip1 = v[4].split(',')[1].split( )[-1]
                state = (" ".join(v[4].split(',')[1].split( )[:-1]))
                city = "<MISSING>"
                city2.append(city)
                
                state2.append(state)
                zip2.append(zip1)

            
            else:
                zip1 = v[4].split(',')[-1].split( )[-1]
                state =v[4].split(',')[-1].split( )[-2]
                city = v[4].split(',')[-2]
                st =v[4].split(',')[0]
                city2.append(city)
                st2.append(st)
                state2.append(state)
                zip2.append(zip1)


   
 


    for i in range(len(store_name)):
        store = list()
        store.append("https://www.adirondacktrust.com")
        store.append(store_name[i])
        store.append(st2[i])
        store.append(city2[i])
        store.append(state2[i])
        store.append(zip2[i])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone1[i])
        store.append("adirondacktrust")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(hours1[1])
        return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


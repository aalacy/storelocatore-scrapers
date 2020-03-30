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
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    base_url= "https://www.chickenuevo.com/locations"
    r = session.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    phone = []
    city = []
    state = []
    k = soup.find_all("div",{"class":"txtNew"})
    tem=[]
    for target_list in k:
        p = target_list.find_all('p')
        
        for p1 in p:
            
            if list(p1.stripped_strings) != []:
                if len(list(p1.stripped_strings))==1:
                    if "-" in (list(p1.stripped_strings)[0]):
                        phone.append(list(p1.stripped_strings)[0])
                if len(list(p1.stripped_strings)[0].split(',')) ==2:
                   city.append((list(p1.stripped_strings)[0].split(','))[0])
                   state.append((list(p1.stripped_strings)[0].split(','))[1])
                   
                else:
                   
                    if "Rd" in list(p1.stripped_strings)[0].split(',')[0] or "4820 South 6th Ave" in list(p1.stripped_strings)[0].split(',')[0]:
                        tem.append(list(p1.stripped_strings)[0].split(',')[0])
    
    mylist = list(dict.fromkeys(tem))
    mylist1 = list(dict.fromkeys(phone))
    del mylist[-1]
    
    
    for i in range(len(mylist)):
        store = list()
        store.append("https://www.chickenuevo.com")
        store.append(mylist[i])
        store.append(mylist[i])
        store.append(city[i])
        store.append(state[i])
        store.append("<MISSING>")
        store.append("US")
        store.append("<MISSING>")
        store.append(mylist1[i])
        store.append("chickenuevo")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

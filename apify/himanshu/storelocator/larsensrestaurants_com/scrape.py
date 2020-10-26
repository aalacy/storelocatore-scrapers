import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json



session = SgRequests()

def write_output(data):
    with open('data.csv', 'w')as output_file:
        writer = csv.writer(output_file, delimiter=',')
        # header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # body
        for row in data or []:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    return_main_object = []
    hour_append = []
    link_append=[]
    get_url = "https://www.larsensrestaurants.com/locations-and-menus"
    base_url = "https://larsensrestaurants.com/"
    r1 = session.get(base_url,headers= headers)
    soup1 = BeautifulSoup(r1.text,"lxml")
    hours_list = []
    l_name = []
    for h in soup1.findAll("div",class_="hours"):
        hours = " ".join(list(h.stripped_strings)).split("Join us")[0]
        if "Happy Hour Daily*" in hours:
            hours = hours.split("Happy Hour Daily*")[0]
        hours_list.append(hours)
        l_name.append(h.parent.h4.text.strip())
        # print("l_name ==== ",h.parent.h4.text.strip())
        


        

    
    r = session.get(get_url, headers=headers)    
    soup = BeautifulSoup(r.text, "lxml")
    main =soup.find("script",{"class":"js-react-on-rails-component"}).text
    js = json.loads(main)
    
    obj = js['preloadQueries'][0]['data']['restaurant']['locations']
    lname = []
    for index,i in enumerate(obj):
  
        # return_main_object = []
        l_name.append(i['name'].strip())
        location_name=i['name'].strip()
        # print(location_name)
        address =i['streetAddress']
        city= i['city']
        state=i['state']
        zip = i['postalCode']
        country_code = i['country']
        store_number=i['id']
        phone=i['phone']
        lat= i['lat']
        lng=i['lng']      
        location_type = i['__typename']
        page_url = "https://www.larsensrestaurants.com/"+str(i['slug'])+"-california"
        
        
        h_list = []
        for i in range(len(hours_list)):
            if l_name[i] == location_name:
                h_list.append(hours_list[i])
                
 
        hour = " ".join(h_list)
        # print(hour)
        store = []
        store.append(base_url if base_url else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(address if address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zip if zip else '<MISSING>')
        store.append(country_code if country_code else '<MISSING>')
        store.append(store_number if store_number else '<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append('<MISSING>')
        store.append(lat if lat else '<MISSING>')
        store.append(lng if lng else '<MISSING>')
        store.append(hour)
        store.append(page_url)  
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]      
        yield store
        # print("store == ",str(store))

def scrape():
    data = fetch_data()
    write_output(data)


scrape()

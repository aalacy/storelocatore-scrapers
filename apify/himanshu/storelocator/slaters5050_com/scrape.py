import csv
import requests
from bs4 import BeautifulSoup
import re
import json

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }

    
    base_url = "https://slaters5050.com"
    r = requests.get("https://slaters5050.com/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []

    url = "http://slaters5050lasvegas.com/"
    r1 = requests.get(url,headers=headers)
    soup1 = BeautifulSoup(r1.text,"lxml")
    # print(soup1)
    addresses123 = []
    name1 = list(soup1.find_all("div",{'class':"wpb_wrapper"})[14].stripped_strings)[0]
    address2 = list(soup1.find_all("div",{'class':"wpb_wrapper"})[14].stripped_strings)[1]
    city1 = list(soup1.find_all("div",{'class':"wpb_wrapper"})[14].stripped_strings)[2].split(",")[0]
    state1 = list(soup1.find_all("div",{'class':"wpb_wrapper"})[14].stripped_strings)[2].split(",")[1].split( )[0]
    zip1= list(soup1.find_all("div",{'class':"wpb_wrapper"})[14].stripped_strings)[2].split(",")[1].split( )[-1]
    phone1 = list(soup1.find_all("div",{'class':"wpb_wrapper"})[14].stripped_strings)[-2]
    # hours1 = " ".join(list(soup1.find("div",{'class':"wpb_text_column wpb_content_element  vc_custom_1575776937348"}).stripped_strings))
    # print(soup1.find_all("div",{'class':"wpb_text_column wpb_content_element"}))
    hours1 = (soup1.find(text='HOURS').parent.parent.text.replace("HOURS",''))
    longitude1 = soup1.find("iframe")['src'].split("!2d")[-1].split("!3d")[0]
    latitude1 = soup1.find("iframe")['src'].split("!2d")[-1].split("!3d")[1].split("!2m")[0]
    store = []
    store.append("https://slaters5050.com")
    store.append(name1.encode('ascii', 'ignore').decode('ascii').strip())
    store.append(address2)
    store.append(city1)
    store.append(state1)
    store.append(zip1)
    store.append("US")
    store.append("<MISSING>")
    store.append(phone1)
    store.append("<MISSING>")
    store.append(latitude1)
    store.append(longitude1)
    store.append(hours1.encode('ascii', 'ignore').decode('ascii').strip())
    store.append("http://slaters5050lasvegas.com/")
    # print(store)
    yield store
    # print(soup1.find("iframe")['src'].split("!2d")[-1].split("!3d")[1].split("!2m")[0])

    
    for location in soup.find_all("li",{'class':re.compile("menu-item menu-item-type-post_type menu-item-object-locations")}):
        location_request = requests.get(location.find("a")["href"],headers=headers)
        page_url =  location.find("a")["href"]
        # print(page_url)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        name = location_soup.find("main",{'role':"main"}).find("h1").text.strip()
        address = list(location_soup.find("p",{'class':"address"}).stripped_strings)
        if "Guests must have JBPHH base access" in address[-1]:
            del address[-1]
        if "Free Valet Parking" in address[-1]:
            del address[-1]
        if len(address) != 1:
            # print(address)
            if len(address[1].split(",")) != 2:
                address[0] = " ".join(address[0:2])
                del address[1]

            
            us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(address[-1]))
            state_list = re.findall(r' ([A-Z]{2})', str(address[-1]))
            

            if state_list:
                state = state_list[-1]

            if us_zip_list:
                zipp = us_zip_list[-1]
            if "JBPHH Honolulu" in address[0]:
                state = address[-1].split(",")[0]
                city = address[0].split(",")[-1]
                address1 = address[0].split(",")[0]
                # print(address[0].split(",")[0])
            else:
                address1 = address[0]
                city = address[-1].split(",")[0]

            if address[0] in addresses123:
                continue
            addresses123.append(address[0])
            # print(address)
            hours = " ".join(list(location_soup.find("div",{'class':"hours"}).stripped_strings)).split("Happy Hour")[0]
            phone = location_soup.find("p",{'class':"phone"}).text.strip()
        else:
            # print(page_url)
            state = address[-1].split(",")[-1]
            city = address[-1].split(",")[0]
            # print(address[-1].split(",")[0])
            try:
                hours = " ".join(list(location_soup.find("div",{'class':"hours"}).stripped_strings))
            except:
                hours = "<MISSING>"
            # print(hours)
            phone = location_soup.find("p",{'class':"phone"}).text.strip()

        store = []
        store.append("https://slaters5050.com")
        store.append(name)
        store.append(address1)
        store.append(city)
        store.append(state.replace("96820",''))
        store.append(zipp)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(hours.replace("Restaurant Hours Coming Soon","<MISSING>").replace("Restaurant Hours","").encode('ascii', 'ignore').decode('ascii').strip())
        store.append(page_url)
        if "661.218.5050" in store:
            pass
        else:
            yield store
        # # return_main_object.append(store)
        # print(store)
   
                


            

        

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

import csv
import requests
from bs4 import BeautifulSoup as bs
import re
import json




def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    base_url = "https://www.dylanscandybar.com/pages/visit"
    r = requests.get('https://www.dylanscandybar.com/pages/visit')
    soup =bs(r.text,'lxml')
    data = soup.find_all("div",{"class":"map-section-content-wrapper desktop-3 tablet-2 mobile-3"})
    for i in data:
        add= list(i.stripped_strings)[-2].split(",")
        if "Phase IV" in add or "127 S. Ocean Road" in add:
            continue
        if "Canada" in  add[-1]:
            del add[-1]
        name = " ".join(list(i.find("h2").stripped_strings))
        phone="<MISSING>"
        hours_of_operation="<MISSING>"
        phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(i.text))
        if phone_list:
            phone =  phone_list[-1]
        # hours_of_operation = soup.find(lambda tag: (tag.name == "strong" ) and "Hours:" in tag.text.strip()).nextSibling
        # print(hours_of_operation)
        state = add[-1].strip().split()[0].replace("New",'NY')
        zipp = " ".join(add[-1].strip().split()[1:]).replace(" - Terminal B",'').replace("York ",'')
        city = add[-2].replace("11000 Terminal Access Rd.",'').replace("6301 Silver Dart Dr",'').replace("Space #SR2",'').strip()
        street_address = " ".join(add).replace(state,'').replace(zipp,'').replace(city,'').replace(",",' ').replace("      ",'')
        # print("~~~~~~~~~~~~~~~~")
    
        lat="<MISSING>"
        lng = "<MISSING>"
        store = []
        store.append("https://www.dylanscandybar.com/")
        store.append(name.replace('|','').encode('ascii', 'ignore').decode('ascii').strip())
        if "52 Main Street" in street_address:
            hours_of_operation ="Mon-Thur: 12pm - 6pm Fri-Sun: 11am - 7pm"
        
        if "231 Hudson Street" in street_address:
            hours_of_operation ="Open 24 hours a day, 7 days a week"
        if "127 S. Ocean Road" in street_address:
            hours_of_operation = "Mon - Sun: 10am - 6pm"
        if "5501 Josh Birmingham Pkwy" in street_address:
             hours_of_operation = "Mon - Sun: 7am - 8pm"
        store.append(street_address.encode('ascii', 'ignore').decode('ascii').strip().replace("- Terminal B",''))
        store.append(city.encode('ascii', 'ignore').decode('ascii').strip())
        store.append(state.encode('ascii', 'ignore').decode('ascii').strip())
        store.append(zipp)
        if "6301 Silver Dart Dr" in street_address:
            store.append("CA")
        else:
            
            store.append("US")
        store.append("<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append("<MISSING>")
        store.append(lat.strip() if lat.strip() else "<MISSING>" )
        store.append(lng.strip() if lng.strip() else "<MISSING>")
        store.append( hours_of_operation)
        store.append("<MISSING>")
        # store = [x.replace("–", "-") if type(x) ==
        #          str else x for x in store]
        store = [x.encode('ascii', 'ignore').decode(
            'ascii').strip() if type(x) == str else x for x in store]
        # print("data ===" + str(store))
        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~")
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

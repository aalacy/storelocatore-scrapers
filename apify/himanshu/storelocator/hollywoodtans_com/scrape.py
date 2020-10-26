import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json

session = SgRequests()

session = SgRequests()
from sgrequests import SgRequests

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
             'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36',    
    }

    base_url = "http://hollywoodtans.com/" 
    try:
        r = session.get("http://hollywoodtans.com/locations/", headers=headers)
    except:
        pass
    soup = BeautifulSoup(r.text, "lxml")
    json_data = json.loads(soup.find(lambda tag: (tag.name == "script" and "map_options" in tag.text)).text.split(".maps(")[1].split(").data(")[0])['places']

    for data in json_data:
        if data['location']['country'] != "United States":
            continue
        location_name = data['title'].replace("Hollywood Tans Fairfax VA","Hollywood Tans Fairfax , VA")
        street_address = data['address'].split(',')[0]
        # print(street_address)
        city = data['location']['city'].replace("11","Nottingham").replace("3","Severna Park").replace("7","Westminster").split(",")[-1].strip() 
        state = location_name.split(",")[-1].strip()
        zipp = data['location']['postal_code']
        if zipp == "1045":
            zipp = "19053"
        country_code = data['location']['country'].replace("United States","US")
        latitude = data['location']['lat']
        longitude = data['location']['lng']
        phone = data['content'].replace("Phone: ","").replace("\r\n","").strip()
        location_type = "Salon"
        store_number = data['id']   
        page_url = data['location']['redirect_custom_link']
        # print(page_url)
        r1 = session.get(page_url, headers=headers)
        soup1 = BeautifulSoup(r1.text , "lxml")
        hours = soup1.find_all("div",{"class":"gdlr-item gdlr-content-item"})[-2].find_all("p")
        if len(hours) == 5:
            hours = " ".join(list(hours[3].stripped_strings)).replace("Salon Hours*:","").strip()
        elif len(hours) == 6:
            hours = " ".join(list(hours[4].stripped_strings)).replace("Salon Hours*:","").strip()
        elif len(hours) ==4:
            hours = " ".join(list(hours[2].stripped_strings)).replace("Salon Hours*:","").strip()
        else:
            hours = " ".join(list(hours[4].stripped_strings)).replace("Salon Hours*:","").strip() \
                +" "+ " ".join(list(hours[5].stripped_strings)).replace("Salon Hours*:","").strip()
                    
    
        store = []
        
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)   
        store.append(country_code)
        store.append(store_number)
        store.append(phone)
        store.append(location_type)
        store.append(latitude )
        store.append(longitude )
        store.append(hours)
        store.append(page_url)
        # print("data==="+str(store))
        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")

        yield store
    

        


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

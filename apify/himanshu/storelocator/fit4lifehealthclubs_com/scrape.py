import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import unicodedata

session = SgRequests()


def write_output(data):
    with open('data.csv', 'w') as output_file:
        writer = csv.writer(output_file, delimiter=",")

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for i in data or []:
            writer.writerow(i)

def fetch_data():
    addressess = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    base_url = "https://fit4lifehealthclubs.com"
    r_data = session.get("https://fit4lifehealthclubs.com/find-a-gym/",headers=headers)
    r_soup = BeautifulSoup(r_data.text,"lxml")
    json_data = json.loads(str(r_soup).split('places":')[1].split(',"listing":')[0])
    
    for value in json_data:
        if "Hope Mills" in value['title']:
            continue
        location_name = value['title']
        city = value['location']['city'].replace("Anderson Creek","Spring Lake")
        state = value['location']['state']
        zipp = value['location']['postal_code']
        if location_name == "McGee's Crossroads":
            street_address = "".join(value['address'].replace(", USA","").split(",")[:2]).replace(city,"")
        elif location_name == "Raeford":
            street_address = "4550 Fayetteville Rd."
        else:
            street_address = value['address'].replace(", USA","").split(",")[0]

        country_code = "US"
        store_number = value['id']
        content = value['content']
        reg = re.compile(r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})')
        phone=reg.findall(content)[0]
        location_type = "<MISSING>"
        latitude = value['location']['lat']
        longitude = value['location']['lng']
        page_url = content.split('<a href=\"')[1].split('\">Location Page')[0]
        r = session.get(page_url,headers=headers)
        soup = BeautifulSoup(r.text,"lxml")
        if location_name == "Mt. Olive":
            hour = list(soup.find_all("div",{"class":"wpb_wrapper"})[35].stripped_strings)
        elif location_name == "Raeford":
            hour = list(soup.find_all("div",{"class":"wpb_wrapper"})[46].stripped_strings)
        elif location_name == "Richlands":
            hour = list(soup.find_all("div",{"class":"wpb_wrapper"})[49].stripped_strings)
        elif location_name == "Spring Lake" or location_name == "Clayton":
            hour = list(soup.find_all("div",{"class":"wpb_wrapper"})[47].stripped_strings)
        elif location_name == "Fayetteville - Owens Dr.":
            pass
        else:
            hour = list(soup.find_all("div",{"class":"wpb_wrapper"})[43].stripped_strings)
            

        hours_of_operation = " ".join(hour)
        if location_name=="Fayetteville - Owens Dr.":
            page_url = "<MISSING>"
        store=[]
        store.append(base_url if base_url else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append(country_code)
        store.append(store_number)
        store.append(phone if phone else '<MISSING>')
        store.append(location_type)
        store.append(latitude)
        store.append(longitude)
        store.append(hours_of_operation)
        store.append(page_url)
        store = [x.replace("–","-") if type(x) == str else x for x in store]
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        yield store

def scrape():
    data = fetch_data()
    write_output(data)
scrape()

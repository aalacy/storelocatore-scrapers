from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import ast
import json
import csv



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation" , "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        'accept': 'application/json, text/javascript, */*; q=0.01',
    }
    base_url = "https://www.citybbq.com"
    r = session.get("https://order.citybbq.com/locations", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")    
    data = soup.find("ul",{"id":"ParticipatingStates"}).find_all("a")
    for links in data:
        r1 = session.get("https://order.citybbq.com"+links['href'], headers=headers)
        soup1 = BeautifulSoup(r1.text, "lxml")
        info = soup1.find_all("li",{"class":"vcard"})

        for location in info:
            
            location_name = location.find("span",{"class":"fn org"}).text.strip()
            street_address = location.find("span",{"class":"street-address"}).text.strip()
            city = location.find("span",{"class":"locality"}).text.strip()
            state = location.find("span",{"class":"region"}).text.strip()
            phone =  location.find("div",{"class":"location-tel-number"}).text.strip()
            hours_of_operation = location.find("span",{"class":"location-hours"}).text.replace("\r\n","").replace("         "," ").strip() +" "+ location.find("span",{"class":"location-delivery-info"}).text.replace("\r\n","").replace("         "," ").strip()
            latitude = location.find("span",{"class":"latitude"}).find("span")['title']
            longitude = location.find("span",{"class":"longitude"}).find("span")['title']
            page_url = location.find("a")['href']

            r2 = session.get(page_url, headers=headers)
            soup2 = BeautifulSoup(r2.text, "lxml")
            json_data = json.loads(soup2.find(lambda tag: (tag.name == "script") and "OLO.Analytics.addEventProperties" in tag.text).text.split("(")[1].split(")")[0].replace("'",'"'))
            zipp = json_data['Store Postal Code']
            store_number = json_data['Store Number']

            store = []
            store.append(base_url)
            store.append(location_name if location_name else '<MISSING>')
            store.append(street_address if street_address else '<MISSING>')
            store.append(city if city else '<MISSING>')
            store.append(state if state else '<MISSING>')
            store.append(zipp if zipp else '<MISSING>')
            store.append('US')
            store.append(store_number if store_number else '<MISSING>')
            store.append(phone if phone else '<MISSING>')
            store.append('<MISSING>')
            store.append(latitude if latitude else '<MISSING>')
            store.append(longitude if longitude else '<MISSING>')
            store.append(hours_of_operation if hours_of_operation else '<MISSING>')
            store.append(page_url)
            # print("data ====="+str(store))
            yield store

def scrape():
    data = fetch_data()
    write_output(data)


scrape()

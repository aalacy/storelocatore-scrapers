# coding=UTF-8
import csv
from bs4 import BeautifulSoup
import re
import json
import time
from sgrequests import SgRequests
import requests

session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8", newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    locator_domain = "https://gallogiro.com/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}
    r= session.get("https://gallogiro.com/locations.html",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    for a in soup.find_all("a",class_="can"):
        page_url = "https://gallogiro.com/locations.html"
        city = a.text.strip()
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        location_name = "Mexican restaurant"
        r_loc = session.get(a["href"],headers=headers)
        soup_loc = BeautifulSoup(r_loc.text,"lxml")
        data = soup_loc.find(lambda tag: (tag.name == "script") and "window.APP_OPTIONS" in tag.text).text
        # print(data.split("APP_INITIALIZATION_STATE=")[1].split("]")[0])
        latitude = data.split("APP_INITIALIZATION_STATE=")[1].split("]")[0].split(",")[1]
        longitude = data.split("APP_INITIALIZATION_STATE=")[1].split("]")[0].split(",")[-1]
        try:
            address = data.split('El Gallo Giro')[2].split('El Gallo Giro')[0]
            address1 = address.split('http://www.google.com.mx/search?q')[0].split(",[")[-3].split("\n")[0].replace("]\\n,null","").replace('\\"','')
            street_address = address1.split(",")[0].strip()
            state = address1.split(",")[-2].split()[0]
            zipp = address1.split(",")[-2].split()[-1]
            phone_tag= data.split("tel:")[1].split(",")[0]
            phone = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(phone_tag))[0]
            hours = data.split("martes")[1].split('https://')[0].split(",")
            days = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
            hour_list =[]
            for i in hours:
                if ":" in i and "–"  in i :
                    hour_list.append(i.replace("[","").replace("]","").replace("\\n","").replace("\\","").replace('"',""))
            final_hours_list = []
            for i in range(len(days)):
                final_hours_list.append(days[i]+" : "+hour_list[i])
            hours_of_operation = "  ".join(final_hours_list)
            
            
        except:
            street_address = "701 E Jefferson Blvd"
            state= "CA"
            zipp = "90011"
            phone = "3232333623"
            hours_of_operation = "Sunday : 7:00–21:00   Monday : 7:00–21:00    Tuesday : 7:00–21:00    Wednesday : 7:00–21:00    Thursday : 7:00–21:00   Friday : 7:00–21:00   Saturday : 7:00–21:00"
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
						store_number, phone, location_type, latitude, longitude, hours_of_operation.replace("–","-"), page_url]
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        yield store
        # print(store)


def scrape():
    data = fetch_data()
    write_output(data)
scrape()

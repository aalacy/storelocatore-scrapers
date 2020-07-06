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
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    page_url1 = "http://www.lumberjacksrestaurant.com"
    base_url= "http://www.lumberjacksrestaurant.com/locations/"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    data_phone = soup.find("a")['href']
    dic1 = {}
    data = (soup.text.split('map_locations = ')[1].split(",null,null,null,null,null,null")[0].replace('id":2579,"image":"http:\/\/www.lumberjacksrestaurant.com\/wp-content\/uploads\/2016\/12\/icon-location-3.png"}','id":2579,"image":"http:\/\/www.lumberjacksrestaurant.com\/wp-content\/uploads\/2016\/12\/icon-location-3.png"}]'))
    for q in soup.find_all("span",{"style":"color: black;"}):
        name =q.find("strong").text.strip()
        phone = q.find("a").text.strip()
        dic1[name] =phone
    json_data = json.loads(data)
    data_8 = (json_data)
    for i in data_8 :
        locator_domain = page_url1
        street_address = (i['name']).split(",")[0]
        city = i['name'].split(",")[1].strip().replace("North Las Vegas","Las Vegas")
        state = i['name'].split(",")[2].split(" ")[-2]
        zipp = i['name'].split(",")[2].split(" ")[-1]
        latitude = i['lat']
        longitude = i['lng']
        store_number = i['id']
        country_code = i['name'].split(",")[-1].strip()
        data_new  = str(city).upper()+", "+str(state).upper()
        location_name = "LUMBERJACKS RESTAURANT - "+str(city).upper()+","+str(state).upper()
        page_url = ('http://www.lumberjacksrestaurant.com/lumberjacks-'+str(city)+"/").replace(" ","-").lower()
        if "95490" in zipp or "95945" in zipp or "95219" in zipp or "89032" in zipp:
            hours_of_operation = "Sun - Sat 7 am to 10 pm"
        elif "95841" in zipp or "94952" in zipp or "96130" in zipp:
            hours_of_operation = "Sun - Sat 6 am to 10 pm"
        else:
            hours_of_operation = "Sun - Thur 6 am to 10 pm,Fri - Sat 6 am to 11 pm"
        if "89032" in zipp:
            hours_of_operation = hours_of_operation.replace("10","3")
        store=[]
        store.append(page_url1 if page_url1 else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append(country_code if country_code else '<MISSING>')
        store.append(store_number if store_number else '<MISSING>')
        store.append(dic1[data_new] if dic1[data_new] else '<MISSING>')
        store.append('<MISSING>')
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')
        store.append(hours_of_operation  if hours_of_operation else '<MISSING>')
        store.append(page_url if page_url else '<MISSING>')
        yield store 
def scrape():
    data = fetch_data()
    write_output(data)
scrape()



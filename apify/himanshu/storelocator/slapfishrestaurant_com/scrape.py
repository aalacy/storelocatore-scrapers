import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', newline= '') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    url = "https://www.slapfishrestaurant.com/locations/storelist"
    payload = "latitude=33.5973469&longitude=-112.1072528&range=2500&search_by_state="
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,pt;q=0.8',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': 'PHPSESSID=buikagjj7q4ugik0rb15ko84s5; _ga=GA1.2.1093626883.1599738803; _gid=GA1.2.1116822427.1599738803; _gat=1; _fbp=fb.1.1599738805287.642293938; PHPSESSID=1nmanf1bpl3sd9r7in8hh6cp04',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    response = session.post(url, headers=headers, data = payload).json()
    data_main = (response['data'])
    for i in data_main:
        city = (i['location'].split("</br>")[1].strip().split(",")[0])
        state = (i['location'].split("</br>")[1].strip().split(",")[1].strip().split(" ")[0])
        zipp = (i['location'].split("</br>")[1].strip().split(",")[1].strip().split(" ")[1])
        street_address = i['location'].split("</br>")[0].replace(",","")
        phone = (i['phone'])
        location_name = i['title']
        lat = i['latitude']
        lng = i['longitude']
        hour = i['hours']
        page_url = i['url']
        base_url = "https://www.slapfishrestaurant.com"
        store=[]
        store.append(base_url)
        store.append(location_name if location_name else "<MISSING>")
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")
        store.append("US")
        store.append("<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append("<MISSING>")
        store.append(lat if lat else "<MISSING>")
        store.append(lng if lng else "<MISSING>")
        store.append(str(hour).replace("</li>"," ").replace("<li>","").replace('<li class="active">',"").strip() if hour else "<MISSING>")
        store.append(page_url if page_url.strip() else "<MISSING>")
        if "123 test test" in street_address:
            continue
        yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()

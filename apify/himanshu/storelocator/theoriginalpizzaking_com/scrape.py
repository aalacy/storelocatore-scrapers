import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import time

def write_output(data):
 with open('data.csv', mode='w') as output_file:
    writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
    # Header
    writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code","store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
    # Body
    for row in data:
        writer.writerow(row)

def request_wrapper(url,method,headers,data=None):
   request_counter = 0
   if method == "get":
       while True:
           try:
               r = requests.get(url,headers=headers)
               return r
               break
           except:
               time.sleep(2)
               request_counter = request_counter + 1
               if request_counter > 10:
                   return None
                   break
   elif method == "post":
       while True:
           try:
               if data:
                   r = requests.post(url,headers=headers,data=data)
               else:
                   r = requests.post(url,headers=headers)
               return r
               break
           except:
               time.sleep(2)
               request_counter = request_counter + 1
               if request_counter > 10:
                   return None
                   break
   else:
       return None
def fetch_data():
    address = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    base_url = "https://theoriginalpizzaking.com"
    location_url = "https://storerocket.global.ssl.fastly.net/api/user/3MZpoQ2JDN/locations?radius=10"
    r = request_wrapper(location_url,"get",headers=headers)
    json_data = r.json()
    for i in json_data['results']['locations']:

# "id": 1500396,
#         "name": "Pizza King Americus",
#         "address": "7506 25 North State Street, Lafayette, Indiana, 47905, United States",
#         "phone": "7655898244",
#         "email": "",
#         "url": "",
#         "lat": "40.5264198",
#         "lng": "-86.7580393",
#         "visible": 1,
#         "marker_id": null,
#         "display_address": "7506 25 North State Street, Lafayette, Indiana, 47905, United States",
#         "address_line_1": "7506 25 North State Street",
#         "address_line_2": "",
#         "city": "Lafayette",
#         "state": "Indiana",
#         "postcode": "47905",
#         "country": "United States",
#         "location_type_id": 2154,
#         "timezone": "America/Indiana/Winamac",
#         "yelp_data": null,
#         "facebook": null,
#         "instagram": null,
#         "twitter": null,
#         "yelp_id": null,
#         "priority": 1,
#         "location_type_name": "Standard",
#         "location_type_show_label": 0,
#         "mon": null,
#         "tue": null,
#         "wed": null,
#         "thu": null,
#         "fri": null,
#         "sat": null,
#         "sun": null,
#         "marker_image": null,
#         "yelp_rating": null,
#         "yelp_review_count": null,
#         "filters": [],
#         "fields": [],
#         "buttons": [],
#         "images": [],
#         "cover_image": null,
#         "locationType": {
#           "name": "Standard",
#           "priority": 1,
#           "show_label": 0
#         },
#         "marker": {
#           "id": null,
#           "image": null
#         },
#         "hours": {
#           "mon": null,
#           "tue": null,
#           "wed": null,
#           "thu": null,
#           "fri": null,
#           "sat": null,
#           "sun": null
#         },
#         "obf_id": "DMJbvdz6JX"
        store = []
        store.append(base_url if base_url else "<MISSING>")
        store.append(i['name'] if i['name'] else "<MISSING>") 
        store.append(i['address_line_1'] if i['address_line_1'] else "<MISSING>")
        store.append(i['city'] if i['city'] else "<MISSING>")
        store.append(i['state'] if i['state'] else "<MISSING>")
        store.append(i['postcode'] if i['postcode'] else "<MISSING>")
        store.append("United States")
        store.append(i['id'] if i['id'] else "<MISSING>")
        store.append(i['phone'] if i['phone'] else"<MISSING>") 
        store.append("<MISSING>")
        store.append(i['lat'] if i['lat'] else "<MISSING>")
        store.append(i['lng'] if i['lng'] else "<MISSING>")
        store.append("<MISSING>")
        store.append("https://theoriginalpizzaking.com/additional-pizza-king-locations/")
        if store[2] in address :
            continue
        address.append(store[2])
        yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()


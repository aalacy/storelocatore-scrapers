import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    adressess = []
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': 'PHPSESSID=miahqdtr2q6h4ni622800h7ig5; Rossy_lang=En; _ga=GA1.2.1497936504.1599040884; _gid=GA1.2.331653320.1599040884; _fbp=fb.1.1599040884656.569999714; _gat_gtag_UA_85203089_2=1; Rossy_lastPageViewed=1599128426; PHPSESSID=0j3hff3p0hpmrjj84vhirref61; Rossy_lang=En; Rossy_lastPageViewed=1599128522',
        'Referer': 'https://www.rossy.ca/en/store-finder/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
        }

    payload = "/ajax/ajaxcall.php?langID=1&do=getLocations&q=E1c5a3&distance=10000&units=km"
    base_url = "https://rossy.ca"
    location_url = "https://www.rossy.ca/ajax/store-finder.php?langID=1&"

    r = session.post(location_url,data=payload,headers=headers)
    r.encoding='utf-8-sig'
    
    json_data = json.loads(r.json()['stores'])
    for value in json_data:
        location_name = value['city']+"("+value['store']+")"
        try:
            street_address = value['address'] +" "+value['address2']
        except:
            street_address = value['address']
        city = value['city']
        state = value['province']
        zipp = value['postalCode']
        country_code = value['country']
        store_number = value['store']
        temp_phone = value['telephone']
        phone = temp_phone[:3]+"-"+temp_phone[3:6]+"-"+temp_phone[6:]
        location_type = "<MISSING>"
        latitude = value['latitude']
        longitude = value['longitude']
        hours_of_operation = "Monday: "+value['mondayHours']+",Tuesday: "+value['tuesdayHours']+",Wednesday: "+value['wednesdayHours']+",Thursday: "+value['thursdayHours']+",Friday: "+value['fridayHours']+",Saturday: "+value['saturdayHours']+",Sunday: "+value['sundayHours']
        page_url = "<MISSING>"

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
        store.append(latitude)
        store.append(longitude)
        store.append(hours_of_operation)
        store.append("<MISSING>")
        if store[2] in adressess:
            continue
        adressess.append(store[2])
        store = [str(x).strip() if x else "<MISSING>" for x in store]
        yield store



def scrape():
   
    data = fetch_data()
    write_output(data)

scrape()

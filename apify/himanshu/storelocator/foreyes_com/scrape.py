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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://www.foreyes.com"
    data = "action=get_properties&lat=39.8283459&lng=-98.5794797&dist=5000&queryType=distance&term=false"
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
        'X-Requested-With': 'XMLHttpRequest',
        'Host': 'www.foreyes.com',
        'Referer': 'https://www.foreyes.com/locations/',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }

    r = session.post(base_url + "/wp-admin/admin-ajax.php",data=data,headers=headers)
    data = r.json()['properties']
    return_main_object = []
    for i in range(len(data)):
        store_data = data[i]
        store = []
        store.append("https://www.foreyes.com ")
        store.append(store_data['name'].split(";")[1])
        store.append(store_data["address1"])
        store.append(store_data['city'])
        store.append(store_data['state'])
        store.append(store_data["zip"])
        store.append("US")
        store.append(store_data['id'])
        store.append(store_data['phoneStripped'])
        store.append("for eyes")
        store.append(store_data["maps"]['lat'])
        store.append(store_data["maps"]['lng'])
        hours = ""
        if store_data["monday_open"] and store_data["monday_open"] != "":
            hours = hours + " Monday open time " + store_data["monday_open"] +" Monday close time " + store_data["monday_close"] + " "
        if store_data["tuesday_open"] and store_data["tuesday_open"] != "":
            hours = hours + " tuesday open time " + store_data["tuesday_open"] +" tuesday close time " + store_data["tuesday_close"] + " "
        if store_data["wednesday_open"] and store_data["wednesday_open"] != "":
            hours = hours + " wednesday open time " + store_data["wednesday_open"] +" wednesday close time " + store_data["wednesday_close"] + " "
        if store_data["thursday_open"] and store_data["thursday_open"] != "":
            hours = hours + " thursday open time " + store_data["thursday_open"] +" thursday close time " + store_data["thursday_close"] + " "
        if store_data["friday_open"] and store_data["friday_open"] != "":
            hours = hours + " friday open time " + store_data["friday_open"] +" friday close time " + store_data["friday_close"] + " "
        if store_data["saturday_open"] and store_data["saturday_open"] != "":
            hours = hours + " saturday open time " + store_data["saturday_open"] +" saturday close time " + store_data["saturday_close"] + " "
        if store_data["sunday_open"] and store_data["sunday_open"] != "":
            hours = hours + " sunday open time " + store_data["sunday_open"] +" sunday close time " + store_data["sunday_close"] + " "
        if hours == "":
            hours = "<MISSING>"
        store.append(hours)
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

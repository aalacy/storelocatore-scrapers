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
    base_url = "https://www.fnb-online.com"
    r = session.get("https://code.metalocator.com/index.php?option=com_locator&view=directory&force_link=1&tmpl=component&task=search_zip&framed=1&format=raw&no_html=1&templ[]=address_format&layout=_jsonfast&postal_code=40.588928169693745,-78.6181640625&radius=nearest&interface_revision=871&user_lat=0&user_lng=0&Itemid=6740&parent_table=&parent_id=0&search_type=point&_opt_out=&option=com_locator&ml_location_override=&reset=false&nearest=false&callback=handleJSONPResults")
    data = json.loads(r.text.split("handleJSONPResults(")[1][0:-2])['results']
    return_main_object = []
    for i in range(len(data)):
        store = []
        print(data[i]["id"])
        url = "https://code.metalocator.com/index.php?option=com_locator&view=location&tmpl=component&task=load&framed=1&format=json&templ[]=map_address_template&sample_data=&lang=&_opt_out=&Itemid=6740&numbe%20r=7&id="+ str(data[i]["id"]) +"&_urlparams="
        location_request = session.get(url)
        store_data = location_request.json()[0]
        store.append("https://www.fnb-online.com")
        store.append(store_data['name'])
        store.append(store_data["address"] + store_data["address2"] if store_data['address2'] != None else store_data["address"])
        store.append(store_data['city'])
        store.append(store_data['state'])
        store.append(store_data["postalcode"])
        store.append("US")
        store.append(store_data['id'])
        store.append(store_data['phone'] if store_data['phone'] != "" and store_data['phone'] != None else "<MISSING>")
        store.append("fnb " + store_data["locationtype"] if "locationtype" in store_data and  store_data["locationtype"] != None else "fnb")
        store.append(store_data["lat"])
        store.append(store_data["lng"])
        hours = ""
        if "hours" in store_data and store_data["hours"] != None:
            hours = store_data['hours'].replace("{"," ").replace("}"," ").replace("-"," to ")
        elif "atmhours" in store_data:
            hours = store_data["atmhours"]
        if hours == "" and hours == None:
            hours = "<MISSING>"
        store.append(hours)
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

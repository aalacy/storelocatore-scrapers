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
    base_url = "https://www.ditchwitch.com"
    r = session.post(base_url + "/find-a-dealer")
    soup = BeautifulSoup(r.text,"lxml")
    data = json.loads(soup.find("div",{"id":"find-a-dealer-page-results-list"})["data-dealers"])
    return_main_object = []
    for i in range(len(data)):
        store_data = data[i]
        store = []
        store.append("https://www.ditchwitch.com")
        store.append(store_data['name'])
        store.append(store_data["address1"])
        store.append(store_data['city'])
        state = store_data['state']
        if state == "":
            state = store_data['province'].split(",")[0]
        store.append(state if state != "" else "<MISSING>")
        if store_data["country"] == "CA":
            if len(store_data["postalcode"].split(" ")) >= 2:
                store.append(store_data["postalcode"])
            else:
                store.append(store_data["postalcode"][:3]+ " " + store_data["postalcode"][3:] )
        else:
            store.append(store_data["postalcode"])
        store.append(store_data["country"])
        store.append(store_data["id"] if store_data["id"] != "" else "<MISSING>")
        store.append(store_data['phone'])
        store.append("ditch witch")
        store.append(store_data["latitude"])
        store.append(store_data["longitude"])
        hours = ""
        if store_data["mon_open"] and store_data["mon_open"] != "Closed":
            hours = hours + " Monday open time " + store_data["mon_open"] +" Monday close time " + store_data["mon_close"] + " "
        if store_data["tue_open"] and store_data["tue_open"] != "Closed":
            hours = hours + " tuesday open time " + store_data["tue_open"] +" tuesday close time " + store_data["tue_close"] + " "
        if store_data["wed_open"] and store_data["wed_open"] != "Closed":
            hours = hours + " wednesday open time " + store_data["wed_open"] +" wednesday close time " + store_data["wed_close"] + " "
        if store_data["thur_open"] and store_data["thur_open"] != "Closed":
            hours = hours + " thursday open time " + store_data["thur_open"] +" thursday close time " + store_data["thur_close"] + " "
        if store_data["fri_open"] and store_data["fri_open"] != "Closed":
            hours = hours + " friday open time " + store_data["fri_open"] +" friday close time " + store_data["fri_close"] + " "
        if store_data["sat_open"] and store_data["sat_open"] != "Closed":
            hours = hours + " saturday open time " + store_data["sat_open"] +" saturday close time " + store_data["sat_close"] + " "
        if store_data["sun_open"] and store_data["sun_open"] != "Closed":
            hours = hours + " sunday open time " + store_data["sun_open"] +" sunday close time " + store_data["sun_close"] + " "
        if hours == "":
            hours = "<MISSING>"
        store.append(hours)
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

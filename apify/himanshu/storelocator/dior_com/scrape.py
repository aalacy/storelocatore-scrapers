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

def handle_result(store_data):
    store = []
    store.append("https://www.dior.com")
    store.append(store_data['defaultName'])
    store.append(store_data["defaultStreet1"] + store_data["defaultStreet2"] if "defaultStreet2" in store_data else store_data["defaultStreet1"])
    store.append(store_data['defaultCity'])
    store.append(store_data['state'] if 'state' in store_data else "<MISSING>")
    if store_data["countryCode"] == "US":
        store.append(store_data["defaultZipCode"].replace("Â ","").split(" ")[-1] if store_data["countryCode"] == "US" else store_data["defaultZipCode"].upper())
    else:
        store.append(store_data["defaultZipCode"].replace("Â ","") if store_data["countryCode"] == "US" else store_data["defaultZipCode"].upper())
    store.append(store_data["countryCode"])
    store.append("") # i will set the id later
    store.append(store_data["phoneNumber"].replace("Â","") if "phoneNumber" in store_data else "<MISSING>")
    store.append("dior")
    store.append(store_data["lat"])
    store.append(store_data["lng"])
    hours = ""
    open_hours = store_data["openingHours"]
    days = {"1": "Monday","2":"Tuesday","3":"Wednesday","4":"Thursday","5":"Friday","6":"Saturday","0":"Sunday"}
    for k in range(len(open_hours)):
        if open_hours[k] == []:
            continue
        hours = hours + " " + days[str(k)] + " from " + open_hours[k][0]["from"] + " end " + open_hours[k][0]["to"]
    store.append(hours if hours != "" else "<MISSING>")
    return store

def fetch_data():
    base_url = "https://www.dior.com"
    r = session.get(base_url + "/store/json/posG.json")
    data = r.json()["items"]
    return_main_object = []
    for i in range(0,len(data),100):
        print(i)
        url = "https://tpc33of0na.execute-api.eu-west-1.amazonaws.com/prod/PointOfSale?ids="
        temp_number = i + 100
        if i + 100 > len(data):
            temp_number = len(data)
        print(str(temp_number) + "========")
        for j in range(i,temp_number):
            url = url + data[j][0] + ","
        url = url[:-1]
        location_reqeust = session.get(url)
        try:
            location_data = location_reqeust.json()["Items"]
            for j in range(len(location_data)):
                if location_data[j]["countryCode"] == "US" or location_data[j]["countryCode"] == "CA":
                    store = handle_result(location_data[j])
                    store[7] = data[i+j][0]
                    return_main_object.append(store)
        except:
            for m in range(i,i+100):
                print(m)
                url = "https://tpc33of0na.execute-api.eu-west-1.amazonaws.com/prod/PointOfSale?ids=" + str(data[i])
                location_reqeust = session.get(url)
                try:
                    location_data = location_reqeust.json()["Items"]
                    for j in range(len(location_data)):
                        if location_data[j]["countryCode"] == "US" or location_data[j]["countryCode"] == "CA":
                            store = handle_result(location_data[j])
                            store[7] = data[i+m][0]
                            return_main_object.append(store)
                except:
                    continue
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

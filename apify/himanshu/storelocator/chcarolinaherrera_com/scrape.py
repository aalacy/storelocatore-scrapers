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
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://chcarolinaherrera.com"
    r = session.post("https://chcarolinaherrera.com/00/en/storelocator",headers=headers)
    return_main_object = []
    soup = BeautifulSoup(r.text,"lxml")
    # data_11 = (soup.find("datalist",{"data-country-id":"US"}).find_all("option"))
    # for g in data_11:
    #     state = (g.text)
    for location in soup.find("datalist",{"data-country-id":"US"}).find_all("option"):
        state = (location.text)
        state_request = session.get("https://chcarolinaherrera.com/STLStoreLocatorJSONDisplayView?catalogId=3074457345616676668&langId=-1002&storeId=715838508&country=US&state=" + str(location["value"]) + "&searchTerm=" ,headers=headers)
        state_soup = BeautifulSoup(state_request.text,"lxml")
        file1 = open("myfile1.txt","w")
        file1.write(state_soup.find("script").text.split("STL.storeArray = ")[1].split("];")[0] + "]")
        data = state_soup.find("script").text.split("STL.storeArray = ")[1].split("];")[0] + "]"
        location_list1 = (data.replace("'",'"').replace('""','"').replace('"extCountry": ",','"extCountry": "",').replace('"info":",','"info":"",').replace('"emailTo" : ",','"emailTo" : "",'))
        location_list = json.loads(location_list1)
        # print(location_list)
        for i in range(len(location_list)):
            store_data = location_list[i]
            store = []
            store.append("https://chcarolinaherrera.com")
            store.append(store_data["name"])
            store.append(store_data["address"][0])
            store.append(store_data["address"][1].split(",")[0])
            store.append(state if state else "<MISSING>")
            store.append(store_data["address"][1].strip().split(",")[1].split(" ")[-1])
            store.append("US")
            store.append(store_data["id"])
            store.append(store_data["telf"].strip() if store_data["telf"].strip() != "n/d" else "<MISSING>")
            store.append("<MISSING>")
            store.append(store_data["latitude"])
            store.append(store_data["longitude"])
            store_hours = str(store_data["timetable"]).replace("'}, {'day': '",", ").replace("', 'hours': '"," - ").replace("[","").replace("]","").replace("'","").replace("{","").replace("}","").replace("day: ","")
            # hours = ""
            # for k in range(len(store_hours)):
            #     hours = hours + " " + store_hours[i]["day"] + " " + store_hours[i]["hours"]
            store.append(store_hours if store_hours != "" else "<MISSING>")
            store.append("<MISSING>")
            return_main_object.append(store)
    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)
scrape()

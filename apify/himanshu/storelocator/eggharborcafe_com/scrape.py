import csv
import requests
from bs4 import BeautifulSoup
import re
import json

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.eggharborcafe.com"
    r = requests.get("https://www.eggharborcafe.com/our-locations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    data = '{"method":"GetLocationLocator","format":"json","parameters":"ProjectID=426a38a2-fa10-46f6-8a17-92eba6dc1d78&SitePageModuleID=400130f7-f75d-439f-9c49-3e064675db80&Latitude=39.5&Longitude=-98.35","typefields":[{"DataType":"LocationLocatorRow","Columns":"*"}],"host":"websiteoutput","params":"ProjectID=426a38a2-fa10-46f6-8a17-92eba6dc1d78&SitePageModuleID=400130f7-f75d-439f-9c49-3e064675db80&Latitude=39.5&Longitude=-98.35"}'
    json_data_headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
        "Content-Type": "application/json"
    }
    json_data = requests.post("https://websiteoutputapi.mopro.com/WebsiteOutput.svc/api/get",headers=json_data_headers,data=data)
    data = json_data.json()[1]["rows"]
    geo_object = {}
    for i in range(len(data)):
        geo_object[data[i]["Address"].replace("<br />",", ")] = [data[i]["Latitude"],data[i]["Longitude"]]
    for state in soup.find_all("div",{"class":"art-reward-points"}):
        if state.find("a") == None:
            continue
        state_request = requests.get("https:" + state.find("a")["href"],headers=headers)
        state_soup = BeautifulSoup(state_request.text,"lxml")
        for link in state_soup.find_all("a",text="Details"):
            location_request = requests.get(link["href"],headers=headers)
            lcoation_soup = BeautifulSoup(location_request.text,"lxml")
            location_details = []
            for details in lcoation_soup.find("table",{"class":"full"}).find_all("tr"):
                location_details.append(list(details.stripped_strings)[1:])
            store = []
            store.append("https://www.eggharborcafe.com")
            store.append(location_details[0][0])
            store.append(" ".join(location_details[0][1:-1]) if len(location_details[0]) == 3 else " ".join(location_details[0][0:-1]))
            store.append(location_details[0][-1].split(",")[0])
            store.append(location_details[0][-1].split(",")[1].split(" ")[-2])
            store.append(location_details[0][-1].split(",")[1].split(" ")[-1])
            store.append("US")
            store.append("<MISSING>")
            store.append(location_details[1][0])
            store.append("egg harbor cafe")
            store.append(geo_object[store[2]][0])
            store.append(geo_object[store[2]][1])
            store.append(" ".join(location_details[-1]))
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

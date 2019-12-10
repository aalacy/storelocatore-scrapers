import csv
import requests
from bs4 import BeautifulSoup
import re
import json


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.eggharborcafe.com"
    r = requests.get(
        "https://www.eggharborcafe.com/our-locations", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    data = '{"method":"GetLocationLocator","format":"json","parameters":"ProjectID=426a38a2-fa10-46f6-8a17-92eba6dc1d78&SitePageModuleID=400130f7-f75d-439f-9c49-3e064675db80&Latitude=39.5&Longitude=-98.35","typefields":[{"DataType":"LocationLocatorRow","Columns":"*"}],"host":"websiteoutput","params":"ProjectID=426a38a2-fa10-46f6-8a17-92eba6dc1d78&SitePageModuleID=400130f7-f75d-439f-9c49-3e064675db80&Latitude=39.5&Longitude=-98.35"}'
    json_data_headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
        "Content-Type": "application/json"
    }
    json_data = requests.post(
        "https://websiteoutputapi.mopro.com/WebsiteOutput.svc/api/get", headers=json_data_headers, data=data)
    data = json_data.json()[1]["rows"]
    geo_object = {}
    c1 = []
    c2 = []
    for i in range(len(data)):
        geo_object[data[i]["Address"].replace(
            "<br />", ", ")] = [data[i]["Latitude"], data[i]["Longitude"]]
        c1.append(geo_object[data[i]["Address"].replace(
            "<br />", ", ")][0])
        c2.append(geo_object[data[i]["Address"].replace(
            "<br />", ", ")][1])
    for state in soup.find_all("div", {"class": "art-reward-points"}):
        if state.find("a") == None:
            continue
        state_request = requests.get(
            "https:" + state.find("a")["href"], headers=headers)
        state_soup = BeautifulSoup(state_request.text, "lxml")
        for link in state_soup.find_all("a", text="Details"):
            location_request = requests.get(link["href"], headers=headers)
            lcoation_soup = BeautifulSoup(location_request.text, "lxml")
            location_details = []
            for details in lcoation_soup.find("table", {"class": "full"}).find_all("tr"):
                location_details.append(list(details.stripped_strings)[1:])
            # print(location_details[0][-1].split(","))
            if len(location_details[0][-1].split(",")) > 1:
                city = location_details[0][-1].split(",")[0]
                state = location_details[0][-1].split(",")[1].split(" ")[-2]
                zipp = location_details[0][-1].split(",")[1].split(" ")[-1]
            else:
                city = location_details[0][0]
                state = location_details[0][-1].split(",")[0].split(" ")[-2]
                zipp = location_details[0][-1].split(",")[0].split(" ")[-1]
            if c1 != []:
                latitude = c1.pop(0)
            if c2 != []:
                longitude = c2.pop(0)
            # print(city, state, zipp)

            store = []
            store.append("https://www.eggharborcafe.com")
            store.append(location_details[0][-1].split(",")[0])
            store.append(" ".join(location_details[0][1:-1]) if len(
                location_details[0]) == 3 else " ".join(location_details[0][0:-1]))
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append("US")
            store.append("<MISSING>")
            store.append(location_details[1][0])
            store.append("<MISSING>")
            store.append(latitude)
            store.append(longitude)
            store.append(" ".join(location_details[-1]))
            store.append("https://www.eggharborcafe.com/our-locations")
            # print("data == " + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

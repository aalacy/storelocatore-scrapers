import csv
import requests
from bs4 import BeautifulSoup
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
    base_url = "http://lakecountyil.gov"
    r = requests.get("http://lakecountyil.gov/facilities",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    typeids = ""
    for FacilityType in soup.find_all("input",{"name":"FacilityType"}):
        typeids = typeids + str(FacilityType["value"]) + ","
    typeids = typeids[:-1]
    data = "featureIDs=&categoryIDs=" + typeids + "&occupants=null&keywords=&pageSize=1000&pageNumber=1&sortBy=3&currentLatitude=null&currentLongitude=null&isReservableOnly=false"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
    }
    store_request = requests.post("http://lakecountyil.gov/Facilities/Facility/Search",headers=headers,data=data)
    store_soup = BeautifulSoup(store_request.text,"lxml")
    for location in store_soup.find_all("a",{"class":"thumb"}):
        location_request = requests.get(base_url + location["href"])
        location_soup = BeautifulSoup(location_request.text,"lxml")
        name = location_soup.find("div",{"class":"sidebar"}).find("h4").text
        address = location_soup.find("div",{"class":"sidebar"}).find("span",{"class":"street-address"}).text
        locality = location_soup.find("div",{"class":"sidebar"}).find("span",{"class":"locality"}).text
        store_zip = location_soup.find("div",{"class":"sidebar"}).find("span",{"class":"postal-code"}).text
        if location_soup.find("div",{'class':"section hours"}) == None:
            hours = "<MISSING>"
        else:
            hours = " ".join(list(location_soup.find("div",{'class':"section hours"}).stripped_strings))
        if location_soup.find("div",{"class":"sidebar"}).find("h4",text="Contact") == None:
            phone = "<MISSING>"
        else:
            phone = list(location_soup.find("div",{"class":"sidebar"}).find("h4",text="Contact").parent.stripped_strings)[-1].replace("Phone:","")
        store_data = json.loads(location_soup.find("input",{"id":"hdn_MapSearchResults"})["value"])[0]
        store = []
        store.append("https://lakecountyil.gov")
        store.append(name)
        store.append(address)
        store.append(locality.split(",")[0].replace("  ",""))
        store.append(locality.split(",")[1])
        store.append(store_zip)
        store.append("US")
        store.append(store_data["ID"])
        store.append(phone)
        store.append("lake county")
        store.append(store_data["Latitude"])
        store.append(store_data["Longitude"])
        store.append(hours)
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

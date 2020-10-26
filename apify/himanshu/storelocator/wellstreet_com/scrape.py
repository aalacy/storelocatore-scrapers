import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8", newline='') as output_file:
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
    base_url = "https://www.wellstreet.com"
    r = session.get("https://www.wellstreet.com/region/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    region_links = []
    for url in soup.find("main",{"id":'main'}).find_all("a"):
        if url['href'] not in region_links:
            region_links.append(url["href"])
    store_name = []
    for i in range(len(region_links)):
        region_request = session.get(base_url + region_links[i],headers=headers)
        region_soup = BeautifulSoup(region_request.text,"lxml")
        for location in region_soup.find_all("div",{'class':"map-list-item"}):
            if location.find("div",{"class":'phone-line'}) == None:
                continue
            title = location.find("a").text
            if title in store_name:
                continue
            store_name.append(title)
            phone = location.find("div",{"class":'phone-line'}).text
            location_url = location.find("a")["href"]
            location_request = session.get(location_url,headers=headers)
            location_soup = BeautifulSoup(location_request.text.replace("</html>"," "),"lxml")
            try:
                hours = " ".join(list(location_soup.find('div',{"class":"hours"}).stripped_strings))
            except:
                # print(location_url)
                continue
            if "This facility" in hours:
                hours = "<MISSING>"
            address = list(location_soup.find("span",{"class":"address-text"}).stripped_strings)
            if "Get Directions" in address[-1]:
                del address[-1]
            street_address = " ".join(address[:-1])
            city = " ".join(address[-1].split(" ")[:-2])
            state = address[-1].split(" ")[-2]
            zipp = address[-1].split(" ")[-1]

            lat = ""
            lng = ""
            for script in location_soup.find_all("script"):
                if "map =" in script.text:
                    lat = script.text.split("new google.maps.LatLng(")[1].split(",")[0]
                    lng = script.text.split("new google.maps.LatLng(")[1].split(",")[1].split(")")[0]

            store = []
            store.append("https://www.wellstreet.com")
            store.append(title)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append("US")
            store.append("<MISSING>")
            store.append(phone)
            store.append("<MISSING>")
            store.append(lat if lat != "" else "<MISSING>")
            store.append(lng if lng != "" else "<MISSING>")
            store.append(hours)
            store.append(location_url)
            yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    zips = sgzip.for_radius(50)
    return_main_object = []
    addresses = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    content_id_request = session.get("https://cinemark.com/theatres")
    content_id_soup = BeautifulSoup(content_id_request.text, "lxml")
    for script in content_id_soup.find_all("script"):
        if "var contentId = " in script.text:
            content_id = script.text.split("(")[1].split(")")[0]
    for zip_code in zips:
        base_url = "https://cinemark.com"
        r = session.get("https://cinemark.com/umbraco/surface/theaters/GetTheatersbyText?contentId=" + str(
            content_id) + "&searchText=" + str(zip_code), headers=headers)
        soup = BeautifulSoup(r.text, "lxml")
        if "No participating theatres found near the selected ZIP code." in soup.find("div",{"id": "theaterList"}).text:
            continue
        for location in soup.find("div", {"id": "theaterList"}).find_all("a", {'class': "theaterLink"}):
            location_request = session.get(base_url + location["href"])
            location_soup = BeautifulSoup(location_request.text, "lxml")
            store_data = json.loads(location_soup.find("script", {'type': "application/ld+json"}).text)

            if location_soup.find("div", {'class': "theatreMap"}) is None:
                continue
            if location_soup.find("div", {'class': "theatreMap"}).find("img") is None:
                continue

            geo_location = location_soup.find("div", {'class': "theatreMap"}).find("img")["data-src"].split("pp=")[1].split("&")[0]
            store = []
            store.append("https://cinemark.com")
            store.append(store_data["name"])
            store.append(store_data["address"][0]["streetAddress"])
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
            store.append(store_data["address"][0]["addressLocality"])
            store.append(store_data["address"][0]["addressRegion"])
            store.append(store_data["address"][0]["postalCode"])
            store.append(store_data["address"][0]["addressCountry"])
            store.append("<MISSING>")
            store.append(store_data["telephone"])
            store.append("cinemark")
            store.append(geo_location.split(",")[0])
            store.append(geo_location.split(",")[1])
            store.append("<MISSING>")
            return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

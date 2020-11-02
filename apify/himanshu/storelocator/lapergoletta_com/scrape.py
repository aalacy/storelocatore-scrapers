import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import ast



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding='utf8') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    addresses = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }

    base_url = "http://lapergoletta.com"
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    inner_soup = soup.find("div", {"class": "box bigtitle gk-description gkmod-1"})
    for part in inner_soup.find_all("iframe"):

        full_address_url = part["src"]

        geo_request = session.get(full_address_url, headers=headers)
        geo_soup = BeautifulSoup(geo_request.text, "lxml")
        for script_geo in geo_soup.find_all("script"):
           if "initEmbed" in script_geo.text:
               geo_data = json.loads(script_geo.text.split("initEmbed(")[1].split(");")[0])[21][3][0][1]
               lat = json.loads(script_geo.text.split("initEmbed(")[1].split(");")[0])[21][3][0][2][0]
               lng = json.loads(script_geo.text.split("initEmbed(")[1].split(");")[0])[21][3][0][2][1]

               phone = json.loads(script_geo.text.split("initEmbed(")[1].split(");")[0])[21][3][7]
        hr = list(part.parent.find_next('p').find_next('p').stripped_strings)
        hour = ','.join(map(str, hr))
        location_name = geo_data.split(',')[0]
        street_address =geo_data.split(',')[1]
        city =geo_data.split(',')[2]
        state =geo_data.split(',')[-2].strip().split(" ")[0]
        zipp =geo_data.split(',')[-2].strip().split(" ")[-1]
        latitude = lat
        longitude = lng
        return_object = []
        if street_address in addresses:
            continue
        addresses.append(street_address)
        return_object.append(base_url)
        return_object.append(location_name)
        return_object.append(street_address)
        return_object.append(city)
        return_object.append(state)
        return_object.append(zipp)
        return_object.append("US")
        return_object.append("<MISSING>")
        return_object.append(phone)
        return_object.append("<MISSING>")
        return_object.append(latitude)
        return_object.append(longitude)
        return_object.append(hour)
        return_object.append("<MISSING>")
        return_main_object.append(return_object)

    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)

scrape()

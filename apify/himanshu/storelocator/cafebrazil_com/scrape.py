import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import ast



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }

    base_url = "http://cafebrazil.com"
    r = session.get(base_url +'/locations' , headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for part in soup.find_all("main", {"id": "genesis-content"}):
        temp_storeaddresss = list(part.stripped_strings)

        return_val = []
        main_val =[]
        i = 1
        for x in temp_storeaddresss:
            if(x == '______________________________________________________________________'):
                main_val.append(return_val)
                return_val = []
            elif(i == len(temp_storeaddresss)):
                main_val.append(return_val)
            else:
                return_val.append(x)
            i += 1
            new = 0
        all_loc = part.find_all("a",text=re.compile("Click Here"))

        for inner in  main_val:
            location_name = inner[0]
            url = all_loc[new]['href']
            if('Locations' in inner):
                inner.remove('Locations')
            if(new == 4):
                lat_find = url.split("&sll=")
                lat = lat_find[1].split(",")[0]
                find_lag = lat_find[1].split(",")[1]
                lag = find_lag.split("&")[0]
            else:
                lat_find = url.split("@")
                lat = lat_find[1].split(",")[0]
                lag = lat_find[1].split(",")[1]
            street_address = inner[1].split(",")[0]
            city = inner[1].split(",")[1]
            state_zip = inner[1].split(",")[2]
            state = state_zip.split(" ")[1]
            store_zip = state_zip.split(" ")[2]
            phone_fax = inner[2].split("|")[0]
            phone = phone_fax.split(":")[1]
            hour = inner[3]
            return_object = []
            return_object.append(base_url)
            return_object.append(location_name)
            return_object.append(street_address)
            return_object.append(city)
            return_object.append(state)
            return_object.append(store_zip)
            return_object.append("US")
            return_object.append("<MISSING>")
            return_object.append(phone)
            return_object.append("<MISSING>")
            return_object.append(lat)
            return_object.append(lag)
            return_object.append(hour)
            return_object.append("http://cafebrazil.com/locations/")
            return_main_object.append(return_object)
            new += 1
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

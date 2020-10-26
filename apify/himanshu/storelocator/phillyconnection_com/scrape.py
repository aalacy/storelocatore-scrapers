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
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }

    base_url = "http://phillyconnection.com/"
    r = session.get(base_url +'locations.html' , headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    part = soup.find("table")
    temp_storeaddresss = list(part.stripped_strings)
    return_val = []
    main_val =[]
    i = 1
    for x in temp_storeaddresss:
        if(x == 'MENU'):
            main_val.append(return_val)
            return_val = []
        elif(i == len(temp_storeaddresss)):
            main_val.append(return_val)
        else:
            return_val.append(x)
        i += 1
    for val in main_val:
        if(len(val) == 6):
            del val[0]
        if 'ORDER ONLINE!' in val:
            val.remove('ORDER ONLINE!');
        if 'GEORGIA' in val:
            val.remove('GEORGIA');
        if 'KENTUCKY' in val:
            val.remove('KENTUCKY');
        if "Morningside Center" in val:
            del val[0]
        location_name = val[0]
        phone = val[-1]
        city_state = val[-2]
        city = city_state.split(",")[0]
        state_zip = city_state.split(",")[1]
        state = state_zip.split(" ")[1]
        store_zip = state_zip.split(" ")[2]
        if (len(val) == 5):
            street_address = val[1]+ ' '+val[2]
        else:
          street_address = val[1]
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
        return_object.append("Philly Connection")
        return_object.append("<MISSING>")
        return_object.append("<MISSING>")
        return_object.append("<MISSING>")
        return_main_object.append(return_object)
        # print(return_object)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

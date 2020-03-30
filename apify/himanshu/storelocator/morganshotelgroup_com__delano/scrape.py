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
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    address = []

    return_main_object = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }

    base_url = "https://www.morganshotelgroup.com/delano"
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")


    parts = soup.find("li", {"class": "navregions__region"})
    for in_parts in parts.find_all("li", {"class": "navlocations__location"}):

        store_request = session.get(in_parts.find("a")['href'])
        page_url = in_parts.find("a")['href']
        store_soup = BeautifulSoup(store_request.text, "lxml")
        for semi_parts in store_soup.find_all("div", {"class": "locationinfo__map-address"}):
            return_object = []
            temp_storeaddresss = list(semi_parts.stripped_strings)

            location_name = temp_storeaddresss[0]
            street_address = temp_storeaddresss[1]
            if "," == street_address:
              street_address = "<MISSING>"
              city = "<MISSING>"
              state = "<MISSING>"
              store_zip = "<MISSING>"
            else:
              street_address  = street_address
              city = temp_storeaddresss[2].split(",")[0].strip()
              state =  temp_storeaddresss[2].split(",")[1].split()[0].strip()
              store_zip =  temp_storeaddresss[2].split(",")[1].split()[-1].strip()
            # print(street_address,city,state,store_zip)


            next_sib = store_soup.find("div", {"class": "bd js-mapholder"}).findNext('div',{"class": "js-maplocation-group"})
            for data_title in next_sib.find_all("div", {"class": "js-maplocation","data-title": location_name}):
                lat = data_title['data-lat']
                lag = data_title['data-lng']
            if "0" == lat or "0" == lag:
              lat= "<MISSING>"
              lag = "<MISSING>"






            phone = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(temp_storeaddresss[-1]))[0]


            return_object.append(base_url)
            return_object.append(location_name)
            return_object.append(street_address)
            return_object.append(city)
            return_object.append(state)
            return_object.append(store_zip)
            return_object.append("US")
            return_object.append("<MISSING>")
            return_object.append(phone)
            return_object.append("Sbe devlano")
            return_object.append(lat)
            return_object.append(lag)
            return_object.append("<MISSING>")
            return_object.append(page_url)

            #print("data =="+str(return_object))
            #print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`')
            return_main_object.append(return_object)

        #    Domain are not same
        if(in_parts.find("a")['href'] == "http://www.delanolasvegas.com/"):
           delano_address = store_soup.find("span", {"class": "address-text"})

           return_object = []
           temp_store = list(delano_address.stripped_strings)
           location_name = "Delano"
           street_address = temp_store[0]
           city = temp_store[1].split(",")[0]
           state_zip = temp_store[1].split(",")[1]
           state = state_zip.split(" ")[1]
           store_zip = state_zip.split(" ")[2]
           return_object.append(base_url)
           return_object.append(location_name)
           return_object.append(street_address)
           return_object.append(city)
           return_object.append(state)
           return_object.append(store_zip)
           return_object.append("US")
           return_object.append("<MISSING>")
           return_object.append("<MISSING>")
           return_object.append("Sbe devlano")
           return_object.append("<MISSING>")
           return_object.append("<MISSING>")
           return_object.append("<MISSING>")
           return_object.append(page_url)
           #print("data =="+str(return_object))
           #print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`')
           return_main_object.append(return_object)
    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)

scrape()

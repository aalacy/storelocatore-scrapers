import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    addresses = []
    base_url = "http://www.chilis.ca"

    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = "US"
    store_number = ""
    phone = ""
    location_type = ""
    latitude = ""
    longitude = ""
    raw_address = ""
    hours_of_operation = ""
    page_url = ""

    r = session.get("http://www.chilis.ca/locations/locations.cfm", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    for script in soup.find_all("a", {"class": re.compile("btn-map")}):
        # print("location_url === " + str(script["id"]))
        location_url = "http://www.chilis.ca/skins/chilis/js/" + script["id"].replace("link-", "") + ".js"
        
        print("location_url === " + location_url)
        r_location = session.get(location_url, headers=headers)
        soup_location = BeautifulSoup(r_location.text, "lxml")

        # print(soup_location)

        split_location = soup_location.text.split("var marker")

        for single_location in split_location[1:]:

            latitude = single_location.split("new google.maps.LatLng(")[1].split(",")[0]
            longitude = single_location.split("new google.maps.LatLng(")[1].split(",")[1].split(")")[0]
            address_list = single_location.split("createInfo(")[1].split("});")[0].strip().replace("\n", "").replace(
                "\t", "").replace("\r", "").replace('"', "").split(",")

            phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(" ".join(address_list)))
            if phone_list:
                phone = phone_list[0]
            else:
                phone = ""

            index_reimage = [i for i, s in enumerate(address_list) if 'reimage' in s]

            if index_reimage:
                address_list.pop(index_reimage[0])

            if address_list[-1].strip():
                # print("full_address === " + str(address_list))

                index_phone = [i for i, s in enumerate(address_list) if phone in s]

                if index_phone:
                    hours_of_operation = address_list[index_phone[0]+1].replace(")","")
                # print("hours_of_operation == " + str(hours_of_operation))
                # print("address_list====",address_list)
                
                location_name = address_list[0]
                city = location_name
                if "(403) 250-2072" in phone:
                    location_name='Calgary'

                if "(780) 890-7766" in phone:
                    location_name='Edmonton'
                    


                if len(address_list) > 1:
                    street_address = address_list[1]

                if len(address_list) > 2:
                    csz = address_list[2] + " "
                    zipp_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(csz))
                    if zipp_list:
                        zipp = zipp_list[-1]
                    else:
                        zipp = ""

                    state_list = re.findall(r' ([A-Z]{2}) ', csz)
                    if state_list:
                        state = state_list[-1]
                    else:
                        state = ""

                    country_code = "CA"

                # print("fffffffffffffffff",hours_of_operation.replace("Edmonton Airport Chili's  Gate 52Sun-Fri",'Sun-Fri').replace(".*Breakfast Served at ALL airport locations",'').replace("PM"," PM "))
                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                         store_number, phone, location_type, latitude, longitude, hours_of_operation.encode('ascii', 'ignore').decode('ascii').strip().replace("Edmonton Airport Chili's  Gate 52Sun-Fri",'Sun-Fri').replace("*Breakfast Served at ALL airport locations",'').replace("PM"," PM ").replace("AM",' AM '), page_url]

                if str(store[1]) + str(store[2]) not in addresses:
                    addresses.append(str(store[1]) + str(store[2]))

                    store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

                    if "(780) 890-7766" in store or "(403) 760-8502" in store or "(403) 250-2072" in store:
                        # print("data = " + str(store))
                        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

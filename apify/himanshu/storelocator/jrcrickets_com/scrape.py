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
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }

    addresses = []

    base_url = "http://jrcrickets.com"
    r = session.get("http://jrcrickets.com/locations.php", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    #   data = json.loads(soup.find("div",{"paging_container":re.compile('latlong.push')["paging_container"]}))
    # for link in soup.find_all('ul',re.compile('content')):
    #     print(link)

    # it will used in store data.
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = ""
    store_number = "<MISSING>"
    phone = ""
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    hours_of_operation = ""

    # print("data ====== "+str(soup))

    location_menu = soup.find(lambda tag: (tag.name == "a") and "LOCATIONS" == tag.text.strip()).parent
    for script_url in location_menu.find("ul",{"class":"sub-menu"}).find_all("a"):
        location_url = base_url +"/"+ script_url["href"]

        # print("href  === "+str(location_url))
        r_location = session.get(location_url, headers=headers)
        soup_location = BeautifulSoup(r_location.text, "lxml")

        for script in soup_location.find_all("div", {"class": "each_loc"}):
            list_location = list(script.stripped_strings)

            if 'More info' in list_location:
                list_location.remove('More info')

            # print(str(len(list_location)) + " ==== script === " + str(list_location))

            location_name = list_location[0]
            street_address = list_location[1]
            if 'Center' in street_address:
                street_address = list_location[2] 
            country_code = "US"

            city_state_zipp_index = [i for i, s in enumerate(list_location) if 'Hours:' in s]
            city_state_zipp = list_location[city_state_zipp_index[0]-1].replace('US', "").split(",")

            # print("city_state_zipp === "+ str(city_state_zipp))

            if len(city_state_zipp) > 1:
                city = city_state_zipp[0]
                state = city_state_zipp[1].strip().split(" ")[0]
                zipp = city_state_zipp[1].strip().split(" ")[1]
            else:
                city_state_zipp[0] = city_state_zipp[0].replace("  "," ")
                # city_state_zipp = city_state_zipp[0].strip()
                # city_state_zipp = city_state_zipp[0].replace("  "," ")
                if city_state_zipp[0].strip().split(" ")[-1].strip().isdigit():
                    zipp = city_state_zipp[0].strip().split(" ")[-1].strip()
                    state = city_state_zipp[0].strip().split(" ")[-2].strip()
                    city = " ".join(city_state_zipp[0].strip().split(" ")[:-2])
                else:
                    zipp = "<MISSING>"
                    state = city_state_zipp[0].strip().split(" ")[-1].strip()
                    if len(state.strip()) == 2:
                        city = " ".join(city_state_zipp[0].strip().split(" ")[:-1])
                    else:
                        state = "<MISSING>"
                        city = " ".join(city_state_zipp[0].strip().split(" "))

            for str_data in list_location:
                if "Hours:" in str_data:
                    hours_of_operation = str_data.replace("Hours:", "")

           
            phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(list_location))

            if phone_list:
                phone = phone_list[0]
            else:
                phone = "<MISSING>"

            # print("street_address === " + str(street_address))

            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation,location_url]

            if str(store[2]) + str(store[-3]) not in addresses:
                addresses.append(str(store[2]) + str(store[-3]))

                store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

                # print("data = " + str(store))
                # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

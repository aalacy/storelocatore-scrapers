import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('hueymagoos_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    }

    # logger.info("soup ===  first")

    base_url = "https://www.hueymagoos.com"
    page_url = "https://hueymagoos.com/locations/"
    r = session.get(page_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    #   data = json.loads(soup.find("div",{"paging_container":re.compile('latlong.push')["paging_container"]}))
    # for link in soup.find_all('ul',re.compile('content')):
    #     logger.info(link)

    # it will used in store data.
    locator_domain = base_url
    location_name = ""
    street_address = "<INACCESSIBLE>"
    city = "<INACCESSIBLE>"
    state = ""
    zipp = ""
    country_code = ""
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    # logger.info("data ====== "+str(soup))
    for script in soup.find_all("div", {"class": "vc_row wpb_row vc_inner vc_row-fluid mkdf-section vc_custom_1502476441129 mkdf-content-aligment-left mkdf-grid-section"}):

        script_location = script.find_all("div", {"class": "mkdf-icon-list-item"})
        location_name = script.h2.text.strip()
        # logger.info(location_name)
        
        try:
            map_link = script.iframe["src"]
            lat_pos = map_link.rfind("!3d")
            latitude = map_link[lat_pos+3:map_link.find("!",lat_pos+5)].strip()
            lng_pos = map_link.find("!2d")
            longitude = map_link[lng_pos+3:map_link.find("!",lng_pos+5)].strip()
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        if len(script_location) > 2:
            phone = "".join(list(script_location[0].stripped_strings))
            address_list = list(script_location[1].stripped_strings)
            hours_of_operation = "".join(list(script_location[2].stripped_strings)) +","+ "".join(list(script_location[3].stripped_strings))
            
            # logger.info("address_list ==== "+ str(address_list))
            address_list[0] = address_list[0].replace(".,",".")
            if len(address_list[0].split(',')) > 2:
                street_address = address_list[0].split(',')[0].strip()
                city = address_list[0].split(',')[-2].strip()
                state = "".join(address_list[0].split('.')[-1]).split(",")[-1].strip().split(' ')[0].strip()
                zipp = "".join(address_list[0].split('.')[-1]).split(",")[-1].strip().split(' ')[1].strip()
            else:
                street_address = " ".join(address_list[0].split('.')[:-1]).strip()
                city = "".join(address_list[0].split('.')[-1]).split(",")[0].strip()
                state = "".join(address_list[0].split('.')[-1]).split(",")[1].strip().split(' ')[0].strip()
                zipp = "".join(address_list[0].split('.')[-1]).split(",")[1].strip().split(' ')[1].strip()

            street_address = street_address.replace("  "," ")
            if "1" in city:
                street_address = (street_address + " " + city[:city.find(location_name.split()[0])]).strip()
                city = city[city.find(location_name.split()[0]):].strip()
            country_code = "US"
            
            store = [locator_domain, page_url, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation]

            # logger.info("data = " + str(store))
            # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

            return_main_object.append(store)

        else:
            if "Coming Soon" != "".join(list(script_location[0].stripped_strings)):
                # logger.info("else =================== "+ str(list(script_location[0].stripped_strings)))
                address_list = list(script_location[0].stripped_strings)
                try:
                    hours_of_operation = "".join(list(script_location[1].stripped_strings))
                except:
                    continue
                address_list[0] = address_list[0].replace(".,",".")
                if len(address_list[0].split(',')) > 2:
                    street_address = address_list[0].split(',')[0].strip()
                    city = address_list[0].split(',')[-2].strip()
                    state = "".join(address_list[0].split('.')[-1]).split(",")[-1].strip().split(' ')[0].strip()
                    zipp = "".join(address_list[0].split('.')[-1]).split(",")[-1].strip().split(' ')[1].strip()
                else:
                    street_address = " ".join(address_list[0].split('.')[:-1]).strip()
                    city = "".join(address_list[0].split('.')[-1]).split(",")[0].strip()
                    state = "".join(address_list[0].split('.')[-1]).split(",")[1].strip().split(' ')[0].strip()
                    zipp = "".join(address_list[0].split('.')[-1]).split(",")[1].strip().split(' ')[1].strip()

                street_address = street_address.replace("  "," ")
                if "1" in city:
                    street_address = (street_address + " " + city[:city.find(location_name.split()[0])]).strip()
                    city = city[city.find(location_name.split()[0]):].strip()

                store = [locator_domain, page_url, location_name, street_address, city, state, zipp, country_code,
                         store_number, phone, location_type, latitude, longitude, hours_of_operation]

                # logger.info("data = " + str(store))
                # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

                return_main_object.append(store)
            else:
                street_address = "<MISSING>"
                city = "<MISSING>"
                state = "<MISSING>"
                zipp = "<MISSING>"
                hours_of_operation = "<MISSING>"
            phone = "<MISSING>"



    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

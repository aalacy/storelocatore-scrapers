import csv
import time
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('exhalespa_com')


 

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
    }

    base_url = "https://www.exhalespa.com"
    addresses = []

    r = session.get("https://www.exhalespa.com/locations", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    for script in soup.find_all("div", {"class": re.compile("loc-locations")}):

        for location_url in script.find_all("a"):
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

            page_url = base_url + location_url["href"]
            # logger.info("page_url = " + page_url)

            r_location = session.get(page_url, headers=headers)
            soup_location = BeautifulSoup(r_location.text, "lxml")

            if soup_location.find("div",{"class":"page_heading Configurable-Text"}):
                try:
                    location_name = soup_location.find("div",{"class":"page_heading Configurable-Text"}).find("h1").text
                except:
                    location_name = soup_location.find("div",{"class":"page_heading Configurable-Text"}).find("h2").text

                full_address = list(soup_location.find("div",{"class":"address"}).stripped_strings)
                street_address = full_address[0]

                city_state_zipp = full_address[1]
                phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(full_address))
                ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(city_state_zipp))
                us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(city_state_zipp))
                state_list = re.findall(r' ([A-Z]{2}) ', str(city_state_zipp))

                if ca_zip_list:
                    zipp = ca_zip_list[0]
                    country_code = "CA"
                elif us_zip_list:
                    zipp = us_zip_list[0]
                    country_code = "US"
                else:
                    country_code = ""

                if state_list:
                    state = state_list[0]

                if phone_list:
                    phone = phone_list[0]

                city = city_state_zipp.replace(zipp, "").replace(state, "").replace(",", "")
                temp_loc_type = soup_location.find("ol",{"class":"breadcrumb"}).find("li",{"class":"active"}).text
                if "(temporarily closed)" in temp_loc_type:
                    location_type = "temporarily closed"
                else:
                    location_type = "<MISSING>"


                hours_list = list(soup_location.find("div",{"class":"field-hours-of-operation"}).stripped_strings)
                latitude = soup_location.find("meta",{"property":"latitude"})["content"]
                longitude = soup_location.find("meta",{"property":"longitude"})["content"]
                if hours_list:
                    hours_of_operation = " ".join(hours_list[1:]).replace("We are open! Please contact us for most up-to-date hours of operation and available services.","<MISSING>")
                    hours_of_operation = hours_of_operation.replace("Exhale at 45PROVINCE is a private facility for residents only. Hours vary and are based on appointment requests and class times.","<MISSING>")
                    hours_of_operation = hours_of_operation.replace("Hours vary. Please see this week's class schedule for times.","<MISSING>")
                    hours_of_operation = hours_of_operation.replace("Hours vary and are based on appointment requests and class times.","<MISSING>")
                # logger.info("hours_of_operation === "+ str(hours_of_operation))

                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                         store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

                if str(store[2]) not in addresses and country_code:
                    addresses.append(str(store[2]))

                    store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

                    # logger.info("data = " + str(store))
                    # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                    yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

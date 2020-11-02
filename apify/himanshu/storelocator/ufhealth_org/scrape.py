import csv
import time
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import requests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('ufhealth_org')




session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8",newline="") as output_file:
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

    base_url = "https://www.ufhealth.org"
    addresses = []

    r_search_location = session.get("https://ufhealth.org/search/locations", headers=headers)
    soup_search_location = BeautifulSoup(r_search_location.text, "lxml")
    # logger.info("soup_search_location === "+ str(soup_search_location))
    for cat_tag in soup_search_location.find_all("option", {"value": re.compile("im_field_dpt_specialty:")}):

        cat_url = "https://ufhealth.org/search/locations?f%5B0%5D=im_field_dpt_specialty%3A" + \
                  cat_tag["value"].split("im_field_dpt_specialty:")[1].split('"')[0]

        while True:
            # logger.info(cat_tag.text + " == type_tag  === " + str(cat_url))
            r_locations = session.get(cat_url, headers=headers)

            if r_locations is None:
                continue

            soup_locations = BeautifulSoup(r_locations.text, "lxml")
            # logger.info("soup_locations = "+ str(soup_locations.find("a",{"title":"Go to next page"})))

            for single_location in soup_locations.find_all("li", {"class": "search-result divclick"}):

                locator_domain = base_url
                location_name = ""
                street_address = ""
                city = ""
                state = ""
                zipp = ""
                country_code = ""
                store_number = ""
                phone = ""
                location_type = ""
                latitude = ""
                longitude = ""
                raw_address = ""
                hours_of_operation = ""
                page_url = single_location.find("a")["href"]

                # page_url = "https://ufhealth.org/uf-health-congenital-heart-center/maps"
                # logger.info(page_url)
                # logger.info("page_url ==== " + page_url)
                # do your logic here.
                r_store = session.get(page_url + "/maps", headers=headers)

                if r_store is None:
                    continue
                soup_store = BeautifulSoup(r_store.text, "lxml")

                location_type = cat_tag.text.split("(")[0]

                if soup_store.find("div", {"class": "street-address"}):
                    street_address = " ".join(list(soup_store.find("div", {"class": "street"}).stripped_strings))
                    # logger.info(street_address)

                if soup_store.find("div", {"class": "span-15 omega location-title"}):
                    location_name = soup_store.find("div", {"class": "span-15 omega location-title"}).text

                if soup_store.find("span", {"class": "locality"}):
                    city = soup_store.find("span", {"class": "locality"}).text

                if soup_store.find("span", {"class": "region"}):
                    state = soup_store.find("span", {"class": "region"}).text

                if soup_store.find("span", {"class": "postal-code"}):
                    zipp = soup_store.find("span", {"class": "postal-code"}).text

                    ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(zipp))
                    us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(zipp))
                    if ca_zip_list:
                        country_code = "CA"

                    if us_zip_list:
                        country_code = "US"
                if soup_store.find("div", {"class": "field field-name-field-phone-number field-type-text field-label-inline clearfix"}):
                    phone_raw = " ".join(list(soup_store.find("div", {"class": "field field-name-field-phone-number field-type-text field-label-inline clearfix"}).stripped_strings))
                    phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(phone_raw))
                    if phone_list:
                        phone = phone_list[0]
                        # logger.info(phone)
                    else:
                        phone = phone_raw.split(":")[1].replace("WELL","").replace("1NOW","").replace("PEDS","").replace("RUNR","").replace("SPNE","").replace("4FRC","").replace("Outpatient","").replace("KIDS","").replace("HELP","").replace("TMS","").strip()
                        # phone = phone_raw.split(":")[1].replace("Outpatient","").replace("TMS","").strip()
                        # logger.info(phone)
                elif soup_store.find("div",{"class":"field field-name-field-alt-phone field-type-text field-label-inline clearfix"}):
                    phone_raw = " ".join(list(soup_store.find("div",{"class":"field field-name-field-alt-phone field-type-text field-label-inline clearfix"}).stripped_strings))
                    phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(phone_raw))
                    if phone_list:
                        phone = phone_list[0]
                        # logger.info(phone)
                    else:
                        phone = phone_raw.split(":")[1].replace("WELL","").replace("1NOW","").replace("PEDS","").replace("RUNR","").replace("Outpatient","").replace("SPNE","").replace("4FRC","").replace("KIDS","").replace("KIDS","").replace("HELP","").replace("TMS","").strip()
                        # phone = phone_raw.split(":")[1].replace("Outpatient","").replace("TMS","").strip()
                        # logger.info(phone)
                        
                else:
                    phone = "<MISSING>"
                if "352-265-" == phone:
                    phone = "352-265-7337"
                # logger.info(phone)
                
                if soup_store.find("div", {"class": "field field-name-field-hours-of-operation field-type-table field-label-hidden"}):
                    hours_raw = soup_store.find("div", {
                        "class": "field field-name-field-hours-of-operation field-type-table field-label-hidden"})
                    if hours_raw:
                        hours_of_operation = " ".join(list(hours_raw.stripped_strings)[1:])
                try:
                    latitude = soup_store.text.split('"latitude":"')[1].split('"')[0]
                    longitude = soup_store.text.split('"longitude":"')[1].split('"')[0]
                except:
                    latitude="<MISSING>"
                    latitude="<MISSING>"
                # logger.info(street_address)
                if "Suite" in street_address or "suite" in street_address:
                    street_address = street_address.split("Suite")[0].split(",")[0].strip()


                store = [locator_domain, location_name.replace(': Maps',''), street_address, city, state, zipp, country_code,
                         store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

                if str(store[1] + " "+ store[2]+ " "+ store[9]) not in addresses and country_code:
                    addresses.append(str(store[1] + " "+ store[2]+ " "+ store[9]))

                    store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

                    # logger.info("data = " + str(store))
                    # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                    yield store

            # logger.info("cat_url next url == "+ str(soup_locations.find("a",{"title","Go to next page"})))
            if soup_locations.find("a", {"title": "Go to next page"}):
                cat_url = base_url + soup_locations.find("a", {"title": "Go to next page"})["href"]
                # logger.info("next page")
            else:
                break


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

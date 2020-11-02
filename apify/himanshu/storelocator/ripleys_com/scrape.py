import csv
import time
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import requests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('ripleys_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8", newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def request_wrapper(url, method, headers, data=None):
    request_counter = 0
    if method == "get":
        while True:
            try:
                r = session.get(url, headers=headers)
                return r
                break
            except:
                time.sleep(2)
                request_counter = request_counter + 1
                if request_counter > 10:
                    return None
                    break
    elif method == "post":
        while True:
            try:
                if data:
                    r = session.post(url, headers=headers, data=data)
                else:
                    r = session.post(url, headers=headers)
                return r
                break
            except:
                time.sleep(2)
                request_counter = request_counter + 1
                if request_counter > 10:
                    return None
                    break
    else:
        return None


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "https://www.ripleys.com"
    addresses = []

    r = session.get("https://www.ripleys.com/attractions/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")


    for location_img_tag in soup.find_all("div", {"class": "row vwpc-row"})[1].find_all("li"):

        location_tag = location_img_tag.find("a")
        

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
        hours_of_operation = ""
        page_url = location_tag["href"].replace("https://marinersquare.com/","https://www.ripleys.com/newport/information/").replace("http://www.williamsburgripleys.com/","https://www.ripleys.com/williamsburg/")
        

        location_name = location_tag.text
        
        r_location = session.get(page_url, headers=headers)

        if r_location is None:
            continue
        soup_location = BeautifulSoup(r_location.text, "lxml")

        full_address_list = []
        hours_list = []
        if soup_location.find("div", {"class": "large-4 medium-4 small-12 columns"}):
        
            full_address_list = list(
                soup_location.find("div", {"class": "large-4 medium-4 small-12 columns"}).stripped_strings)
            if soup_location.find("div", {"class": "medium-6 columns hide-for-small-only"}):
                hours_list = list(
                    soup_location.find("div", {"class": "medium-6 columns hide-for-small-only"}).stripped_strings)
                hours_index = [i for i, s in enumerate(hours_list) if 'Hours' in s]
                hours_of_operation = " ".join(hours_list[hours_index[0]:])
        elif soup_location.find("div", {"class": "footerText"}):
            # logger.info("22222222222")
            full_address_list = list(soup_location.find("div", {"class": "footerText"}).stripped_strings)
            hours_tag = soup_location.find(lambda tag: (tag.name == "h6") and "Hours of Operation" == tag.text.strip())
            if hours_tag:
                hours_list = list(hours_tag.find_next_sibling("div").stripped_strings)
                hours_of_operation = " ".join(hours_list)

        elif soup_location.find("span", {"id": "contact"}):
            # logger.info("33333333333")
            # https://www.ripleys.com/atlanticcity/
            # https://www.ripleysamsterdam.com/
            full_address_list = list(soup_location.find("span", {"id": "contact"}).parent.parent.stripped_strings)[1:]
            hours_tag = soup_location.find(
                lambda tag: (tag.name == "span" or tag.name == "h3") and "HOURS" == tag.text.strip())

            # logger.info("hours_tag === " + str(hours_tag))
            if hours_tag:
                if hours_tag.parent.find_next_sibling("p"):
                    hours_list = list(hours_tag.parent.find_next_sibling("p").stripped_strings)
                elif hours_tag.find_next_sibling("p"):
                    hours_list = list(hours_tag.find_next_sibling("p").stripped_strings)

                if "$" not in str(hours_list):
                    hours_of_operation = " ".join(hours_list)

        elif soup_location.find("div", {"class": "contact-info-container"}):
            # logger.info("44444444444444")
            # https://www.ripleysnewyork.com/
            full_address_list = list(soup_location.find("div", {"class": "contact-info-container"}).stripped_strings)
            if soup_location.find("section", {"id": "text-4"}):
                hours_list = list(soup_location.find("section", {"id": "text-4"}).stripped_strings)[:-1]
                hours_of_operation = " ".join(hours_list)
        elif soup_location.find("div", {"class": "hotel-contact"}):
            # logger.info("55555555555")
            # https://marinersquare.com/
            full_address_list = list(soup_location.find("div", {"class": "hotel-contact"}).stripped_strings)
        elif soup_location.find("div", {"class": "block contact-info-block"}):
            # logger.info("666666666666")
            # http://www.ripleysdells.com/
            full_address_list = list(soup_location.find("div", {"class": "block contact-info-block"}).stripped_strings)
            street_address = full_address_list[-2].replace("\xa0", " ")
            # logger.info(full_address_list[-2] + " ======= ripleysdells street_address ==== " + str(street_address))
            # logger.info("splait array = "+ str(street_address.split(" ")))
            hours_tag = soup_location.find(lambda tag: (tag.name == "strong") and "Current Hours:" == tag.text.strip())
            try:
                hours_list = list(hours_tag.parent.parent.stripped_strings)
            except:
                hours_list = ""
            hours_of_operation = " ".join(hours_list)
        elif soup_location.find("div", {"id": "text-2"}):
            # logger.info("7777777777777")
            # https://www.ripleyaquariums.com/canada/
            full_address_list = list(soup_location.find("div", {"id": "text-2"}).stripped_strings)[1:]
            if soup_location.find("div", {"class": "mtphr-dnt-tick mtphr-dnt-default-tick mtphr-dnt-clearfix"}):
                hours_list = list(soup_location.find("div", {
                    "class": "mtphr-dnt-tick mtphr-dnt-default-tick mtphr-dnt-clearfix"}).stripped_strings)
                # logger.info("77 hours_list == " + str(hours_list))
                hours_of_operation = " ".join(hours_list)

            if "," in full_address_list[0]:
                street_address = full_address_list[0].split(",")[0]
                city = full_address_list[0].split(",")[1]
            else:
                street_address = full_address_list[0]
                city = full_address_list[1].split(",")[0]
        elif soup_location.find("div", {"class": "contact-infotxt"}):
            # logger.info("888888888888")
            # http://www.ripleysthailand.com/index.php?p=attractions
            full_address_list = list(soup_location.find("div", {"class": "contact-infotxt"}).stripped_strings)[1:]
            hours_of_operation = list(soup_location.find("div", {"class": "contact-infotxt"}).stripped_strings)[0]
            # hours_list = list(soup_location.find("div",{"class":"mtphr-dnt-tick mtphr-dnt-default-tick mtphr-dnt-clearfix"}).stripped_strings)
        elif soup_location.find("div", {"id": "text-5"}):
            # https://www.ripleyaquariums.com/myrtlebeach/
            full_address_list = list(soup_location.find("div", {"id": "text-5"}).stripped_strings)[1:]
            hours_tag = soup_location.find(
                lambda tag: (tag.name == "h4") and "WEEKLY OPERATING HOURS" == tag.text.strip())
            hours_of_operation = hours_tag.find_next_sibling("h5").text
            # logger.info("9999999999999")
            # street_address = full_address_list[0].split(",")[0]

            if "," in full_address_list[0]:
                street_address = full_address_list[0].split(",")[0]
                city = full_address_list[0].split(",")[1]
            else:
                street_address = full_address_list[0]
                city = full_address_list[1].split(",")[0]
            # hours_list = list(soup_location.find("div",{"class":"mtphr-dnt-tick mtphr-dnt-default-tick mtphr-dnt-clearfix"}).stripped_strings)
        elif soup_location.find("div",{"class":"contentParappa"}):
            full_address_list = list(soup_location.find("div",{"class":"contentParappa"}).find_all("div",{"class":"cell medium-6"})[-1].find_all("p")[2].stripped_strings)
            street_address = full_address_list[0]
            city = full_address_list[1].split(",")[0]
            hours_of_operation = " ".join(list(soup_location.find("div",{"class":"contentParappa"}).find_all("div",{"class":"cell medium-6"})[-1].find_all("p")[4].stripped_strings))
        else:
            continue


        phone_list = re.findall(re.compile(r".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"),
                                str(full_address_list).replace("\xa0", " "))
        ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}',
                                 str(full_address_list).replace("\xa0", " "))
        us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"),
                                 str(full_address_list).replace("\xa0", " "))

        state_list = re.findall(r'\b[A-Z]{2}\b', str(location_name))
        if not state_list:
            state_list = re.findall(r'\b[A-Z]{2}\b', str(full_address_list))

        if state_list:
            state = state_list[0]

        if phone_list:
            phone = phone_list[0]

        if ca_zip_list:
            zipp = ca_zip_list[-1]
            country_code = "CA"

        if us_zip_list:
            zipp = us_zip_list[-1]
            country_code = "US"

        if not city:
            city = location_name.split(",")[0]

        # logger.info("hours_list === " + str(hours_list))
        # logger.info("hours of operation  === " + str(hours_of_operation))
        # logger.info("full_Address === " + str(full_address_list))

        if not street_address:
            if zipp:
                zipp_index = [i for i, s in enumerate(full_address_list) if zipp in s]
                # logger.info(str(city) + " === zipp_index === "+ str(zipp_index))
                if city in full_address_list[zipp_index[0]]:
                    city_index = full_address_list[zipp_index[0]].rindex(city)

                    state_list = re.findall(r'\b[A-Z]{2}\b', str(location_name))
                    if not state_list:
                        state_list = re.findall(r'\b[A-Z]{2}\b', str(full_address_list[:zipp_index[0] + 1]))

                    if state_list:
                        state = state_list[0]
                    # logger.info("state_list === "+ str(state_list))
                    if city_index == 0:
                        street_address = full_address_list[:zipp_index[0] + 1][0].replace("\n", ",").replace("\r", "")
                    else:
                        street_address = "".join(full_address_list[:zipp_index[0] + 1])[:city_index].replace("\n",
                                                                                                             ",").replace(
                            "\r", "")
                else:
                    street_address = " ".join(full_address_list[:zipp_index[0]]).replace("\n", ",").replace("\r", "")
                    street_address = street_address.split(",")[0]
            else:
                if city in full_address_list[0]:
                    city_index = full_address_list[0].rindex(city)
                    street_address = "".join(full_address_list[0])[:city_index].replace("\n", ",").replace("\r", "")
                else:
                    street_address = full_address_list[0].replace("\n", ",").replace("\r", "")
                    street_address = street_address.split(",")[0]
        


        # logger.info(str(street_address.strip()) + " ====== is num ========== "+ str(street_address.isnumeric()))
        if street_address.strip().isnumeric():
            street_address = street_address + " " + city
        if "329  Alamo Plaza" in street_address:
            city = "San Antonio"
            street_address = "329 Alamo Plaza"
        if "329 Alamo Plaza" in street_address:
            r5 = session.get("https://www.ripleys.com/phillips/", headers=headers)
            soup = BeautifulSoup(r5.text, "lxml")
            k2 = "".join(list(soup.find("div", {"class": "g1-block"}).stripped_strings))
            hours_of_operation = (k2.replace("pm","pm "))
            
        if "800 Parkway" in street_address:
            r6 = session.get("https://www.ripleys.com/gatlinburg/",  headers=headers)
            soup6 = BeautifulSoup(r6.text, "lxml")
            hours_of_operation = (" ".join(list(soup6.find_all("li",{"class": "g1-column g1-one-half g1-valign-top"})[-2].stripped_strings)).split("*Weather")[0].replace("** ALL ATTRACTIONS WILL BE CLOSING EARLY AT 4PM ON WEDNESDAY, DECEMBER 4, 2019 FOR A CHRISTMAS PARTY** Believe It or Not!",""))

        if "Mon - Sun" in street_address:
            street_address="115 Broadway"
            zipp="53965"
            hours_of_operation="Mon - Sun	Closed"

        # logger.info(str(street_address).encode('ascii', 'ignore').decode('ascii').strip()+ " !!! last street_address === "+ str(street_address))
        # logger.info("hours_of_operation === "+ str(hours_of_operation))

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation.replace('\t',''), page_url]

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

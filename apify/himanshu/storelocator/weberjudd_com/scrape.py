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
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'application/json',
    }

    addresses = []
    base_url = "http://www.weberjudd.com"

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
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = ""
    page_url = ""
    # 800 N. 2nd Street
    r = session.get("https://www.googletagmanager.com/gtm.js?id=GTM-5TL68P", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    caption_value_list = soup.text.split('Coption value=\\"')
    for cap_val in caption_value_list[2:]:

        page_url = "https://www.hy-vee.com/stores/detail.aspx?s=" + str(cap_val.split('\\"')[0])

        # print("page_url === "+ page_url)
        r_location = session.get(page_url, headers=headers)
        soup_location = BeautifulSoup(r_location.text, "lxml")

        if not soup_location.find("div", {"class": "col-sm-6 util-padding-bottom-15"}):
            continue

        full_address = list(soup_location.find("div", {"class": "col-sm-6 util-padding-bottom-15"}).stripped_strings)

        if 'Address' in full_address:
            full_address.remove('Address')

        if 'Google Maps' in full_address:
            full_address.remove('Google Maps')

        full_address = ", ".join(full_address)

        us_zipp_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(full_address))
        ca_zipp_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(full_address))
        if us_zipp_list:
            zipp = us_zipp_list[-1]
            country_code = "US"
        elif ca_zipp_list:
            zipp = ca_zipp_list[-1]
            country_code = "CA"
        else:
            country_code = "US"
            zipp = ""

        state_list = re.findall(r' ([A-Z]{2}) ', full_address)
        if state_list:
            state = state_list[-1]
        else:
            state = ""

        if zipp and state:
            street_address = full_address.replace(zipp,"").replace(state,"").split(",")[0]
            city = full_address.replace(zipp,"").replace(state,"").split(",")[1]
        else:
            street_address = full_address.split(",")[0]
            city = ""
            if len(full_address.split(",")[1].strip().split(" ")) > 2:
                state = " ".join(full_address.split(",")[1].strip().split(" ")[:-1])
            else:
                state = full_address.split(",")[1].strip().split(" ")[0]
        phone_raw = soup_location.find("i",{"class":"fa fa-phone"}).nextSibling
        phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(phone_raw))
        if phone_list:
            phone = phone_list[0]
        else:
            phone = ""
        hours_of_operation = " ".join(list(soup_location.find("p",{"class":"util-padding-top-15"}).findNext("p").stripped_strings))
        hours_of_operation += " "+" ".join(list(soup_location.find("table",{"class":"storeHours table"}).stripped_strings))
        if len(hours_of_operation) < 2:
            hours_of_operation = ""

        location_name = soup_location.find("h1").text
        # geo_url = soup_location.find("a",{"id":"ctl00_cph_main_content_aMapItWithGoogle"})["href"]

        # latitude = geo_url.split("&spn=")[1].split(",")[0]
        # longitude = geo_url.split("&spn=")[1].split(",")[1].split("&")[0]

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

        if str(store[1]) + str(store[2]) not in addresses and "coming soon" not in location_name.lower():
            addresses.append(str(store[1]) + str(store[2]))

            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

            # print("data = " + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

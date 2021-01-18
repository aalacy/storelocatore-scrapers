import csv
import re

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

import usaddress

log = SgLogSetup().get_logger("myjhfamilystores.com")


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def parse_addy(addy):
    parsed_add = usaddress.tag(addy)[0]

    street_address = ""

    if "AddressNumber" in parsed_add:
        street_address += parsed_add["AddressNumber"] + " "
    if "StreetNamePreDirectional" in parsed_add:
        street_address += parsed_add["StreetNamePreDirectional"] + " "
    if "StreetNamePreType" in parsed_add:
        street_address += parsed_add["StreetNamePreType"] + " "
    if "StreetName" in parsed_add:
        street_address += parsed_add["StreetName"] + " "
    if "StreetNamePostType" in parsed_add:
        street_address += parsed_add["StreetNamePostType"] + " "
    if "OccupancyType" in parsed_add:
        street_address += parsed_add["OccupancyType"] + " "
    if "OccupancyIdentifier" in parsed_add:
        street_address += parsed_add["OccupancyIdentifier"] + " "
    city = parsed_add["PlaceName"]
    state = parsed_add["StateName"]
    zip_code = parsed_add["ZipCode"]

    return street_address.strip(), city.strip(), state, zip_code


def fetch_data():
    locator_domain = "http://www.myjhfamilystores.com/"
    ext = "locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(locator_domain + ext, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    hrefs = base.find(class_="et_pb_row et_pb_row_2").find_all("a")

    link_list = []
    for h in hrefs:
        link_list.append(h["href"])

    all_store_data = []
    for link in link_list:
        link = link.replace("creekl", "creek")
        log.info(link)
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = base.h1.text

        addy_phone = base.find_all(class_="et_pb_text_inner")[2].text.split("|")

        addy = addy_phone[0]

        street_address, city, state, zip_code = parse_addy(addy)
        phone_number = addy_phone[1].replace("PHONE:", "").strip()

        geo = re.findall(r"[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+", str(base))[0].split(
            ","
        )
        lat = geo[0]
        longit = geo[1]

        country_code = "US"

        location_type = "<MISSING>"
        page_url = link
        hours = "<MISSING>"
        store_number = "<MISSING>"

        store_data = [
            locator_domain,
            location_name,
            street_address,
            city,
            state,
            zip_code,
            country_code,
            store_number,
            phone_number,
            location_type,
            lat,
            longit,
            hours,
            page_url,
        ]
        all_store_data.append(store_data)

    return all_store_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

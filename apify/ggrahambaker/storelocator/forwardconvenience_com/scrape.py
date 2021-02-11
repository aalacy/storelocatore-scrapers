import csv

from bs4 import BeautifulSoup

from sgrequests import SgRequests

import usaddress


def parse_address(addy_string):
    parsed_add = usaddress.tag(addy_string)[0]

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

    if "PlaceName" not in parsed_add:
        city = "<MISSING>"
    else:
        city = parsed_add["PlaceName"]

    if "StateName" not in parsed_add:
        state = "<MISSING>"
    else:
        state = parsed_add["StateName"]

    if "ZipCode" not in parsed_add:
        zip_code = "<MISSING>"
    else:
        zip_code = parsed_add["ZipCode"]

    return street_address, city, state, zip_code


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


def fetch_data():
    session = SgRequests()
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }

    locator_domain = "https://forwardconvenience.com/"
    ext = "contact-locations/"
    r = session.get(locator_domain + ext, headers=headers)

    all_store_data = []
    soup = BeautifulSoup(r.content, "html.parser")
    locs = soup.find_all("div", {"class": "et_pb_map_pin"})
    for loc in locs:
        clean_info = []
        lat = loc["data-lat"]
        longit = loc["data-lng"]
        location_name = loc["data-title"].replace("&amp;", "&")
        info = loc.prettify().split("\n")
        for i in info:
            if "<" in i:
                continue

            clean_info.append(i.strip())

        location_type = "<MISSING>"
        if len(clean_info) == 6:
            phone_number = clean_info[1]
            addy = clean_info[4]

        else:
            phone_number = clean_info[1]
            addy = clean_info[2]

        if "-" not in phone_number:
            phone_number = clean_info[2]
            addy = clean_info[3]

        street_address, city, state, zip_code = parse_address(addy)

        hours = "<MISSING>"
        store_number = "<MISSING>"
        page_url = "https://forwardconvenience.com/contact-locations/"
        country_code = "US"

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

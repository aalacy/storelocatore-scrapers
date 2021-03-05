import csv

from sgselenium import SgChrome

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
    locator_domain = "https://nouriaenergy.com/"
    ext = "store-locator/"

    driver = SgChrome().chrome()
    driver.get(locator_domain + ext)

    driver.implicitly_wait(20)
    locs = driver.execute_script("return locations")

    all_store_data = []
    for loc in locs:
        info = locs[loc]
        addy = info["location"]

        if not addy:
            continue

        addy_info = addy["address"]
        street_address, city, state, zip_code = parse_address(addy_info)

        lat = addy["lat"]
        longit = addy["lng"]

        page_url = info["permalink"]
        phone_number = info["phone"]
        location_name = info["title"]

        store_number = location_name.split(" - ")[0].split(" ")[-1]

        country_code = "US"

        hours = ""

        h_obj = info["hours"][0]

        hours += h_obj["header"] + " "

        for h in h_obj["hours"]:
            hours += h_obj["hours"][h]["datetime"] + " "

        location_type = "<MISSING>"

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

    driver.quit()
    return all_store_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

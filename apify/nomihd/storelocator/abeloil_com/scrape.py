# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape import sgpostal as parser
import lxml.html

website = "abeloil.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
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
            ]
        )
        # Body
        temp_list = []  # ignoring duplicates
        for row in data:
            comp_list = [
                row[2].strip(),
                row[3].strip(),
                row[4].strip(),
                row[5].strip(),
                row[6].strip(),
                row[8].strip(),
                row[10].strip(),
            ]
            if comp_list not in temp_list:
                temp_list.append(comp_list)
                writer.writerow(row)

        log.info(f"No of records being processed: {len(temp_list)}")


def fetch_data():
    # Your scraper here
    loc_list = []

    session.get("https://www.abeloil.com/")
    search_url = "https://www.powr.io/wix/map/public.json?pageId=mainPage&compId=comp-jxlx28pu&viewerCompId=comp-jxlx28pu&siteRevision=246&viewMode=site&deviceType=desktop&locale=en&tz=America%2FChicago&width=620&height=420&instance=h3GWKCccR94Y7a6lgSbsdJVb4aG9prQWYrrgOimif0Q.eyJpbnN0YW5jZUlkIjoiM2NmZmZjZWYtNjhhNy00ODFjLWEyZDUtYzA4YWIzYTRhMzdjIiwiYXBwRGVmSWQiOiIxMzQwYzVlZC1hYWM1LTIzZWYtNjkzYy1lZDIyMTY1Y2ZkODQiLCJzaWduRGF0ZSI6IjIwMjEtMDItMTNUMDk6MzE6MTcuMDE2WiIsInZlbmRvclByb2R1Y3RJZCI6ImJ1c2luZXNzIiwiZGVtb01vZGUiOmZhbHNlLCJhaWQiOiIxOGE1MjEzNy0wNWVhLTQ2ODAtYTZhMC0zN2IzMjRhZTkzYmUiLCJzaXRlT3duZXJJZCI6Ijk4NWQwOGU2LTM5NTQtNDE2ZC05MDNmLTJhZmY0MDM5YTUyYiJ9&currency=USD&currentCurrency=USD&vsi=a698f35c-ceb3-4ca5-8d03-64c4bfd3abaa&commonConfig=%7B%22brand%22%3A%22wix%22%2C%22bsi%22%3A%22745a37fa-79b6-49a8-a7aa-710d6b6983a0%7C2%22%2C%22BSI%22%3A%22745a37fa-79b6-49a8-a7aa-710d6b6983a0%7C2%22%7D&url=https://www.abeloil.com/"
    stores_req = session.get(search_url)
    stores = json.loads(stores_req.text)["content"]["locations"]
    for store_json in stores:
        page_url = "<MISSING>"
        latitude = store_json["lat"]
        longitude = store_json["lng"]

        location_name = (
            store_json["name"]
            .replace("<p>", "")
            .replace("</p>", "")
            .strip()
            .replace("&#x27;", "'")
            .strip()
        )

        locator_domain = website

        location_type = "<MISSING>"

        raw_address = store_json["address"]
        formatted_addr = parser.parse_address_usa(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        state = formatted_addr.state
        zip = formatted_addr.postcode
        country_code = formatted_addr.country

        desc_sel = lxml.html.fromstring(store_json["description"])
        desc = desc_sel.xpath("//p/text()")

        phone = ""
        if len(desc) > 0:
            phone = desc[0].strip()

        hours_of_operation = ""
        if len(desc) > 1:
            hours_of_operation = desc[1].strip()

        store_number = "<MISSING>"
        if store_number == "":
            store_number = "<MISSING>"

        if location_name == "":
            location_name = "<MISSING>"

        if street_address == "" or street_address is None:
            street_address = "<MISSING>"

        if city == "" or city is None:
            city = "<MISSING>"

        if state == "" or state is None:
            state = "<MISSING>"

        if zip == "" or zip is None:
            zip = "<MISSING>"

        if country_code == "" or country_code is None:
            country_code = "<MISSING>"

        if phone == "" or phone is None:
            phone = "<MISSING>"

        if latitude == "" or latitude is None:
            latitude = "<MISSING>"
        if longitude == "" or longitude is None:
            longitude = "<MISSING>"

        if hours_of_operation == "":
            hours_of_operation = "<MISSING>"

        if location_type == "":
            location_type = "<MISSING>"

        curr_list = [
            locator_domain,
            page_url,
            location_name,
            street_address,
            city,
            state,
            zip,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]
        loc_list.append(curr_list)
        # break

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()

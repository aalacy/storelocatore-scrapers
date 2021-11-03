# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json
import lxml.html

website = "ultratantoday.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


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

    search_url = "https://ultratantoday.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    json_text = "".join(
        stores_sel.xpath('//script[@id="__NEXT_DATA__"]/text()')
    ).strip()
    stores = json.loads(json_text)["props"]["pageProps"]["data"]["filterLocations"][
        "edges"
    ]

    for store in stores:
        attributes = store["node"]["customAttributes"]
        page_url = "<MISSING>"
        for att in attributes:
            if "Slug" == att["name"]:
                page_url = att["value"]

        if len(page_url) > 0:
            page_url = "https://ultratantoday.com/stores/" + page_url[0]
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)
            if "This page could not be found" not in store_req.text:
                json_text = "".join(
                    store_sel.xpath('//script[@id="__NEXT_DATA__"]/text()')
                ).strip()
                store_json = json.loads(json_text)["props"]["pageProps"]["data"][
                    "getLocationsByIds"
                ][0]

                locator_domain = website
                location_name = "".join(store_sel.xpath("//div/h1/text()")).strip()
                if location_name == "":
                    location_name = "<MISSING>"

                street_address = store_json["street"]
                city = store_json["city"]
                state = store_json["stateIso"]
                zip = store_json["postalCode"]

                street_address = (
                    street_address.replace(city + ",", "")
                    .replace(state, "")
                    .replace(zip, "")
                    .strip()
                )
                country_code = store_json["countryIso"]
                if country_code == "" or country_code is None:
                    country_code = "<MISSING>"

                if street_address == "" or street_address is None:
                    street_address = "<MISSING>"

                if city == "" or city is None:
                    city = "<MISSING>"

                if state == "" or state is None:
                    state = "<MISSING>"

                if zip == "" or zip is None:
                    zip = "<MISSING>"

                store_number = "<MISSING>"

                phone = store_json["phone"]

                location_type = "<MISSING>"
                location_type = store_json["name"]
                hours = store_json["businessHours"]
                hours_list = []
                for hour in hours:
                    day = hour["day"]
                    if hour["slots"] is not None and day != "SPECIAL":
                        start = hour["slots"][0]["start"]
                        end = hour["slots"][0]["end"]
                        hours_list.append(day + ":" + start + "-" + end)

                hours_of_operation = ";".join(hours_list).strip()

                latitude = store_json["latitude"]
                longitude = store_json["longitude"]

                if latitude == "" or latitude is None:
                    latitude = "<MISSING>"
                if longitude == "" or longitude is None:
                    longitude = "<MISSING>"

                if hours_of_operation == "":
                    hours_of_operation = "<MISSING>"

                if phone == "" or phone is None:
                    phone = "<MISSING>"

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

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()

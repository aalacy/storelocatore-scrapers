# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import json

website = "daylewis.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
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

    search_url = "https://www.daylewis.co.uk/pharmacyFinder.php"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    ids_list = stores_sel.xpath(
        '//select[@id="search_phm"]/option[position()>1]/@value'
    )
    for ID in ids_list:
        log.info(f"Pulling Store for ID: {ID}")
        data = {"address": "", "id": ID, "mode": "ddl"}
        stores_req = session.post(
            "https://www.daylewis.co.uk/searchPharmacy.php", data=data, headers=headers
        )
        stores = json.loads(stores_req.text)
        for store in stores:
            page_url = "<MISSING>"
            locator_domain = website
            location_name = store["name"]
            if location_name == "":
                location_name = "<MISSING>"

            street_address = store["add1"].strip()
            add2 = store["add2"]
            if add2 is not None and len(add2) > 0:
                street_address = street_address + ", " + add2.strip()

            city = ""
            if store["add3"] is not None:
                city = store["add3"].strip()

            state = ""
            if store["add4"] is not None:
                state = store["add4"].strip()

            zip = store["pcode"]
            country_code = "GB"

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

            store_number = store["id"]
            phone = store["phone1"]

            location_type = "<MISSING>"
            hours_of_operation = ""
            if len(store["mon"]) > 0:
                hours_of_operation = hours_of_operation + "mon:" + store["mon"] + "; "

            if len(store["tue"]) > 0:
                hours_of_operation = hours_of_operation + "tue:" + store["tue"] + "; "
            if len(store["wed"]) > 0:
                hours_of_operation = hours_of_operation + "wed:" + store["wed"] + "; "
            if len(store["thu"]) > 0:
                hours_of_operation = hours_of_operation + "thu:" + store["thu"] + "; "
            if len(store["fri"]) > 0:
                hours_of_operation = hours_of_operation + "fri:" + store["fri"] + "; "
            if len(store["sat"]) > 0:
                hours_of_operation = hours_of_operation + "sat:" + store["sat"] + "; "
            if len(store["sun"]) > 0:
                hours_of_operation = hours_of_operation + "sun:" + store["sun"]

            latitude = store["latitude"]
            longitude = store["longitude"]

            if latitude == "" or latitude is None:
                latitude = "<MISSING>"
            if longitude == "" or longitude is None:
                longitude = "<MISSING>"

            if hours_of_operation == "" or hours_of_operation is None:
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
            break

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()

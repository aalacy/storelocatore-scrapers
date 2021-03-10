# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import us
import json

website = "clipperpetroleum.com"
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

    search_url = "https://clipperpetroleum.com/__locations.php"
    data = {"cat": "", "count": "", "keyword": ""}
    stores_req = session.post(search_url, data=data, headers=headers)
    stores = json.loads(stores_req.text)
    for store in stores:
        page_url = "https://clipperpetroleum.com/locations/" + store["url_title"]
        locator_domain = website
        location_name = store["title"]
        if location_name == "":
            location_name = "<MISSING>"

        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        address = store_sel.xpath("//address/p")
        add_list = []
        for add in address:
            if "Phone:" in "".join(add.xpath("text()")).strip():

                break
            else:
                add_list.append(
                    "".join(add.xpath("text()")).strip().replace("\xa0", " ").strip()
                )

        street_address = ""
        city = ""
        state = ""
        zip = ""
        if len(add_list) == 2:
            street_address = " ".join(add_list[0].split("\n")).strip()
            city = add_list[1].split(",")[0].strip()
            state = add_list[1].split(",")[1].strip().split(" ")[0].strip()
            zip = add_list[1].split(",")[1].strip().split(" ")[1].strip()
        elif len(add_list) == 1:
            street_address = " ".join(
                add_list[0].split(",")[0].strip().split("\n")
            ).strip()
            city = "<MISSING>"
            state = add_list[0].split(",")[1].strip().split(" ")[0].strip()
            zip = add_list[0].split(",")[1].strip().split(" ")[1].strip()
        country_code = "<MISSING>"
        if us.states.lookup(state):
            country_code = "US"

        if street_address == "":
            street_address = "<MISSING>"

        if city == "":
            city = "<MISSING>"

        if state == "":
            state = "<MISSING>"

        if zip == "":
            zip = "<MISSING>"

        if city == "<MISSING>":
            city = street_address.split(" ")[-1].strip()
            street_address = " ".join(street_address.split(" ")[:-1]).strip()

        store_number = store["field_id_79"].replace("#", "").strip()
        phone = "".join(store_sel.xpath('//a[@class="tel"]/text()')).strip()
        try:
            phone = phone.split("/")[0].strip().replace("Clipper-", "").strip()
        except:
            pass

        location_type = "<MISSING>"
        temp_hours = address
        hours_of_operation = ""
        hours_list = []
        for index in range(0, len(temp_hours)):
            if "Store Hours:" in "".join(temp_hours[index].xpath("text()")).strip():
                try:
                    for counter in range(index + 1, len(temp_hours)):
                        hours = (
                            "".join(temp_hours[counter].xpath("text()"))
                            .strip()
                            .split("\n")
                        )
                        for hour in hours:
                            if "," not in hour:
                                if len("".join(hour).strip()) > 0:
                                    hours_list.append(
                                        "".join(hour)
                                        .strip()
                                        .replace("\xa0", " ")
                                        .strip()
                                        .replace("Clipper -", "")
                                        .strip()
                                    )
                except:
                    pass

                break

        hours_of_operation = (
            " ".join(hours_list).strip().replace("Open 7 days", "").strip()
        )
        try:
            hours_of_operation = hours_of_operation.split("Bojangles")[0].strip()
        except:
            pass

        latitude = store["field_id_82"]
        longitude = store["field_id_83"]

        if latitude == "":
            latitude = "<MISSING>"
        if longitude == "":
            longitude = "<MISSING>"

        if hours_of_operation == "":
            hours_of_operation = "<MISSING>"
        if phone == "":
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

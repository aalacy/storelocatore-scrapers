# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json
import us

website = "genghisgrill.com"
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
    search_url = "https://maps.genghisgrill.com/api/getAsyncLocations?template=domain&level=domain&radius=100000&search=89521"
    stores_req = session.get(search_url, headers=headers)
    maplist = json.loads(stores_req.text)["maplist"]
    json_text = (
        "[{" + maplist.split("{", 1)[1].strip().split(",</div>")[0].strip() + "]"
    )
    stores = json.loads(json_text)

    for store in stores:
        page_url = store["url"]

        locator_domain = website
        location_name = store["location_name"]
        if location_name == "":
            location_name = "<MISSING>"

        street_address = store["address_1"]
        if len(store["address_2"]) > 0:
            street_address = street_address + ", " + store["address_2"]

        city = store["city"]
        state = store["region"]
        zip = store["post_code"]
        country_code = ""
        if us.states.lookup(state):
            country_code = "US"

        if country_code == "":
            country_code = "<MISSING>"

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

        store_number = store["fid"]
        phone = store["local_phone"]

        location_type = "<MISSING>"

        latitude = store["lat"]
        longitude = store["lng"]

        if latitude == "" or latitude is None:
            latitude = "<MISSING>"
        if longitude == "" or longitude is None:
            longitude = "<MISSING>"

        hours_of_operation = ""
        hours = json.loads(store["hours_sets:primary"].replace('"', '"').strip())[
            "days"
        ]
        hours_list = []
        for day in hours.keys():
            if isinstance(hours[day], list):
                time = hours[day][0]["open"] + "-" + hours[day][0]["close"]
            else:
                time = hours[day]
            hours_list.append(day + ":" + time)

        hours_of_operation = "; ".join(hours_list).strip()
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
        yield curr_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()

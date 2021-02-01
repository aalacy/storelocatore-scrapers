# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json
import us

website = "launchtrampolinepark.com"
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

    search_url = "https://launchtrampolinepark.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(
        stores_req.text.split("JSON.parse('")[1].strip().split("');")[0].strip()
    )

    for store in stores:
        if store["site_name"] != "Corporate" and store["site_name"] != "TEST":
            page_url = store["full_site_url"]

            locator_domain = website
            location_name = store["site_name"]
            if location_name == "":
                location_name = "<MISSING>"

            street_address = store["street"]
            city = store["city"]
            state = store["state"]
            zip = store["zipcode"].replace(state, "").strip()
            country_code = "<MISSING>"
            if us.states.lookup(country_code):
                country_code = "US"

            if street_address == "" or street_address is None:
                street_address = "<MISSING>"

            if city == "" or city is None:
                city = "<MISSING>"

            if state == "" or state is None:
                state = "<MISSING>"

            if zip == "" or zip is None:
                zip = "<MISSING>"

            store_number = str(store["site_id"])
            phone = store["phone"]

            location_type = "<MISSING>"
            hours_of_operation = "<MISSING>"
            hour_list = []
            hours_type = store["hours"]
            for typ in hours_type:
                if typ["title"] == "Regular Hours":
                    hours = typ["schedule"]
                    for hour in hours:
                        day = hour["day"]
                        time = hour["times"]
                        hour_list.append(day + ":" + time)

            if len(hour_list) <= 0:
                hours = store["hours_legacy"]
                for hour in hours:
                    day = hour["day"]
                    if day == "__________________________________________________":
                        break
                    else:
                        time = hour["times"]
                        hour_list.append(day + ":" + time)

            hours_of_operation = "; ".join(hour_list).strip()

            latitude = store["lat"]
            longitude = store["long"]

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

        # break
    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()

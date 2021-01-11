# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json
import us
import lxml.html

website = "sonnysbbq.com"
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

    search_url = "https://api.sonnysbbq.com/api/v1/locations.bystate"
    stores_req = session.get(search_url, headers=headers)
    states_dict = json.loads(stores_req.text)
    for state in states_dict.keys():
        stores = states_dict[state]
        for store in stores:
            if store["post_status"] == "publish":
                page_url = "https://www.sonnysbbq.com/locations/" + store["slug"]
                locator_domain = website
                location_name = store["post_title"]
                if location_name == "":
                    location_name = "<MISSING>"

                store_number = str(store["ID"])
                phone = store["contact_phone"]

                location_type = "<MISSING>"
                hours_of_operation = ""
                try:
                    hours = (
                        store["store_hours"].split("\r\n\r\n")[1].strip().split("\n")
                    )

                    hours_of_operation = ""  # store["store_hours"].split('\n')
                    for hour in hours:
                        hours_of_operation = hours_of_operation + hour + " "
                except:
                    hours_of_operation = store["store_hours"]

                hours_of_operation = " ".join(
                    hours_of_operation.strip().split("\n")
                ).strip()

                latitude = store["address"]["lat"]
                longitude = store["address"]["lng"]

                if latitude == "":
                    latitude = "<MISSING>"
                if longitude == "":
                    longitude = "<MISSING>"

                if hours_of_operation == "":
                    hours_of_operation = "<MISSING>"
                if phone == "":
                    phone = "<MISSING>"

                store_req = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_req.text)
                address = (
                    "".join(store_sel.xpath('//span[@class="address-line"][2]/text()'))
                    .strip()
                    .replace(", United States", "")
                    .strip()
                )

                street_address = "".join(
                    store_sel.xpath('//span[@class="address-line"][1]/text()')
                ).strip()

                city = "<MISSING>"
                state = "<MISSING>"
                zip = "<MISSING>"
                country_code = ""
                if len(address) > 0:
                    if "," in address:
                        city = address.split(",")[0].strip()
                        state_zip = address.split(",")[1].strip()
                        if " " in state_zip:
                            state = address.split(",")[1].strip().split(" ")[0].strip()
                            zip = address.split(",")[1].strip().split(" ")[1].strip()
                        else:
                            state = state_zip
                            zip = "<MISSING>"
                    else:
                        state_zip = address
                        if " " in state_zip:
                            state = address.split(" ")[0].strip()
                            zip = address.split(" ")[1].strip()
                        else:
                            state = state_zip
                            zip = "<MISSING>"

                else:
                    address = store["address"]["address"]
                    street_address = address.split(",")[0].strip()
                    city = ""
                    state = ""
                    zip = ""
                    if len(address.split(",")) >= 3:
                        city = address.split(",")[1].strip()
                        state_zip = address.split(",")[2].strip()
                        if " " in state_zip:
                            state = address.split(",")[2].strip().split(" ")[0].strip()
                            zip = address.split(",")[2].strip().split(" ")[1].strip()
                        else:
                            state = state_zip
                            zip = "<MISSING>"

                if us.states.lookup(state):
                    country_code = "US"

                if city == "<MISSING>":
                    city = location_name
                    if "-" in city:
                        city = city.split("-")[0].strip()

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

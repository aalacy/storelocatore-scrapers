# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json
import us

website = "simplymac.com"
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

    search_url = "https://api2.storepoint.co/v1/15ec82b1d81806/locations?rq"
    stores_req = session.get(search_url, headers=headers)
    if json.loads(stores_req.text)["success"] is True:
        stores = json.loads(stores_req.text)["results"]["locations"]

        for store in stores:
            page_url = store["website"]
            locator_domain = website
            location_name = store["name"]
            if location_name == "":
                location_name = "<MISSING>"

            address = store["streetaddress"]
            if len(address.split(",")) == 4:
                street_address = ", ".join(address.split(",")[:-2]).strip()
                city = address.split(",")[-2].strip()
                state = address.split(",")[-1].strip().split(" ")[0].strip()
                zip = address.split(",")[-1].strip().split(" ")[1].strip()
            else:
                street_address = " ".join(
                    ", ".join(address.split(",")[:-1]).strip().split(" ")[:-1]
                ).strip()
                city = "".join(
                    ", ".join(address.split(",")[:-1]).strip().split(" ")[-1]
                ).strip()
                state = address.split(",")[-1].strip().split(" ")[0].strip()
                zip = address.split(",")[-1].strip().split(" ")[1].strip()
            country_code = "<MISSING>"
            if us.states.lookup(state):
                country_code = "US"

            if street_address == "" or street_address is None:
                street_address = "<MISSING>"

            if city == "" or city is None:
                city = "<MISSING>"

            if state == "" or state is None:
                state = "<MISSING>"

            if zip == "" or zip is None:
                zip = "<MISSING>"

            store_number = str(store["id"])
            phone = store["phone"]
            if "(" not in phone:
                phone = "<MISSING>"

            location_type = store["description"]
            if location_type == "" or location_type is None:
                location_type = "<MISSING>"

            hours_of_operation = ""
            hours_list = []
            if len(store["monday"]) > 0:
                hours_list.append("monday:" + store["monday"])
            else:
                hours_list.append("monday:" + "Closed")
            if len(store["tuesday"]) > 0:
                hours_list.append("tuesday:" + store["tuesday"])
            else:
                hours_list.append("tuesday:" + "Closed")
            if len(store["wednesday"]) > 0:
                hours_list.append("wednesday:" + store["wednesday"])
            else:
                hours_list.append("wednesday:" + "Closed")
            if len(store["thursday"]) > 0:
                hours_list.append("thursday:" + store["thursday"])
            else:
                hours_list.append("thursday:" + "Closed")
            if len(store["friday"]) > 0:
                hours_list.append("friday:" + store["friday"])
            else:
                hours_list.append("friday:" + "Closed")
            if len(store["saturday"]) > 0:
                hours_list.append("saturday:" + store["saturday"])
            else:
                hours_list.append("saturday:" + "Closed")
            if len(store["sunday"]) > 0:
                hours_list.append("sunday:" + store["sunday"])
            else:
                hours_list.append("sunday:" + "Closed")

            hours_of_operation = "; ".join(hours_list).strip()
            latitude = store["loc_lat"]
            longitude = store["loc_long"]

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
    else:
        log.error("Something wrong with the response SUCCESS value")
        # break
    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()

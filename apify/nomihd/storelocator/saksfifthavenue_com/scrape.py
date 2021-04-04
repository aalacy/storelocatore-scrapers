# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json
import datetime

website = "saksfifthavenue.com"
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

    timestamp = str(datetime.datetime.now().timestamp()).split(".")[0].strip()
    current_page = 0
    search_url = (
        "https://saksfifthavenue.brickworksoftware.com/locations_search?hitsPerPage=50&page="
        + str(current_page)
        + "&getRankingInfo=true&facets[]=*&aroundRadius=all&filters=domain:saksfifthavenue.brickworksoftware.com+AND+publishedAt%3C%3D{}&esSearch=%7B%22page%22:"
        + str(current_page)
        + ",%22storesPerPage%22:50,%22domain%22:%22saksfifthavenue.brickworksoftware.com%22,%22locale%22:%22en_US%22,%22must%22:[%7B%22type%22:%22range%22,%22field%22:%22published_at%22,%22value%22:%7B%22lte%22:1610932161969%7D%7D],%22filters%22:[],%22aroundLatLngViaIP%22:true%7D&aroundLatLngViaIP=true"
    )
    stores_req = session.get(search_url.format(timestamp), headers=headers)
    total_pages = json.loads(stores_req.text)["nbPages"]
    for index in range(0, total_pages):
        current_page = index

        timestamp = str(datetime.datetime.now().timestamp()).split(".")[0].strip()
        search_url = (
            "https://saksfifthavenue.brickworksoftware.com/locations_search?hitsPerPage=50&page="
            + str(current_page)
            + "&getRankingInfo=true&facets[]=*&aroundRadius=all&filters=domain:saksfifthavenue.brickworksoftware.com+AND+publishedAt%3C%3D{}&esSearch=%7B%22page%22:"
            + str(current_page)
            + ",%22storesPerPage%22:50,%22domain%22:%22saksfifthavenue.brickworksoftware.com%22,%22locale%22:%22en_US%22,%22must%22:[%7B%22type%22:%22range%22,%22field%22:%22published_at%22,%22value%22:%7B%22lte%22:1610932161969%7D%7D],%22filters%22:[],%22aroundLatLngViaIP%22:true%7D&aroundLatLngViaIP=true"
        )
        stores_req = session.get(search_url.format(timestamp), headers=headers)
        stores = json.loads(stores_req.text)["hits"]
        for store in stores:
            page_url = (
                "https://www.saksfifthavenue.com/locations/s/"
                + store["attributes"]["slug"]
            )

            locator_domain = website
            location_name = store["attributes"]["name"]
            if location_name == "":
                location_name = "<MISSING>"

            street_address = store["attributes"]["address1"]
            if store["attributes"]["address2"] is not None:
                if len("".join(store["attributes"]["address2"])) > 0:
                    street_address = (
                        street_address + ", " + store["attributes"]["address2"]
                    )
            if store["attributes"]["address3"] is not None:
                if len("".join(store["attributes"]["address3"])) > 0:
                    street_address = (
                        street_address + ", " + store["attributes"]["address3"]
                    )

            city = store["attributes"]["city"]
            state = store["attributes"]["state"]
            zip = store["attributes"]["postalCode"]
            country_code = store["attributes"]["countryCode"]

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

            store_number = str(store["id"])
            phone = store["attributes"]["phoneNumber"]
            try:
                phone = phone.split(";")[0].strip()
            except:
                pass

            location_type = store["attributes"]["type"]

            latitude = store["attributes"]["latitude"]
            longitude = store["attributes"]["longitude"]

            if latitude == "" or latitude is None:
                latitude = "<MISSING>"
            if longitude == "" or longitude is None:
                longitude = "<MISSING>"

            hours_of_operation = ""
            hours = store["relationships"]["hours"]
            hours_list = []
            for hour in hours:
                if hour["type"] == "regular":
                    day = hour["displayDay"]
                    time = hour["displayStartTime"] + "-" + hour["displayEndTime"]
                    hours_list.append(day + ":" + time)

            hours_of_operation = "; ".join(hours_list).strip()
            if hours_of_operation == "":
                hours_of_operation = "<MISSING>"

            if phone == "" or phone is None:
                phone = "<MISSING>"

            if country_code == "US" or country_code == "CA":
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

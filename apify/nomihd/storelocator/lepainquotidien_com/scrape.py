# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json

website = "lepainquotidien.com"
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

    search_url = "https://liveapi.yext.com/v2/accounts/1308693/entities/geosearch?api_key=a8db8f1f1c70c53b5f6346b6882e13a4&v=20200802&location=United%20States&countryBias=us&radius=2500&offset=0&limit=50&entityTypes=location&languages=primary&filter={%22closed%22:{%22$eq%22:false},%22countryCode%22:{%22$in%22:[%22us%22]}}"
    offset = 0
    total_count = None
    count = 0
    while True:
        final_url = (
            search_url.split("&offset=")[0].strip()
            + "&offset="
            + str(offset)
            + "&"
            + search_url.split("&offset=")[1].strip().split("&", 1)[1].strip()
        )
        stores_req = session.get(final_url, headers=headers)

        if count == 0:
            total_count = json.loads(stores_req.text)["response"]["count"]
            count = count + 1

        if offset < total_count:
            stores = json.loads(stores_req.text)["response"]["entities"]
            for store in stores:
                page_url = store["websiteUrl"]["url"]
                try:
                    page_url = page_url.split("?utm_source")[0].strip()
                except:
                    pass

                locator_domain = website
                location_name = store["name"]

                store_number = "<MISSING>"

                if location_name == "":
                    location_name = "<MISSING>"

                street_address = store["address"]["line1"]
                if "line2" in store:
                    street_address = street_address + ", " + store["line2"]

                city = store["address"]["city"]
                state = store["address"]["region"]
                zip = store["address"]["postalCode"]
                country_code = "<MISSING>"

                if street_address == "":
                    street_address = "<MISSING>"

                if city == "":
                    city = "<MISSING>"

                if state == "":
                    state = "<MISSING>"

                if zip == "":
                    zip = "<MISSING>"

                phone = store["mainPhone"]

                location_type = "<MISSING>"
                if "-" in location_name:
                    location_name = store["name"].split("-")[0].strip()
                    location_type = store["name"].split("-")[1].strip()

                latitude = store["geocodedCoordinate"]["latitude"]
                longitude = store["geocodedCoordinate"]["longitude"]

                if latitude == "" or latitude is None:
                    latitude = "<MISSING>"
                if longitude == "" or longitude is None:
                    longitude = "<MISSING>"

                if phone == "" or phone is None:
                    phone = "<MISSING>"

                hours_of_operation = ""
                hours = store["hours"]
                for hour in hours.keys():
                    if "openIntervals" in hours[hour]:
                        hours_of_operation = (
                            hours_of_operation
                            + hours[hour]["openIntervals"][0]["start"]
                            + "-"
                            + hours[hour]["openIntervals"][0]["end"]
                            + " "
                        )

                hours_of_operation = hours_of_operation.strip()
                if hours_of_operation == "" or hours_of_operation is None:
                    hours_of_operation = "<MISSING>"

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
            break

        offset = offset + 50
        # break
    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()

# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog

website = "cartoys.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.cartoys.com",
    "sec-ch-ua": '"Google Chrome";v="87", " Not;A Brand";v="99", "Chromium";v="87"',
    "accept": "application/json, text/javascript, */*; q=0.01",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://www.cartoys.com",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.cartoys.com/store-locator",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
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

    search_url = "https://www.cartoys.com/store-locator/index/loadstore/"
    data = {"curPage": "1"}
    stores_req = session.post(search_url, data=data, headers=headers)
    total_pages = int(float(stores_req.json()["num_store"] / 10)) + 2

    for index in range(1, total_pages):
        search_url = "https://www.cartoys.com/store-locator/index/loadstore/"
        data = {"curPage": str(index)}
        stores_req = session.post(search_url, data=data, headers=headers)
        stores = stores_req.json()["storesjson"]

        for store in stores:
            page_url = "https://www.cartoys.com/" + store["rewrite_request_path"]

            locator_domain = website
            location_name = store["store_name"]
            if location_name == "":
                location_name = "<MISSING>"

            street_address = store["address"]
            city = store["city"]
            state = store["state"]
            zip = store["zipcode"]
            country_code = store["country_id"]

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

            store_number = store["store_code"]
            phone = store["phone"]

            location_type = "<MISSING>"

            latitude = store["latitude"]
            longitude = store["longitude"]

            if latitude == "" or latitude is None:
                latitude = "<MISSING>"
            if longitude == "" or longitude is None:
                longitude = "<MISSING>"

            hours_list = []
            for key in store.keys():
                if "_open" in key:
                    day = key.replace("_open", "").strip()
                    open_time = store[day + "_open"]
                    close_time = store[day + "_close"]
                    hours_list.append(day + ":" + open_time + "-" + close_time)

            hours_of_operation = "; ".join(hours_list).strip()

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

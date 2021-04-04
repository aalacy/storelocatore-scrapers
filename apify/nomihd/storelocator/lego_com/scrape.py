# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json

website = "lego.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '"Google Chrome";v="87", " Not;A Brand";v="99", "Chromium";v="87"',
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "x-api-key": "p0OKLXd8US1YsquudM1Ov9Ja7H91jhamak9EMrRB",
    "Content-Type": "application/json",
    "Accept": "*/*",
    "Origin": "https://www.lego.com",
    "Sec-Fetch-Site": "same-site",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://www.lego.com/",
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

    search_url = "https://services.slingshot.lego.com/api/v4/lego_store_read/_search"
    data = '{"size":9001,"query":{"bool":{"must":[{"match":{"locale":"en-us"}},{"match":{"showOnWebsite":true}}]}},"sort":[{"country":"asc"},{"state":"asc"},{"name2":"asc"}]}'

    stores_req = session.post(search_url, data=data, headers=headers)
    stores = json.loads(stores_req.text)["hits"]["hits"]
    for store in stores:
        country_code = store["_source"]["country"]

        if country_code == "CA" or country_code == "US":
            locator_domain = website
            location_name = store["_source"]["name1"]
            if location_name == "":
                location_name = "<MISSING>"

            page_url = (
                "https://www.lego.com/en-us/stores/store?store="
                + location_name.replace(" ", "-").strip()
            )

            street_address = store["_source"]["addressLine1"]
            city = store["_source"]["city"]
            state = store["_source"]["state"]
            zip = store["_source"]["postCode"]

            if street_address == "":
                street_address = "<MISSING>"

            if city == "":
                city = "<MISSING>"

            if state == "":
                state = "<MISSING>"

            if zip == "":
                zip = "<MISSING>"

            store_number = str(store["_source"]["storeId"])
            phone = store["_source"]["phone"]

            location_type = "<MISSING>"
            hours = store["_source"]["openingHours"]
            hours_of_operation = ""
            try:
                hours = hours.split("\n")
                for hour in hours:
                    hours_of_operation = hours_of_operation + hour + " "
            except:
                pass

            if len("".join(hours_of_operation).strip()) <= 0:
                try:
                    hours = (
                        store["_source"]["additionalDetails"]
                        .split("\n\n")[1]
                        .strip()
                        .split("\n")
                    )
                    hours_of_operation = ""
                    for hour in hours:
                        hours_of_operation = hours_of_operation + hour + " "
                except:
                    hours_of_operation = hour
                    pass

            hours_of_operation = (
                hours_of_operation.strip()
                .encode("ascii", "replace")
                .decode("utf-8")
                .replace("?", "-")
                .strip()
                .replace("Instore:", "")
                .strip()
                .replace("Instore Hours:", "")
                .strip()
                .replace("In-Store:", "")
                .strip()
            )

            latitude = store["_source"]["location"]["lat"]
            longitude = store["_source"]["location"]["lon"]

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

            # break
    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()

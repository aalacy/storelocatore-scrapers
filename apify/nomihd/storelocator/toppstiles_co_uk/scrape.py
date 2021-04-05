# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json
import datetime

website = "toppstiles.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.toppstiles.co.uk",
    "sec-ch-ua": '"Google Chrome";v="87", " Not;A Brand";v="99", "Chromium";v="87"',
    "accept": "application/json, text/plain, */*",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "content-type": "application/json",
    "origin": "https://www.toppstiles.co.uk",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.toppstiles.co.uk/store_finder",
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

    search_url = "https://www.toppstiles.co.uk/api/locateStore"
    data = '{"address":"london","country":"GB","maxDistance":200000,"limit":30000}'

    stores_req = session.post(search_url, data=data, headers=headers)
    stores = json.loads(stores_req.text)["stores"]

    for store in stores:
        page_url = "https://www.toppstiles.co.uk" + store["url"]

        locator_domain = website
        location_name = store["store_name"]
        if location_name == "":
            location_name = "<MISSING>"

        street_address = ""
        city = ""
        zip = ""
        country_code = ""
        try:
            street_address = store["address"].strip()
        except:
            pass
        try:
            city = store["city"].strip()
        except:
            pass
        state = "<MISSING>"
        try:
            zip = store["postcode"].strip()
        except:
            pass
        try:
            country_code = store["country_id"]
        except:
            pass

        if "," in city:
            street_address = street_address + " " + city.split(",")[0].strip()
            city = city.split(",")[-1].strip()

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

        store_number = str(store["id"])
        phone = store["phone"].strip()

        location_type = "<MISSING>"

        latitude = store["latitude"]
        longitude = store["longitude"]

        if latitude == "" or latitude is None:
            latitude = "<MISSING>"
        if longitude == "" or longitude is None:
            longitude = "<MISSING>"

        hours_of_operation = ""
        hours = store["days"]
        day_list = []
        hours_list = []
        for date in hours.keys():
            day = datetime.datetime.strptime(date, "%Y-%m-%y").strftime("%A")
            if hours[date]["status"] == 2:
                time = "Closed"
            else:
                time = hours[date]["open"] + "-" + hours[date]["close"]

            if day not in day_list:
                day_list.append(day)
                hours_list.append(day + ":" + time)

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
        # break

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()

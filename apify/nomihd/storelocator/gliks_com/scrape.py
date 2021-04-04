# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json

website = "gliks.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    "Accept": "*/*",
    "Origin": "https://www.gliks.com",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://www.gliks.com/",
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

    search_url = [
        "https://rebase.global.ssl.fastly.net/api/places/index.json?api_key=a0f289f0b91b1b6177194e9e0336f7ef",
        "https://rebase.global.ssl.fastly.net/api/places/index.json?api_key=a0f289f0b91b1b6177194e9e0336f7ef&lat=38.716&lng=-90.131",
    ]
    for s_url in search_url:
        stores_req = session.get(s_url, headers=headers)
        stores = json.loads(stores_req.text)["locations"]
        for store_json in stores:
            page_url = "https://www.gliks.com/pages/store-locator"
            latitude = store_json["latitude"]
            longitude = store_json["longitude"]

            location_name = store_json["info"]["name"]

            locator_domain = website

            location_type = "<MISSING>"

            street_address = store_json["info"]["location"]["street"]

            city = store_json["info"]["location"]["city"]
            state = store_json["info"]["location"]["state"]
            zip = store_json["info"]["location"]["zip"]
            country_code = store_json["info"]["location"]["country"]
            phone = store_json["info"]["phone"]
            hours_of_operation = ""
            hours_list = []
            hours = store_json["info"]["hours"]
            try:
                daytime = "Monday:" + hours["mon_1_open"] + "-" + hours["mon_1_close"]
                hours_list.append(daytime)
            except:
                pass
            try:
                daytime = "Tuesday:" + hours["tue_1_open"] + "-" + hours["tue_1_close"]
                hours_list.append(daytime)
            except:
                pass
            try:
                daytime = (
                    "Wednesday:" + hours["wed_1_open"] + "-" + hours["wed_1_close"]
                )
                hours_list.append(daytime)
            except:
                pass
            try:
                daytime = "Thursday:" + hours["thu_1_open"] + "-" + hours["thu_1_close"]
                hours_list.append(daytime)
            except:
                pass
            try:
                daytime = "Friday:" + hours["fri_1_open"] + "-" + hours["fri_1_close"]
                hours_list.append(daytime)
            except:
                pass
            try:
                daytime = "Saturday:" + hours["sat_1_open"] + "-" + hours["sat_1_close"]
                hours_list.append(daytime)
            except:
                pass
            try:
                daytime = "Sunday:" + hours["sun_1_open"] + "-" + hours["sun_1_close"]
                hours_list.append(daytime)
            except:
                pass

            hours_of_operation = "; ".join(hours_list).strip()

            store_number = str(store_json["id"])
            if store_number == "":
                store_number = "<MISSING>"

            if location_name == "":
                location_name = "<MISSING>"

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

            if phone == "" or phone is None:
                phone = "<MISSING>"

            if latitude == "" or latitude is None:
                latitude = "<MISSING>"
            if longitude == "" or longitude is None:
                longitude = "<MISSING>"

            if hours_of_operation == "":
                hours_of_operation = "<MISSING>"

            if location_type == "":
                location_type = "<MISSING>"

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

# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json

website = "calbanktrust.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "authority": "www.calbanktrust.com",
    "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
    "accept": "*/*",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
    "content-type": "application/json",
    "origin": "https://www.calbanktrust.com",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.calbanktrust.com/locations/",
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

    search_url = "https://www.calbanktrust.com/locationservices/searchwithfilter"

    data = '{"channel":"Online","schemaVersion":"1.0","clientUserId":"ZIONPUBLICSITE","clientApplication":"ZIONPUBLICSITE","transactionId":"txId","affiliate":"0140","searchResults":"20000","username":"ZIONPUBLICSITE","searchAddress":{"address":"10001","city":null,"stateProvince":null,"postalCode":null,"country":null},"distance":"300000","searchFilters":[{"fieldId":"1","domainId":"140","displayOrder":1,"groupNumber":1}]}'

    stores_req = session.post(search_url, data=data, headers=headers)
    stores = json.loads(stores_req.text)["location"]

    for store in stores:
        latitude = store["lat"]
        longitude = store["long"]
        page_url = "https://www.calbanktrust.com/locations/"

        locator_domain = website
        location_name = store["locationName"]
        if location_name == "":
            location_name = "<MISSING>"

        street_address = store["address"]
        city = store["city"]
        state = store["stateProvince"]
        zip = store["postalCode"]
        country_code = store["country"]
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

        store_number = str(store["locationId"])
        location_type = "<MISSING>"

        phone = store["phoneNumber"]

        attributes = store["locationAttributes"]
        hours_list = []
        for att in attributes:
            if "Monday-Thursday Hours" == att["name"]:
                time = att["value"]
                try:
                    time = time.split("(")[0].strip() + time.split(")")[1].strip()
                except:
                    pass

                if "Lobby:" in time:
                    time = time.split("Lobby: ")[1].strip()

                hours_list.append("Monday-Thursday:" + time)

            if "Friday Hours" == att["name"]:
                time = att["value"]
                try:
                    time = time.split("(")[0].strip() + time.split(")")[1].strip()
                except:
                    pass

                if "Lobby:" in time:
                    time = time.split("Lobby: ")[1].strip()

                hours_list.append("Friday:" + time)

        hours_of_operation = "; ".join(hours_list).strip()
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

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()

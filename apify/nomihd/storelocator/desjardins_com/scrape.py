# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json

website = "desjardins.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
    "Accept": "application/json, text/plain, */*",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
    "Origin": "https://www.desjardins.com",
    "Sec-Fetch-Site": "same-site",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://www.desjardins.com/",
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

    search_url = "https://pservices.desjardins.com/proxy/001/index_ps_en.json"
    stores_req = session.get(search_url, headers=headers)
    stores = json.loads(stores_req.text)["entrees"]
    for store in stores:
        store_number = store["id"]
        latitude = store["latitude"]
        longitude = store["longitude"]
        page_url = "<MISSING>"
        log.info(f"Pulling data for ID: {store_number}")
        store_req = session.get(
            "https://pservices.desjardins.com/caisses/donnees_caisses.nsf/traitement?Open&ic=details&l=en&id="
            + store_number,
            headers=headers,
        )

        try:
            store_json = json.loads(
                store_req.text.replace(",,,,", "").strip().replace(",,", ",").strip()
            )["entrees"][0]["info_caisse"]

            location_name = store_json["nom"]

            locator_domain = website

            location_type = "<MISSING>"
            if store["type"] == "3":
                location_type = "ATM"

            street_address = store_json["adr"]
            city = store_json["ville"]
            state = store_json["prov"]
            zip = store_json["cp"][:3] + " " + store_json["cp"][3:]
            phone = store_json["tel"]
            hours_of_operation = ""
            hours_list = []
            try:
                hours = json.loads(store_req.text)["entrees"][0]["heures_ouverture"][
                    "services"
                ][0]["jours"]
                for hour in hours:
                    day = ""
                    time = ""
                    if hour["jour"] == "1":
                        day = "Sunday:"
                    if hour["jour"] == "2":
                        day = "Monday:"
                    if hour["jour"] == "3":
                        day = "Tuesday:"
                    if hour["jour"] == "4":
                        day = "Wednesday:"
                    if hour["jour"] == "5":
                        day = "Thursday:"
                    if hour["jour"] == "6":
                        day = "Friday:"
                    if hour["jour"] == "7":
                        day = "Saturday:"

                    if len(hour["plages"]) > 0:
                        time = hour["plages"][0]["de"] + "-" + hour["plages"][0]["a"]
                    else:
                        time = "Closed"

                    hours_list.append(day + time)

            except:
                pass

            hours_of_operation = "; ".join(hours_list).strip()

            if store_number == "":
                store_number = "<MISSING>"

            if location_name == "":
                location_name = "<MISSING>"

            country_code = "CA"

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
        except:
            pass
    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()

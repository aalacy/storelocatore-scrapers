# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html

website = "hungryhorse.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "venuefinder.greeneking-pubs.co.uk",
    "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
    "accept": "*/*",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
    "content-type": "application/json",
    "origin": "https://www.hungryhorse.co.uk",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.hungryhorse.co.uk/",
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

    search_url = "https://www.hungryhorse.co.uk/find-us/"
    stores_req = session.get(search_url)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//li/a[@class="pub-list__pub-name"]/@href')
    for store_url in stores:
        page_url = "https://www.hungryhorse.co.uk" + store_url
        log.info(page_url)
        store_req = session.get(page_url)
        venueId = store_req.text.split("venueId: '")[1].strip().split("',")[0].strip()
        data = {
            "operationName": "Venue",
            "variables": {"id": venueId},
            "query": "query Venue($id: ID!) {\n  venue(id: $id) {\n    name\n    address {\n      line1\n      line2\n      line3\n      county\n      postcode\n    }\n    closed\n    phone\n    email\n    attributes {\n      name\n      value\n    }\n    location {\n      latitude\n      longitude\n    }\n    operatingHours {\n      close\n      comment\n      name\n      open\n    }\n    specialOperatingHours {\n      name\n      open\n      close\n      comment\n      date\n    }\n    servingHours {\n      name\n      start\n      end\n      comment\n    }\n    specialServingHours {\n      name\n      start\n      end\n      comment\n      date\n    }\n    urls {\n      directions\n      book\n    }\n  }\n}\n",
        }

        store_req = session.post(
            "https://venuefinder.greeneking-pubs.co.uk/graphql",
            json=data,
            headers=headers,
        )
        store_json = store_req.json()["data"]["venue"]
        locator_domain = website
        latitude = store_json["location"]["latitude"]
        longitude = store_json["location"]["longitude"]
        store_number = venueId
        location_name = store_json["name"]
        location_type = "<MISSING>"
        if store_json["closed"] is True:
            location_type = "Temporary Closed"

        street_address = store_json["address"]["line1"]
        city = store_json["address"]["line2"]
        state = store_json["address"]["county"]
        zip = store_json["address"]["postcode"]
        phone = store_json["phone"]

        hours = store_json["operatingHours"]
        hours_list = []
        for hour in hours:
            if hour["open"] is not None and len(hour["open"]) > 0:
                day = hour["name"]
                time = hour["open"] + "-" + hour["close"]
                hours_list.append(day + ":" + time)

        hours_of_operation = "; ".join(hours_list).strip()

        if store_number == "":
            store_number = "<MISSING>"

        if location_name == "":
            location_name = "<MISSING>"

        country_code = "GB"

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

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()

# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
import json

website = "bahamabreeze.com"
session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=website)


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

    headers = {
        "authority": "www.bahamabreeze.com",
        "cache-control": "max-age=0",
        "sec-ch-ua": '"Google Chrome";v="87", " Not;A Brand";v="99", "Chromium";v="87"',
        "sec-ch-ua-mobile": "?0",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "referer": "https://www.bahamabreeze.com/locations/all-locations",
        "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    }
    search_url = "https://www.bahamabreeze.com/locations/all-locations"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="cal_col"]/ul//li/a/@href')
    for store_url in stores:
        page_url = "https://www.bahamabreeze.com" + store_url.strip()
        locator_domain = website
        log.info(page_url)
        headers = {
            "authority": "www.bahamabreeze.com",
            "sec-ch-ua": '"Google Chrome";v="87", " Not;A Brand";v="99", "Chromium";v="87"',
            "sec-ch-ua-mobile": "?0",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "navigate",
            "sec-fetch-user": "?1",
            "sec-fetch-dest": "document",
            "referer": "https://www.bahamabreeze.com/locations/all-locations",
            "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
        }

        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        json_list = store_sel.xpath('//script[@type="application/ld+json"]/text()')
        for js in json_list:
            if "@type" in js:
                if json.loads(js)["@type"] == "Restaurant":
                    json_text = js
                    store_json = json.loads(json_text)

                    location_name = store_json["name"]
                    if location_name == "":
                        location_name = "<MISSING>"

                    street_address = store_json["address"]["streetAddress"]
                    city = store_json["address"]["addressLocality"]
                    state = store_json["address"]["addressRegion"]
                    zip = store_json["address"]["postalCode"]
                    country_code = store_json["address"]["addressCountry"]

                    if country_code == "" or country_code is None:
                        country_code = "<MISSING>"
                    if street_address == "":
                        street_address = "<MISSING>"

                    if city == "":
                        city = "<MISSING>"

                    if state == "":
                        state = "<MISSING>"

                    if zip == "":
                        zip = "<MISSING>"

                    store_number = store_json["branchCode"]
                    if store_number == "":
                        store_number = "<MISSING>"
                    phone = store_json["telephone"]

                    location_type = store_json["@type"]
                    if location_type == "":
                        location_type = "<MISSING>"

                    hours_of_operation = ""
                    hours_list = []
                    hours = store_json["openingHours"]
                    for hour in hours:
                        if len("".join(hour).strip()) > 0:
                            hours_list.append("".join(hour).strip())

                    hours_of_operation = "; ".join(hours_list).strip()

                    latitude = store_json["geo"]["latitude"]
                    longitude = store_json["geo"]["longitude"]

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

            else:
                location_name = "".join(
                    store_sel.xpath('//h1[@class="style_h1"]/text()')
                ).strip()
                if location_name == "":
                    location_name = "<MISSING>"

                street_address = "".join(
                    store_sel.xpath('//p[@id="info-link-webhead"]/text()[1]')
                ).strip()
                city_state_Zip = "".join(
                    store_sel.xpath('//p[@id="info-link-webhead"]/text()[2]')
                ).strip()
                city = city_state_Zip.split(",")[0].strip()
                state = city_state_Zip.split(",")[1].strip().split(" ")[0].strip()
                zip = city_state_Zip.split(",")[1].strip().split(" ")[1].strip()
                country_code = "US"

                if country_code == "" or country_code is None:
                    country_code = "<MISSING>"
                if street_address == "":
                    street_address = "<MISSING>"

                if city == "":
                    city = "<MISSING>"

                if state == "":
                    state = "<MISSING>"

                if zip == "":
                    zip = "<MISSING>"

                store_number = "<MISSING>"
                if store_number == "":
                    store_number = "<MISSING>"
                phone = "".join(
                    store_sel.xpath('//p[@id="info-link-webhead"]/text()[3]')
                ).strip()

                location_type = "<MISSING>"
                if location_type == "":
                    location_type = "<MISSING>"

                hours_of_operation = ""
                hours_list = []
                hours = store_sel.xpath('//div[@class="hours-section"]/span')
                total = int((len(hours) / 2))
                for index in range(0, total):
                    hours_list.append(
                        "".join(hours[index].xpath("text()")).strip()
                        + ":"
                        + "".join(hours[index + 1].xpath("text()")).strip()
                    )

                hours_of_operation = "; ".join(hours_list).strip()

                latitude = "<MISSING>"
                longitude = "<MISSING>"

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

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()

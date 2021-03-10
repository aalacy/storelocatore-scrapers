# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from sglogging import sglog
import json
import lxml.html
import us

website = "freepeople.com"
domain = "https://www.freepeople.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
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


def get_api_key(resp):

    json_config = (
        resp.split("window.urbn.runtimeConfig =")[1]
        .strip()
        .split('JSON.parse("')[1]
        .strip()
        .split('");')[0]
        .strip()
    )

    json_config = json_config.replace(r"\"", '"')
    return json_config


def get_day(day):

    week_day = ""
    if day == "1":
        week_day = "Sunday"
    if day == "2":
        week_day = "Monday"
    if day == "3":
        week_day = "Tuesday"
    if day == "4":
        week_day = "Wednesday"
    if day == "5":
        week_day = "Thursday"
    if day == "6":
        week_day = "Friday"
    if day == "7":
        week_day = "Saturday"

    return week_day


def append_zero(zip):

    if len(zip) == 1:
        zip = "0000" + zip
    if len(zip) == 2:
        zip = "000" + zip
    if len(zip) == 3:
        zip = "00" + zip
    if len(zip) == 4:
        zip = "0" + zip

    return zip


def fetch_data():
    # Your scraper here
    locator_domain = website
    page_url = ""
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zip = ""
    country_code = ""
    store_number = ""
    phone = ""
    location_type = ""
    latitude = ""
    longitude = ""
    hours_of_operation = ""
    loc_list = []

    api_resp = session.get("https://www.freepeople.com/stores/", headers=headers)
    json_config = get_api_key(api_resp.text)
    API_KEY = json.loads(json_config)["misl"]["apiKey"]
    locations_resp = session.get(
        "https://www.freepeople.com/stores/#?viewAll=true",
        headers=headers,
    )
    locations_sel = lxml.html.fromstring(locations_resp.text)
    stores = locations_sel.xpath('//a[@itemprop="url"]')
    stores_info = locations_sel.xpath(
        '//div[@itemtype="http://schema.org/LocalBusiness"]'
    )
    for index in range(0, len(stores)):
        page_url = domain + "".join(stores[index].xpath("@href")).strip()
        slug = page_url.split("/stores/")[-1].strip()
        if "/stores" in slug:

            page_url = "<MISSING>"
            location_name = temp_location = "".join(
                stores[index].xpath("span/text()")
            ).strip()
            if " - " in temp_location:
                location_name = temp_location.split(" - ")[0].strip()
                location_type = temp_location.split(" - ")[1].strip()

            street_address = "".join(
                stores_info[index].xpath(
                    'div[@itemprop="address"]/span[@itemprop="streetAddress"]/text()'
                )
            ).strip()
            city = "".join(
                stores_info[index].xpath(
                    'div[@itemprop="address"]/span[@itemprop="addressLocality"]/text()'
                )
            ).strip()
            state = "".join(
                stores_info[index].xpath(
                    'div[@itemprop="address"]/span[@itemprop="addressRegion"]/text()'
                )
            ).strip()
            if state == "":
                state = "<MISSING>"

            zip = "".join(
                stores_info[index].xpath(
                    'div[@itemprop="address"]/span[@itemprop="postalCode"]/text()'
                )
            ).strip()

            if location_type == "":
                location_type = "<MISSING>"

            latitude = "<MISSING>"
            longitude = "<MISSING>"

            if us.states.lookup(state):
                country_code = "US"
            else:
                country_code = "<MISSING>"

            store_number = "<MISSING>"
            phone = "<MISSING>"

            hours_of_operation = "<MISSING>"
            if country_code == "US":
                zip = append_zero(zip)

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

            stores_resp = session.get(
                (
                    "https://www.freepeople.com/api/misl/v1/stores/search?brandId=08%7C09"
                    "&slug={}&urbn_key={}"
                    "StoreLocatorService/getStoreDetailsByID"
                ).format(slug, API_KEY),
                headers=headers,
            )

            store_json = json.loads(stores_resp.text)["results"]
            if len(store_json) == 1:
                store_json = store_json[0]
                location_name = temp_location = store_json["addresses"]["marketing"][
                    "name"
                ]
                if " - " in temp_location:
                    location_name = temp_location.split(" - ")[0].strip()
                    location_type = temp_location.split(" - ")[1].strip()

                street_address = store_json["addresses"]["marketing"]["addressLineOne"]
                city = store_json["addresses"]["marketing"]["city"]
                state = store_json["addresses"]["marketing"]["state"]
                if state == "":
                    state = "<MISSING>"

                zip = store_json["addresses"]["marketing"]["zip"]
                if len(zip) == 4:
                    zip = "0" + zip

                if location_type == "":
                    location_type = "<MISSING>"

                latitude = store_json["loc"][1]
                longitude = store_json["loc"][0]

                country_code = store_json["addresses"]["iso2"]["country"]
                if country_code == "":
                    country_code = "<MISSING>"

                store_number = store_json["storeNumber"]
                phone = store_json["addresses"]["marketing"]["phoneNumber"]
                if phone == "":
                    phone = "<MISSING>"

                hours_of_operation = ""
                workingHours = store_json["hours"]
                for day, time in workingHours.items():
                    week_day = get_day(day)
                    hours_of_operation = (
                        hours_of_operation
                        + week_day
                        + " "
                        + workingHours[day]["open"]
                        + "-"
                        + workingHours[day]["close"]
                        + " "
                    )

                hours_of_operation = hours_of_operation.strip()
                if hours_of_operation == "":
                    hours_of_operation = "<MISSING>"

                if country_code == "US" or country_code == "CA":
                    if country_code == "US":
                        zip = append_zero(zip)
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
                    log.info(f"ignored because country is: {country_code}")
            else:
                log.info(f"\n{page_url} does not have any data to show\n")

        # break

    return loc_list


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()

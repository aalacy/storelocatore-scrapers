# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json

website = "stlouiswings.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
}


def get_ids(res):
    json_str = (
        '[{"type"'
        + res.split('"features":[{"type"')[1].split(']},"uiLocationsList"')[0]
        + "]"
    )
    json_res = json.loads(json_str)  # json_res is list and has all ids
    ids_list = []
    for obj in json_res:
        ids_list.append(str(obj["properties"]["id"]))

    ids = "%2C".join(ids_list)
    return ids


def fetch_data():
    # Your scraper here

    search_url = "https://locations.stlouiswings.com/"
    search_res = session.get(search_url, headers=headers)
    ids = get_ids(search_res.text)

    api_url = f"https://sls-api-service.sweetiq-sls-production-east.sweetiq.com/o8gc3jHgHQREe31VPdMNRnA9xMehpN/locations-details?locale=en_CA&ids={ids}&clientId=5a0361d5ec45394373a0b643&cname=locations.stlouiswings.com"

    api_res = session.get(api_url, headers=headers)
    json_res = json.loads(api_res.text)

    stores_list = json_res["features"]

    for store in stores_list:

        if store["properties"]["isPermanentlyClosed"]:
            continue

        page_url = search_url + store["properties"]["slug"].strip()
        locator_domain = website

        location_name = store["properties"]["name"].strip()

        street_address = store["properties"]["addressLine1"].strip()

        city = store["properties"]["city"].strip()
        state = store["properties"]["province"].strip()
        zip = store["properties"]["postalCode"].strip()
        country_code = store["properties"]["country"].strip()
        store_number = store["properties"]["branch"]

        phone = store["properties"]["phoneLabel"].strip()

        location_type = "<MISSING>"

        hours_info = store["properties"]["hoursOfOperation"]
        hours_list = []

        for day, time in hours_info.items():  # here time is [[opening, closing]]
            if time:
                opening = time[0][0]
                closing = time[0][1]
                hours_list.append(f"{day}: {opening} - {closing}")

        hours_of_operation = "; ".join(hours_list)
        if "temporarily closed" in store["properties"]["longDescription"]:
            location_type = "temporarily closed"
            hours_of_operation = "<MISSING>"

        if "Coming Soon" in store["properties"]["longDescription"]:
            location_type = "Coming Soon"

        latitude = store["geometry"]["coordinates"][1]
        longitude = store["geometry"]["coordinates"][0]

        raw_address = "<MISSING>"

        yield SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

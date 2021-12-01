# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "megafurnitureusa.com"
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

    search_url = "https://locations.megafurnitureusa.com/"
    search_res = session.get(search_url, headers=headers)
    ids = get_ids(search_res.text)

    api_url = f"https://sls-api-service.sweetiq-sls-production-east.sweetiq.com/9BpEAnHCDiw72SpaYYae6OAFdPdX4q/locations-details?locale=en_US&ids={ids}&clientId=5cc349a6b28726d02cd9b949&cname=locations.megafurnitureusa.com"

    api_res = session.get(api_url, headers=headers)

    json_res = json.loads(api_res.text)

    stores_list = json_res["features"]

    for store in stores_list:

        if (
            store["properties"]["isPermanentlyClosed"]
            or store["properties"]["metaStatus"] == "COMING_SOON"
        ):
            continue

        page_url = search_url + store["properties"]["slug"].strip()
        locator_domain = website

        location_name = store["properties"]["name"].strip()

        street_address = store["properties"]["addressLine1"].strip()

        if (
            "addressLine2" in store["properties"]
            and store["properties"]["addressLine2"] is not None
            and len(store["properties"]["addressLine2"]) > 0
        ):
            street_address = street_address + ", " + store["properties"]["addressLine2"]

        city = store["properties"]["city"].strip()
        location_name = location_name + " - " + city
        state = store["properties"]["province"].strip()
        zip = store["properties"]["postalCode"].strip()
        country_code = store["properties"]["country"].strip()
        store_number = store["properties"]["id"]

        phone = store["properties"]["phoneNumber"].strip()

        location_type = "<MISSING>"

        hours_info = store["properties"]["hoursOfOperation"]
        hours_list = []

        for day, time in hours_info.items():  # here time is [[opening, closing]]
            if time:
                opening = time[0][0]
                closing = time[0][1]
                hours_list.append(f"{day}: {opening} - {closing}")

        hours_of_operation = "; ".join(hours_list)

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
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

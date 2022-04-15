# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "freepeople.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def get_api_key(resp):

    json_config = (
        resp.split("window.urbn.config =")[1]
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
    api_resp = session.get("https://www.freepeople.com/stores/", headers=headers)
    json_config = get_api_key(api_resp.text)
    API_KEY = json.loads(json_config)["misl"]["apiKey"]
    stores_resp = session.get(
        (
            "https://www.freepeople.com/api/misl/v1/stores/search?brandId=08%7C09&distance=25&urbn_key={}"
        ).format(API_KEY),
        headers=headers,
    )

    stores = json.loads(stores_resp.text)["results"]
    for store_json in stores:
        page_url = "<MISSING>"
        if "slug" in store_json:
            page_url = "https://www.freepeople.com/stores/" + store_json["slug"]
        location_name = store_json["addresses"]["marketing"]["name"]

        street_address = store_json["addresses"]["marketing"]["addressLineOne"]
        city = store_json["addresses"]["marketing"]["city"]
        state = store_json["addresses"]["marketing"]["state"]

        zip = store_json["addresses"]["marketing"]["zip"]
        location_type = store_json["brandName"]
        latitude = ""
        longitude = ""
        try:
            latitude = store_json["loc"][1]
        except:
            pass

        try:
            longitude = store_json["loc"][0]
        except:
            pass

        try:
            country_code = store_json["addresses"]["iso2"]["country"]
        except:
            country_code = store_json["country"]

        store_number = store_json["storeNumber"]
        phone = "<MISSING>"
        try:
            phone = store_json["addresses"]["marketing"]["phoneNumber"]
        except:
            pass

        if phone == "(???)???-???" or phone == "(???) ???-????":
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

        if country_code == "US":
            zip = append_zero(zip)

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

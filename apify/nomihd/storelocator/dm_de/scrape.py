# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "dm.de"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "store-data-service.services.dmtech.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    "accept": "application/json, text/plain, */*",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "origin": "https://www.dm.de",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.dm.de/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    with SgRequests() as session:
        for index in range(0, 4):
            countries_req = session.get(
                f"https://store-data-service.services.dmtech.com/stores/cluster/85.999%2C-179.999%2C-89.999%2C179.999/{index}",
                headers=headers,
            )
            countries_json = countries_req.json()
            for country in countries_json.keys():
                lat = countries_json[country]["centerPoint"]["lat"]
                lng = countries_json[country]["centerPoint"]["lon"]
                lat1 = lat
                lat2 = lat - 0.09
                lng1 = lng
                lng2 = lng + 0.09

                BBOX = f"{lat1},{lng1},{lat2},{lng2}"
                log.info(BBOX)
                stores_req = session.get(
                    "https://store-data-service.services.dmtech.com/stores/bbox/"
                    + BBOX,
                    headers=headers,
                )
                stores = json.loads(stores_req.text)["stores"]

                for store in stores:
                    page_url = store["storeUrlPath"]
                    if page_url:
                        page_url = "https://www.dm.de/store" + page_url
                    locator_domain = website
                    location_name = store["address"]["street"]
                    street_address = store["address"]["street"]
                    city = store["address"]["city"]
                    state = "<MISSING>"
                    zip = store["address"]["zip"]

                    country_code = store["countryCode"]

                    store_number = store["storeNumber"]
                    phone = store["phone"]

                    location_type = "<MISSING>"
                    hours_list = []
                    hours = store["openingHours"]
                    for hour in hours:
                        if hour["weekDay"] == 1:
                            day = "Monday:"
                        if hour["weekDay"] == 2:
                            day = "Tuesday:"
                        if hour["weekDay"] == 3:
                            day = "Wednesday:"
                        if hour["weekDay"] == 4:
                            day = "Thursday:"
                        if hour["weekDay"] == 5:
                            day = "Friday:"
                        if hour["weekDay"] == 6:
                            day = "Saturday:"
                        if hour["weekDay"] == 7:
                            day = "Sunday:"

                        time = (
                            hour["timeRanges"][0]["opening"]
                            + " - "
                            + hour["timeRanges"][0]["closing"]
                        )
                        hours_list.append(day + time)

                    hours_of_operation = "; ".join(hours_list).strip()

                    latitude = store["location"]["lat"]
                    longitude = store["location"]["lon"]

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
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.ZIP,
                    SgRecord.Headers.COUNTRY_CODE,
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.PAGE_URL,
                }
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

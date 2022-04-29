# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "easyfinancial.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "be.easyfinancial.com",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "accept": "*/*",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "content-type": "application/json",
    "origin": "https://www.easyfinancial.com",
    "sec-fetch-site": "same-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.easyfinancial.com/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}

params = (("code", "WLcdq2dRebMBytNYRbk7l/FOdQ8zAMXsKacLZV3vSqOJzknemwL9PQ=="),)

data = '{"operationName":"getAllBranches","variables":{"lat":44.1018128,"lng":-77.5756806,"radius":50000},"query":"query getAllBranches($lat: Float, $lng: Float, $radius: Float) {\\n getAllBranches(lat: $lat, lng: $lng, radius: $radius)\\n}\\n"}'


def fetch_data():
    # Your scraper here
    stores_req = session.post(
        "https://be.easyfinancial.com/api/src",
        headers=headers,
        params=params,
        data=data,
    )
    stores = json.loads(stores_req.text)["data"]["getAllBranches"]

    for store in stores:
        page_url = "<MISSING>"
        locator_domain = website
        location_name = store["storeNameC"]
        street_address = store["addressC"]
        if store["address2C"] is not None and len(store["address2C"]) > 0:
            street_address = street_address + ", " + store["address2C"]

        city = store["cityC"]
        state = store["provinceStateC"]
        if "-" in state:
            state = state.split("-")[0].strip()

        zip = store["postalCodeC"]

        country_code = store["countryC"]

        store_number = store["storeCodeC"]
        phone = store["storePhoneC"]

        location_type = store["typeC"]

        hours_list = []
        try:
            temp_hours = (
                "Mon-Fri:"
                + store["weekdayOpenC"][:2]
                + ":"
                + store["weekdayOpenC"][2:]
                + "-"
                + store["weekdayCloseC"][:2]
                + ":"
                + store["weekdayCloseC"][2:]
            )
            hours_list.append(temp_hours)
        except:
            pass

        try:
            temp_hours = (
                "Sat:"
                + store["saturdayOpenC"][:2]
                + ":"
                + store["saturdayOpenC"][2:]
                + "-"
                + store["saturdayCloseC"][:2]
                + ":"
                + store["saturdayCloseC"][2:]
            )
            hours_list.append(temp_hours)
        except:
            pass

        try:
            temp_hours = (
                "Sun:"
                + store["sundayOpenC"][:2]
                + ":"
                + store["sundayOpenC"][2:]
                + "-"
                + store["sundayCloseC"][:2]
                + ":"
                + store["sundayCloseC"][2:]
            )
            hours_list.append(temp_hours)
        except:
            pass

        hours_of_operation = "; ".join(hours_list).strip()

        latitude = str(store["lat"])
        longitude = str(store["lng"])

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

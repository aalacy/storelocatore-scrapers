# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "bppulse.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "api-ev-app.bp.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "accept": "*/*",
    "content-type": "application/json",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "x-api-key": "SIyw2j1kFfaV1FXkwgOEN5mKdA7rN16G2eph3HR8",
    "sec-ch-ua-platform": '"Windows"',
    "origin": "https://www.bppulse.co.uk",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.bppulse.co.uk/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.bppulse.co.uk/pulse-point-map"
    data = '{"operationName":"chargepointList","variables":{"from":offset,"size":100,"lat":51.50746,"lon":-0.11262},"query":"query chargepointList($from: Int, $size: Int, $lat: Float, $lon: Float) {\\n  chargepoints(from: $from, size: $size, lat: $lat, lon: $lon) {\\n    status\\n    data {\\n      available\\n      id\\n      address\\n      city\\n      postcode\\n      location {\\n        lat\\n        lon\\n        __typename\\n      }\\n      hours: hours_of_operation {\\n        mon1\\n        mon2\\n        tue1\\n        tue2\\n        wed1\\n        wed2\\n        thu1\\n        thu2\\n        fri1\\n        fri2\\n        sat1\\n        sat2\\n        sun1\\n        sat2\\n        __typename\\n      }\\n      connectors {\\n        connectorNum\\n        state\\n        type\\n        rating\\n        __typename\\n      }\\n      connectorFormat: connector_format\\n      free\\n      overstayFee: overstay_fee\\n      lastCharge: last_charge\\n      costCharge: costCharge {\\n        tariff: Tariff {\\n          type: Type\\n          cost: Cost\\n          unit: Unit\\n          multiplier: Multiplier\\n          __typename\\n        }\\n        minimumCharge: Minimum_Charge_Amount {\\n          type: Type\\n          cost: Cost\\n          unit: Unit\\n          __typename\\n        }\\n        __typename\\n      }\\n      deleted\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n"}'

    offset = 0
    with SgRequests(dont_retry_status_codes=([404])) as session:
        while True:
            log.info(f"fetching records starting from: {offset+100}")
            stores_req = session.post(
                "https://api-ev-app.bp.com/Chargemaster/v4",
                headers=headers,
                data=data.replace("offset", str(offset)),
            )
            if "chargepoints" not in stores_req.text:
                break

            stores = json.loads(stores_req.text)["data"]["chargepoints"]["data"]
            if len(stores) <= 0:
                break
            for store in stores:
                if store["available"] is None:
                    continue
                page_url = search_url

                locator_domain = website
                store_number = store["id"]
                location_name = f"Charge Point- {store_number}"
                street_address = store["address"]
                city = store["city"]
                state = "<MISSING>"
                zip = store["postcode"]
                country_code = "GB"

                phone = "<MISSING>"

                location_type = store["__typename"]

                hours_of_operation = "<MISSING>"
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

            offset = offset + 100


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

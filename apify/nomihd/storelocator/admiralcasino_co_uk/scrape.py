# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "admiralcasino.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "apiproxy.admiralcasino.co.uk",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    "accept-language": "en",
    "sec-ch-ua-mobile": "?0",
    "authorization": 'Bearer ""',
    "content-language": "en",
    "accept": "application/json",
    "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzaXRlIjoiYWRtaXJhbGNhc2lub2NvdWsiLCJhcHAiOiJ3ZWIiLCJpYXQiOjE0NzcwNTM2MzR9.P5_j-l0NxeruKUPWg-rzzCwinHv1X_SEE8pgRrBaZ3Y",
    "content-type": "application/json",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "origin": "https://www.admiralcasino.co.uk",
    "sec-fetch-site": "same-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.admiralcasino.co.uk/",
}


def fetch_data():
    # Your scraper here
    search_url = "https://apiproxy.admiralcasino.co.uk/proxy/v1/venue"
    with SgRequests() as session:
        stores_req = session.get(search_url, headers=headers)
        stores = json.loads(stores_req.text)
        for store in stores:
            page_url = "https://www.admiralcasino.co.uk/en/venues"
            locator_domain = website
            location_name = store["name"]

            street_address = store["address"]
            city = store["city"]
            state = "<MISSING>"
            zip = store["postcode"]

            country_code = "GB"
            store_number = store["id"]
            phone = store["telephone"]

            location_type = "<MISSING>"

            latitude = store["lat"]
            longitude = store["lng"]

            hours_of_operation = store["hours"]

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

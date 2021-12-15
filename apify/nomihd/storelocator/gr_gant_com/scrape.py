# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "gr.gant.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "gr.gant.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    with SgRequests(dont_retry_status_codes=([404])) as session:
        search_url = "https://gr.gant.com/pages/store-locator"
        stores_req = session.get(
            search_url,
            headers=headers,
        )
        stores = eval(
            stores_req.text.split('"data": ')[1]
            .strip()
            .split("],")[0]
            .strip()
            .replace("//Northwest", "")
            .strip()
            + "]"
        )
        for store in stores:
            store_number = "<MISSING>"
            locator_domain = website
            page_url = search_url
            location_name = store["name"]
            raw_address = store["address"]
            street_address = raw_address.split(",")[0].strip()
            city = "<MISSING>"
            if "-" in location_name:
                city = location_name.split("-")[1].strip().split("(")[0].strip()
            state = "<MISSING>"
            zip = "<MISSING>"

            country_code = "GR"

            phone = store["text"]
            try:
                phone = phone.split(":")[-1].strip()
            except:
                pass
            location_type = "<MISSING>"

            latitude = store["lat"]
            longitude = store["lng"]

            hours_of_operation = store["opening"]

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
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

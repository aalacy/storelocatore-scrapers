# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import csv

website = "jeep.rs"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "Accept": "*/*",
    "Referer": "https://www.fiatsrbija.rs/jeep-sajt/dileri/",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.fiatsrbija.rs/jeep-sajt/dileri/jeep.csv"
    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)
        text = search_res.iter_lines()
        reader = csv.reader(text)

        count = 0
        for row in reader:
            if count > 0:
                location_type = row[0].strip()
                page_url = search_url
                locator_domain = website
                location_name = row[2].strip()

                street_address = row[3].strip()
                city = row[1].strip()
                zip = row[7].strip()
                state = row[6].strip()

                country_code = "<MISSING>"

                phone = (
                    row[5].strip().split("<br")[0].strip().replace("Tel:", "").strip()
                )
                store_number = row[14].strip()

                hours_of_operation = "<MISSING>"
                latitude, longitude = row[13].strip(), row[12].strip()
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
            else:
                count = count + 1


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

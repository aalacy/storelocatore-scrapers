# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import ast

website = "centra.ie"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "centra.ie",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://centra.ie/locate"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        markers = search_res.text.split("var marker = addMarker")

        for index in range(1, len(markers)):
            store_info = ast.literal_eval(
                markers[index]
                .split(";")[0]
                .strip()
                .replace("true", "True")
                .replace("false", "False")
            )

            locator_domain = website
            page_url = "https://centra.ie" + store_info[9]
            location_name = store_info[2]
            location_type = "<MISSING>"

            raw_address = (
                store_info[4]
                .replace("<br \\/>", "")
                .strip()
                .replace("\n", " ")
                .strip()
                .replace("\\/", "/")
                .strip()
            )
            temp_address = raw_address.split(",")
            street_address = ", ".join(temp_address[:-3]).strip()
            if (
                len(street_address.split(",")) > 1
                and street_address.split(",")[0] == "Centra"
            ):
                street_address = ", ".join(temp_address[1:-3]).strip()

            city = temp_address[-3]
            state = temp_address[-2]
            zip = temp_address[-1]

            country_code = "IE"

            phone = store_info[6]
            hours_of_operation = (
                store_info[5]
                .replace("<br \\/>", "")
                .strip()
                .replace("\n", "; ")
                .strip()
            )

            store_number = store_info[8]
            latitude, longitude = store_info[0], store_info[1]

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

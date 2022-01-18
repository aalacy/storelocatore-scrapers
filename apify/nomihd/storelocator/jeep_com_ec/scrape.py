# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "jeep.com.ec"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.fiat.ec",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.jeep.com.ec/concesionarios-jeep-nueva"
    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        store_list = search_res.text.split("tabla.push(")

        for index in range(1, len(store_list)):
            store_info = store_list[index].split(");")[0].strip()
            page_url = search_url
            locator_domain = website
            location_name = (
                store_info.split("content:'")[1].strip().split("'")[0].strip()
            )

            street_address = (
                store_info.split("direccion:'")[1].strip().split("'")[0].strip()
            )
            city = store_info.split("ciudad:'")[1].strip().split("'")[0].strip()
            state = "<MISSING>"
            zip = "<MISSING>"

            country_code = "EC"

            phone = store_info.split("telc:'")[1].strip().split("'")[0].strip()
            if len(phone) <= 0:
                phone = store_info.split("telp:'")[1].strip().split("'")[0].strip()

            phone = phone.split("/")[0].strip().replace('"', "").strip()
            store_number = store_info.split("id:'")[1].strip().split("'")[0].strip()

            location_type = store_info.split("tipo:'")[1].strip().split("'")[0].strip()

            hours_of_operation = (
                store_info.split("horarios:'")[1]
                .strip()
                .split("'")[0]
                .strip()
                .replace("<br>", "; ")
                .strip()
            )
            latitude, longitude = (
                store_info.split("coords:{lat:")[1].strip().split(",")[0].strip(),
                store_info.split("coords:{lat:")[1]
                .strip()
                .split("lng:")[1]
                .strip()
                .split("}")[0]
                .strip(),
            )

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

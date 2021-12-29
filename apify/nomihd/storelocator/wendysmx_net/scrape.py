# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "wendysmx.net"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "wendysmx.net",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "http://wendysmx.net/sucursales.php"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    for num in range(1, 10):
        store_list = search_sel.xpath(
            f'//div[@class="sucurcont"][count(preceding::div[@class="titsuc"])={num}]'
        )
        if not store_list:
            break
        city_name = search_sel.xpath(
            f'//div[@class="sucurcont"][count(preceding::div[@class="titsuc"])={num}]/preceding::div[@class="titsuc"]//text()'
        )

        for store in store_list:

            page_url = search_url

            locator_domain = website

            store_info = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store.xpath(
                            './div[contains(@class,"sucdatos")]//text()'
                        )
                    ],
                )
            )

            raw_address = "<MISSING>"

            street_address = store_info[0].strip()
            city = city_name[-1].strip()
            state = "<MISSING>"
            zip = "<MISSING>"
            country_code = "MX"

            location_name = " ".join(
                store.xpath('.//div[@class="sucname"]//text()')
            ).strip()

            phone = store_info[1].replace("Tel.", "").strip()
            store_number = "<MISSING>"

            location_type = "<MISSING>"
            hours_of_operation = store_info[-2].strip()
            if "Cerrado temporalmente" in hours_of_operation:
                location_type = "Temporarily Closed"

            latitude, longitude = "<MISSING>", "<MISSING>"

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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

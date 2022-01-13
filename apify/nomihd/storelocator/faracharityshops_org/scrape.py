# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "faracharityshops.org"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.faracharity.org",
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

    for no in range(1, 100):
        search_url = f"https://www.faracharity.org/fara-shop/find-a-shop/page/{no}/"
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)

        store_list = search_sel.xpath('//div[@class="cards"]/article')
        if not store_list:
            break

        for store in store_list:

            page_url = "".join(store.xpath(".//h3/a/@href")).strip()

            log.info(page_url)
            store_res = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_res.text)

            locator_domain = website

            store_info = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            '//li[contains(@class,"location")]//text()'
                        )
                    ],
                )
            )

            street_address = (
                ", ".join(store_info[1:]).split("London")[0].strip(", ").strip()
            )
            city = "London"
            state = "<MISSING>"
            zip = store_info[-1].replace("London", "").strip(", ").strip()
            if "," in street_address:
                state = street_address.split(",")[1].strip()
                street_address = street_address.split(",")[0].strip()

            country_code = "GB"

            location_name = "".join(store.xpath(".//h3//text()")).strip()
            phone = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            '//li[contains(@class,"hours")]//text()'
                        )
                    ],
                )
            )
            phone = phone[-1].strip()

            store_number = "<MISSING>"

            location_type = "<MISSING>"
            hours = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            '//li[contains(@class,"hours")]//text()'
                        )
                    ],
                )
            )
            hours_of_operation = (
                "; ".join(hours[1:-2])
                .replace("Now Open!;", "")
                .replace(":;", ":")
                .replace("Temporarily Closed;", "")
                .strip()
            )
            if hours[0] == "Temporarily Closed":
                location_type = "Temporarily Closed"
            latitude, longitude = "<MISSING>", "<MISSING>"
            raw_address = "<MISSING>"

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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

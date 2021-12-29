# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "hartfordmedicalgroup.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "sec-ch-ua": '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://hartfordhealthcaremedicalgroup.org/locations"

    with SgRequests(dont_retry_status_codes=set([404])) as session:
        search_res = session.get(search_url, headers=headers)
        search_sel = lxml.html.fromstring(search_res.text)

        stores = search_sel.xpath('//div[@class="CLContentDataView"]//li')
        for store in stores:

            page_url = (
                "https://hartfordhealthcaremedicalgroup.org"
                + "".join(store.xpath("@data-href")).strip()
            )
            log.info(page_url)
            page_res = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(page_res.text)

            locator_domain = website

            location_name = "Hartfod HealthCare "

            street_address = "".join(store.xpath("@data-address1")).strip()
            add_2 = "".join(store.xpath("@data-address2")).strip()
            if len(add_2) > 0:
                street_address = street_address + ", " + add_2

            city = "".join(store.xpath("@data-city")).strip()
            state = "".join(store.xpath("@data-state")).strip()
            zip = "".join(store.xpath("@data-zip-code")).strip()
            country_code = "US"
            store_number = "<MISSING>"

            phone = store.xpath("@data-phone")
            if len(phone) <= 0:
                phone = store_sel.xpath(
                    '//p[./strong[contains(text(),"Phone")]]/a/text()'
                )
                if len(phone) <= 0:
                    phone = store_sel.xpath(
                        '//div[./h2[contains(text(),"Contact Us:")]]//a/text()'
                    )
                if len(phone) <= 0:
                    phone = store_sel.xpath(
                        './/div[@class="middle"]//a[contains(@href,"tel:")]/text()'
                    )
            if len(phone) > 0:
                phone = phone[0]

            if len("".join(phone)) <= 0:
                phone = "<MISSING>"

            location_type = (
                page_url.split("/locations/")[1]
                .strip()
                .split("/")[0]
                .strip()
                .replace("-", " ")
                .strip()
            )
            location_name = location_name + location_type

            hours_of_operation = "".join(
                store_sel.xpath(
                    '//td[./strong[contains(text(),"Primary Care Hours:")]]/text()'
                )
            ).strip()
            if len(hours_of_operation) <= 0:
                hours_of_operation = (
                    " ".join(
                        store_sel.xpath(
                            '//div[./h2[contains(text(),"Hours:")]]/h2/span//text()'
                        )
                    )
                    .strip()
                    .replace("\n", "")
                    .strip()
                )
            if len(hours_of_operation) <= 0:
                hours_of_operation = (
                    " ".join(
                        store_sel.xpath(
                            '//div[./h2[contains(text(),"Hours:")]]/p//text()'
                        )
                    )
                    .strip()
                    .split("Phone")[0]
                    .strip()
                    .replace("\n", "")
                    .strip()
                )

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

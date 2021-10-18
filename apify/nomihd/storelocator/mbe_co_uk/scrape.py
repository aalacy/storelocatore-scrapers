# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "mbe.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.mbe.co.uk",
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
    search_url = "https://www.mbe.co.uk/"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    store_list = search_sel.xpath('//div[contains(@class,"storeSearch")]//option')

    for store in store_list[1:]:

        page_url = search_url + "".join(store.xpath("./@value"))
        locator_domain = website

        log.info(page_url)
        store_res = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_res.text)

        street_address = (
            store_res.text.split('"streetAddress":')[1]
            .split('",')[0]
            .strip('" ')
            .strip()
        )
        city = (
            store_res.text.split('"addressLocality":')[1]
            .split('",')[0]
            .strip('" ')
            .strip()
        )
        state = (
            store_res.text.split('"addressRegion":')[1]
            .split('",')[0]
            .strip('" ')
            .strip()
        )
        zip = (
            store_res.text.split('"postalCode":')[1].split('",')[0].strip('" ').strip()
        )
        country_code = "GB"

        location_name = (
            store_res.text.split('"name":')[1].split('",')[0].replace('"', "").strip()
        )
        phone = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store_sel.xpath('//a[contains(@href,"tel:")]/text()')
                ],
            )
        )
        phone = phone[0].strip()

        store_number = "<MISSING>"

        location_type = "<MISSING>"
        hours = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store_sel.xpath(
                        '//div[contains(@class,"store-details")][h5]//text()'
                    )
                ],
            )
        )
        hours_of_operation = (
            "; ".join(hours[1:])
            .replace("Now Open!;", "")
            .replace(":;", ":")
            .strip()
            .replace("day;", "day:")
            .replace("days;", "days:")
        )

        latitude, longitude = (
            store_res.text.split('"latitude":')[1].split(",")[0].strip(),
            store_res.text.split('"longitude":')[1].split("},")[0].strip(),
        )

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

# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "bankwestmn.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.bankwestmn.com",
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
    base = "https://www.bankwestmn.com"
    search_url = "https://www.bankwestmn.com/about-us/locations-hours.html"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    store_list = search_sel.xpath('//ul[@id="locList"]/li')

    for store in store_list:

        page_url = base + "".join(store.xpath('.//a[@class="seeDetails"]/@href'))

        locator_domain = website

        street_address = "".join(store.xpath("./@data-address1")).strip()
        street_address = (
            (street_address + ", " + "".join(store.xpath("./@data-address2")).strip())
            .strip(", ")
            .strip()
        )

        city = "".join(store.xpath("./@data-city")).strip()
        state = "".join(store.xpath("./@data-state")).strip()
        zip = "".join(store.xpath("./@data-zip")).strip()
        country_code = "US"
        location_name = "".join(store.xpath("./@data-title")).strip()

        phone = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store.xpath(
                        './/*[text()="Phone"]/../*[@class="value"]/text()'
                    )
                ],
            )
        )
        phone = phone[0].strip()

        store_number = page_url.split("id=")[1].split("&")[0].strip()

        location_type = "<MISSING>"
        hours = list(
            filter(
                str,
                [x.strip() for x in store.xpath('.//*[@class="lobbyHours"]//text()')],
            )
        )
        hours_of_operation = (
            "; ".join(hours[1:]).replace("day;", "day:").replace("ri;", "ri:").strip()
        )

        latitude, longitude = "".join(store.xpath("./@data-latitude")), "".join(
            store.xpath("./@data-longitude")
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

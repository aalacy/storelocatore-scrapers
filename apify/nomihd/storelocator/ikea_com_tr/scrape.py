# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "ikea.com.tr"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "sec-ch-ua": '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.ikea.com.tr/en/stores.aspx"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    store_list = search_sel.xpath(
        '//div[@class="malls-city height-wrap"]/div[@class="row"]/div'
    )

    for store in store_list:

        page_url = (
            "https://www.ikea.com.tr"
            + "".join(store.xpath('a[contains(text(),"More Info")]/@href')).strip()
        )
        if "pick-up-point" in page_url:
            continue

        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        locator_domain = website

        location_name = "".join(
            store_sel.xpath("//h1[@class='page-title']/text()")
        ).strip()
        raw_address = store_sel.xpath(
            '//div[@class="address-item"][./i[@class="icon-adres"]]/p/text()'
        )
        street_address = (
            ", ".join(raw_address[2:-2])
            .strip()
            .replace("\n", "")
            .strip()
            .replace(".,", ",")
            .strip()
        )
        city = "".join(raw_address[-1]).strip()
        state = "".join(raw_address[-2]).strip().split(" ")[-1].strip()
        zip = "".join(raw_address[-2]).strip().split(" ")[0].strip()
        country_code = "TR"

        phone = "".join(
            store_sel.xpath(
                '//div[@class="address-item"][./i[@class="icon-musteri"]]/a/text()'
            )
        ).strip()
        latitude = "".join(store.xpath("@data-latitude")).strip()
        longitude = "".join(store.xpath("@data-longitude")).strip()
        store_number = "<MISSING>"

        location_type = "<MISSING>"
        hours = store_sel.xpath(
            '//div[@class="address-item"][./i[@class="icon-magaza-saat"]]/p/text()'
        )
        hours_list = []
        for hour in hours:
            if len("".join(hour).strip()) > 0:
                hours_list.append("".join(hour).strip())

        hours_of_operation = "; ".join(hours_list).strip()
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

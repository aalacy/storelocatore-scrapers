# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "fortunoffbys.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "sec-ch-ua": '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.fortunoffbys.com/locations.inc"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    stores = search_sel.xpath('//a[contains(text(),"View Store Details")]/@href')

    for store_url in stores:

        page_url = "https://www.fortunoffbys.com" + store_url
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        locator_domain = website
        location_name = "".join(
            store_sel.xpath('//div[@id="pagetitle"]/h1/text()')
        ).strip()

        raw_address = store_sel.xpath(
            '//p[.//text()="Address:"]/following-sibling::p[1]/text()'
        )
        add_list = []
        for add in raw_address:
            if "(" in add:
                continue
            add_list.append(add)

        street_address = ", ".join(add_list[:-1]).strip().replace("\n", "").strip()

        city_state_zip = add_list[-1]
        city = city_state_zip.split(",")[0].strip()
        state = city_state_zip.split(",")[1].strip().split(" ")[0].strip()
        zip = city_state_zip.split(",")[1].strip().split(" ")[-1].strip()
        street_address = (
            (
                street_address.replace(" " + state, "")
                .strip()
                .replace(" " + zip, "")
                .strip()
            )
            .replace(",  ,", ",")
            .strip()
            .replace(",,", ",")
            .strip()
            .replace("The Source Mall,", "")
            .strip()
            .replace(", Store 11-12", "")
            .strip()
        )
        country_code = "US"

        store_number = "<MISSING>"

        location_type = "<MISSING>"
        phone = "".join(
            store_sel.xpath('//p[.//text()="Phone:"]/following-sibling::p[1]//text()')
        ).strip()
        hours = (
            " ".join(
                store_sel.xpath(
                    '//p[.//text()="Hours:"]/following-sibling::p[1]//text()'
                )
            )
            .strip()
            .split("\n")
        )
        hours_list = []
        for hour in hours:
            if len("".join(hour).strip()) > 0:
                hours_list.append("".join(hour).strip())

        hours_of_operation = "; ".join(hours_list).strip()
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

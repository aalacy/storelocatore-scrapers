# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "nubiyogurt.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    base = "http://www.nubiyogurt.com/"
    search_url = "http://www.nubiyogurt.com/cafes.html"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    store_list = search_sel.xpath('//div[@id="locations"]//a/@href')

    for store_url in store_list:

        page_url = base + store_url
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        locator_domain = website
        raw_info = store_sel.xpath('//div[contains(@id,"text")]//text()')

        raw_list = []
        for raw in raw_info:
            if len("".join(raw).strip()) > 0:
                raw_list.append("".join(raw).strip())

        location_name = raw_list[0].strip()

        street_address = raw_list[2].strip()

        city_state_zip = raw_list[3].strip()
        if "," in city_state_zip:
            city = city_state_zip.split(",")[0].strip()
            state = city_state_zip.split(",")[-1].strip().split(" ")[0].strip()
            zip = city_state_zip.split(",")[-1].strip().split(" ")[-1].strip()
        else:
            city = city_state_zip.split(" ")[0].strip()
            state = city_state_zip.split(" ")[1].strip()
            zip = city_state_zip.split(" ")[-1].strip()

        country_code = "US"

        phone = raw_list[4].strip().replace("T", "").strip()

        store_number = "<MISSING>"

        location_type = "<MISSING>"
        hours_of_operation = raw_list[-2].strip()
        map_link = "".join(
            store_sel.xpath('//a[contains(@href,"maps.google.com")]/@href')
        ).strip()

        latitude, longitude = "<MISSING>", "<MISSING>"
        if "sll=" in map_link:
            latitude = map_link.split("sll=")[1].strip().split(",")[0].strip()
            longitude = (
                map_link.split("sll=")[1]
                .strip()
                .split(",")[1]
                .strip()
                .split("&")[0]
                .strip()
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

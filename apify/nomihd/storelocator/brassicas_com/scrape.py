# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "brassicas.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://brassicas.com/locations/"
    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)

    stores_list = search_sel.xpath('//div[@class="tile"]//a/@href')

    for store_url in stores_list:
        if "/locations/" not in store_url:
            continue
        page_url = store_url
        locator_domain = website
        log.info(store_url)
        page_res = session.get(store_url, headers=headers)
        page_sel = lxml.html.fromstring(page_res.text)

        location_name = "".join(page_sel.xpath("//h1/text()")).strip()

        details_info = list(
            filter(
                str,
                page_sel.xpath('//div[@class="copy"]/p//text()'),
            )
        )
        details_info = details_info[1:]
        try:
            details_info.remove("\xa0")
        except:
            pass

        street_address = details_info[0].strip()

        city = details_info[1].split(",")[0].strip()

        state = details_info[1].split(",")[1].strip().split(" ")[0].strip()
        zip = details_info[1].split(",")[1].strip().split(" ")[1].strip()

        country_code = "US"

        store_number = "<MISSING>"

        phone = details_info[-2].strip()

        location_type = "<MISSING>"

        hours_of_operation = details_info[-1].strip()

        lat_lng_info = (
            page_res.text.split("var position = {")[1].split("markerlink")[0].strip()
        )
        latitude = (
            lat_lng_info.split(",")[0].replace("latitude", "").strip(" :").strip()
        )
        longitude = (
            lat_lng_info.split(",")[1]
            .replace("longitude", "")
            .strip(" :")
            .strip()
            .replace(":", "")
            .strip()
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

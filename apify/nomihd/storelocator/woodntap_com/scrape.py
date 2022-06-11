# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "woodntap.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Referer": "https://www.woodntap.com/locations",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    stores_req = session.get("https://www.woodntap.com/", headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//li[./a[text()="Locations"]]/ul/li/a/@href')
    for store_url in stores:

        page_url = store_url
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        locator_domain = website

        location_name = "".join(
            store_sel.xpath('//div[@class="page-masthead-body"]/h1/text()')
        ).strip()

        address = store_sel.xpath('//div[@class="page-masthead-body"]/address//text()')
        add_list = []
        for add in address:
            if len("".join(add).strip()) > 0:
                add_list.append("".join(add).strip())

        street_address = add_list[0].strip()
        if street_address[-1] == ",":
            street_address = "".join(street_address[:-1]).strip()

        city = add_list[-1].strip().split(",")[0].strip()
        state_zip = add_list[-1].strip().split(",")[-1].strip().split(" ")
        state = "<MISSING>"
        zip = "<MISSING>"
        if len(state_zip) > 1:
            state = state_zip[0].strip()
            zip = state_zip[-1].strip()
        else:
            state = state_zip[0].strip()

        country_code = "US"

        store_number = "<MISSING>"

        phone = "".join(
            store_sel.xpath(
                '//div[@class="page-masthead-body"]//a[@class="phone"]/text()'
            )
        ).strip()

        location_type = "<MISSING>"
        if "We are CLOSED temporarily" in store_req.text:
            location_type = "temporarily closed"

        hours_of_operation = (
            "; ".join(
                store_sel.xpath(
                    '//div[@class="info-card "][./header/h3[contains(text(),"Hours")]]/div[@class="info-card-body"]/text()'
                )
            )
            .strip()
            .split("\n")[0]
            .strip()
        )
        if len(hours_of_operation) > 0 and hours_of_operation[-1] == ";":
            hours_of_operation = "".join(hours_of_operation[:-1]).strip()
        latitude = ""
        try:
            latitude = (
                store_req.text.split("google.maps.LatLng(")[1]
                .strip()
                .split(",")[0]
                .strip()
            )
        except:
            pass
        longitude = ""
        try:
            longitude = (
                store_req.text.split("google.maps.LatLng(")[1]
                .strip()
                .split(",")[1]
                .strip()
                .split(")")[0]
                .strip()
            )
        except:
            pass

        if len(latitude) <= 0:
            map_link = "".join(
                store_sel.xpath(
                    '//div[@class="page-masthead-body"]//a[contains(text(),"Get Directions")]/@href'
                )
            ).strip()

            if len(map_link) > 0:
                latitude = map_link.split("/@")[1].strip().split(",")[0].strip()
                longitude = map_link.split("/@")[1].strip().split(",")[1].strip()

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

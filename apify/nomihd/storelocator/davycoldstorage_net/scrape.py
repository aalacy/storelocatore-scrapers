# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "davycoldstorage.net"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://davycoldstorage.net/contact-us/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath(
        "//section[contains(@class,'elementor-section elementor-inner-section')]//p[@class='elementor-heading-title elementor-size-default']"
    )
    maps = stores_sel.xpath(
        '//div[@class="textwidget custom-html-widget"]/iframe[contains(@src,"maps/embed?")]/@src'
    )
    index = 0
    for store in stores:
        if len("".join(store.xpath("text()")).strip()) > 0 and (
            "".join(store.xpath("text()")).strip()[0].isalpha()
            or "".join(store.xpath("text()")).strip()[0].isdigit()
        ):
            if "P:" in "".join(store.xpath("text()")).strip():
                continue
            page_url = search_url
            location_name = "DAVY COLD STORAGE"
            location_type = "<MISSING>"
            locator_domain = website

            raw_info = store.xpath("text()")
            street_address = raw_info[0].strip()

            city = raw_info[1].strip().split(",")[0].strip()
            state = raw_info[1].strip().split(",")[1].strip().split(" ", 1)[0].strip()
            zipp = raw_info[1].strip().split(",")[1].strip().split(" ", 1)[-1].strip()
            phone = stores_sel.xpath('//a[contains(@href,"Tel:")]/text()')
            if len(phone) > 0:
                phone = phone[0].strip()

            hours = stores_sel.xpath('//table[contains(@id,"uael-table-id-")]//tr')
            hours_list = []
            for hour in hours:
                day = "".join(hour.xpath("td[1]//text()")).strip()
                time = "".join(hour.xpath("td[2]//text()")).strip()
                hours_list.append(day + ":" + time)

            hours_of_operation = "; ".join(hours_list).strip()
            country_code = "US"
            store_number = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            map_link = maps[index]
            if "!3d" and "!2d" in map_link:
                latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
                longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
            index = index + 1

            yield SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zipp,
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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

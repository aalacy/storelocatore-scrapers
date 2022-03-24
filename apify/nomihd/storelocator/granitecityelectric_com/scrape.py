# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import us

website = "granitecityelectric.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests(dont_retry_status_codes=([404]))
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.granitecityelectric.com/locations-showrooms"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//ul[@class="locationList"]/li/a')
    for store in stores:
        page_url = (
            "https://www.granitecityelectric.com/"
            + "".join(store.xpath("@href")).strip()
        )
        log.info(page_url)
        locator_domain = website

        store_req = session.get(page_url, headers=headers)

        if "location is permanently closed" in store_req.text:
            continue
        store_sel = lxml.html.fromstring(store_req.text)
        location_name = "".join(store.xpath("text()")).strip()
        address = store_sel.xpath('//div[@class="storeInfoLeft"]/p/text()')
        if len(address) <= 0:
            address = store_sel.xpath('//div[@class="storeInfoLeft"]/h3/text()')

        add_list = []
        hours_of_operation = ""

        for add in address:
            if len("".join(add).strip()) > 0:
                if "STORE" not in "".join(add).strip():
                    add_list.append("".join(add).strip())
        if len(add_list) > 0:
            street_address = add_list[0]
            city = add_list[1].split(",")[0].strip()
            state = add_list[1].split(",")[1].strip().split(" ")[0].strip()
            zip = add_list[1].split(",")[1].strip().split(" ")[1].strip()
        else:
            temp_address = store_sel.xpath('//div[@class="main-content"]/text()')
            add_list = []
            for temp in temp_address:
                if len("".join(temp).strip()) > 0:
                    add_list.append("".join(temp).strip())

            if len(add_list) > 0:
                street_address = add_list[0]
                city = add_list[1].split(",")[0].strip()
                state = add_list[1].split(",")[1].strip().split(" ")[0].strip()
                zip = add_list[1].split(",")[1].strip().split(" ")[1].strip()
                hours_of_operation = "; ".join(add_list[-2:])
            else:
                log.info("SKIP !!!!!")
                continue
        country_code = "<MISSING>"
        if us.states.lookup(state):
            country_code = "US"

        store_number = (
            "".join(store_sel.xpath('//*[contains(text(),"STORE ID:")]/text()'))
            .strip()
            .replace("STORE ID:", "")
            .strip()
        )
        raw_text = store_sel.xpath(
            '//div[@class="storeInfoLeft"]/div[@class="storeInfo"]/p'
        )
        phone = ""
        hours = []
        for temp_text in raw_text:
            if "Phone" in "".join(temp_text.xpath("text()")).strip():
                if len(phone) <= 0:
                    phone = temp_text.xpath("a//text()")
                    if len(phone) <= 0:
                        phone = temp_text.xpath("text()")
                        if len(phone) > 0:
                            phone = phone[0]
                            if "(" in phone:
                                phone = phone.split("(")[0].strip()
                    else:
                        phone = phone[0].strip()

            if "Monday" in "".join(temp_text.xpath("text()")).strip():
                if len(hours_of_operation) <= 0:
                    hours = temp_text.xpath("text()")
                    hours_list = []
                    for hour in hours:
                        if len("".join(hour).strip()) > 0 and "Hours" not in hour:
                            hours_list.append("".join(hour).strip())

                    hours_of_operation = (
                        "; ".join(hours_list)
                        .strip()
                        .encode("ascii", "replace")
                        .decode("utf-8")
                        .replace("?", "-")
                        .strip()
                        .replace("Hours", "")
                        .strip()
                    )

        if len(phone) <= 0:
            phone = "".join(
                store_sel.xpath(
                    '//div[@class="main-content"]/a[contains(@href,"tel:")]/text()'
                )
            ).strip()

        location_type = "<MISSING>"
        map_link = "".join(
            store_sel.xpath('//iframe[contains(@src,"maps/embed?")]/@src')
        ).strip()
        latitude = ""
        longitude = ""
        if len(map_link) > 0:
            latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
            longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()

        if hours_of_operation:
            hours_of_operation = (
                hours_of_operation.split("; GCE")[0]
                .strip()
                .split("; 24/7 EZ Pick UP")[0]
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

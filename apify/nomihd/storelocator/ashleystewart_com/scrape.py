# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import us
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "ashleystewart.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.ashleystewart.com/stores/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="store-information-div"]')
    for store in stores:
        page_url = (
            "https://www.ashleystewart.com"
            + "".join(store.xpath('div[@class="store-detail"]/a/@href')).strip()
        )

        locator_domain = website
        location_name = "".join(
            store.xpath('div[@class="store-name"]/a/text()')
        ).strip()

        address = store.xpath('div[@class="store-address"]/text()')
        add_list = []
        for add in address:
            if len("".join(add).strip()) > 0:
                add_list.append("".join(add).strip())

        if len(add_list) > 1:
            street_address = add_list[0].strip()
            city = add_list[1].strip().split(",")[0].strip()
            state = " ".join(
                " ".join(add_list[1].split("\n"))
                .strip()
                .split(",")[1]
                .strip()
                .rsplit(" ", 1)[0:-1]
            ).strip()
            zip = (
                " ".join(add_list[1].split("\n"))
                .strip()
                .split(",")[1]
                .strip()
                .rsplit(" ", 1)[-1]
                .strip()
            )
        else:
            street_address = "<MISSING>"
            city = "<MISSING>"
            state = add_list[0]
            zip = "<MISSING>"

        country_code = "<MISSING>"
        if us.states.lookup(state):
            country_code = "US"

        store_number = page_url.split("?StoreID=")[1].strip().split("-")[0].strip()
        phone = "".join(store.xpath('.//div[@class="store-phone"]/text()')).strip()

        location_type = "".join(
            store.xpath('div[@class="store-hours"]/p/strong/span/text()')
        ).strip()
        hours = store.xpath('div[@class="store-hours"]/p/text()')
        hours_list = []
        if "TEMPORARILY CLOSED" not in location_type:

            for hour in hours:
                if len("".join(hour).strip()) > 0:
                    hours_list.append("".join(hour).strip())
                else:
                    break

        hours_of_operation = "; ".join(hours_list).strip()

        latitude = "<MISSING>"
        longitude = "<MISSING>"

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

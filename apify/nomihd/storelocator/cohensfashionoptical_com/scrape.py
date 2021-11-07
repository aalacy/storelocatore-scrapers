# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import us
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "cohensfashionoptical.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.cohensfashionoptical.com/all-locations/"
    with SgRequests() as session:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath('//div[@class="fs-all-block"]')
        for store in stores:
            page_url = "".join(
                store.xpath('.//div[@class="fs-loc"]/h5/a/@href')
            ).strip()
            locator_domain = website
            location_name = (
                "".join(store.xpath('.//div[@class="fs-loc"]/h5/a/text()'))
                .strip()
                .encode("ascii", "replace")
                .decode("utf-8")
                .replace("?", "-")
                .strip()
            )

            street_address = (
                "".join(
                    store.xpath('.//div[@class="address"]/span[@class="street"]/text()')
                )
                .strip()
                .replace("Cross County Center,", "")
                .strip()
            )

            city_state_zip = "".join(
                store.xpath('.//div[@class="address"]/span[@class="city_zip"]/text()')
            ).strip()

            city = city_state_zip.split(",")[0].strip()
            zip = city_state_zip.split(",")[1].strip().rsplit(" ", 1)[-1].strip()
            state = city_state_zip.split(",")[1].strip().replace(zip, "").strip()

            if len(street_address) <= 0:
                store_req = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_req.text)
                raw_address = (
                    "".join(store_sel.xpath('//div[@class="loc_address"]//text()'))
                    .strip()
                    .split("\n")
                )
                street_address = raw_address[0].strip()
                city = raw_address[-1].strip().split(",")[0].strip()
                state = (
                    raw_address[-1].strip().split(",")[-1].strip().split(" ")[0].strip()
                )
                zip = (
                    raw_address[-1]
                    .strip()
                    .split(",")[-1]
                    .strip()
                    .split(" ")[-1]
                    .strip()
                )
            country_code = "<MISSING>"
            if us.states.lookup(state):
                country_code = "US"

            store_number = "<MISSING>"
            phone = (
                "".join(store.xpath('.//div[@class="phone desktop"]/text()'))
                .strip()
                .replace("Call", "")
                .strip()
            )

            location_type = "OPEN"
            if (
                "Closed"
                in "".join(
                    store.xpath('.//div[@class="loc-link"]/a/button/text()')
                ).strip()
            ):
                location_type = "CLOSED"

            hours = store.xpath(
                './/div[contains(@class,"fs-store-hour")]/div[@class="day-hours-wrapper clearfix"]'
            )
            hours_list = []
            for hour in hours:
                day = "".join(hour.xpath('div[@class="display-days"]/text()')).strip()
                time = "".join(hour.xpath('div[@class="display-hours"]/text()')).strip()
                hours_list.append(day + ": " + time)

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
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.ZIP,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

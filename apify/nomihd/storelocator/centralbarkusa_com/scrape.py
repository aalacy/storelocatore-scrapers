# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "centralbarkusa.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.centralbarkusa.com/fetch-a-location/"
    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)

    stores_list = search_sel.xpath('//div[@class="location"]')

    for store in stores_list:

        page_url = "".join(store.xpath('.//h2[@class="name-line"]/a/@href')).strip()
        locator_domain = website
        location_name = "".join(
            store.xpath('.//h2[@class="name-line"]/a/text()')
        ).strip()

        raw_address = " ".join(
            store.xpath('.//p[@class="address-line"]/span/text()')
        ).strip()

        formatted_addr = parser.parse_address_intl(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        state = formatted_addr.state
        zip = formatted_addr.postcode

        country_code = "US"

        store_number = "<MISSING>"

        phone = "".join(store.xpath('.//p[@class="phone-line"]/a/text()')).strip()

        location_type = "<MISSING>"

        if website in page_url:
            log.info(page_url)
            store_page_res = session.get(page_url, headers=headers)
            store_page_sel = lxml.html.fromstring(store_page_res.text)

            if (
                len(
                    "".join(
                        store_page_sel.xpath('//span[@class="coming-soon"]/text()')
                    ).strip()
                )
                > 0
            ):
                continue
            hours = store_page_sel.xpath('//div[@class="location-hours"]/p')
            hours_list = []
            for hour in hours:
                day = "".join(hour.xpath("span[1]/text()")).strip()
                time = (
                    "".join(hour.xpath("span[2]/text()")).strip().split("(")[0].strip()
                )
                if len(day) > 0 and len(time) > 0:
                    hours_list.append(day + ":" + time)

            hours_of_operation = (
                "; ".join(hours_list)
                .strip()
                .split("Sleepovers ")[0]
                .strip()
                .split("for Stay-n-Play")[0]
                .strip()
            )
            lat_lng = (
                store_page_res.text.split("var myLatLng = { ")[1].split("};")[0].strip()
            )

            latitude = lat_lng.split(",")[0].replace("lat:", "").strip()
            longitude = lat_lng.split(",")[1].replace("lng:", "").strip()
        else:
            page_url = search_url
            hours_of_operation = "<MISSING>"
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
            raw_address=raw_address,
        )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
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

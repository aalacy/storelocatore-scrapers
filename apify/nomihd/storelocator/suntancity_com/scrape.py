# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "suntancity.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.suntancity.com/find-a-salon"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//a[@class="city-link"]/@href')
    for store_url in stores:
        locator_domain = website
        page_url = "https://www.suntancity.com" + store_url
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        if len("".join(store_sel.xpath('//h1[@class="h3"]/text()')).strip()) <= 0:
            sub_stores = store_sel.xpath(
                '//div[@class="stc-content-line-content "]//a[contains(text(),"Details & Pricing")]/@href'
            )
            for sub in sub_stores:
                page_url = "https://www.suntancity.com" + sub
                log.info(page_url)
                store_req = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_req.text)
                if (
                    len("".join(store_sel.xpath('//h1[@class="h3"]/text()')).strip())
                    > 0
                ):

                    location_name = "".join(
                        store_sel.xpath('//h1[@class="h3"]/text()')
                    ).strip()
                    address = "".join(
                        store_sel.xpath('//div[@class="salon-address"]/text()')
                    ).strip()

                    street_address = ", ".join(address.split(",")[:-2]).strip()
                    city = address.rsplit(",")[-2].strip()
                    state = address.rsplit(",")[-1].strip().split(" ")[0].strip()
                    zip = address.rsplit(",")[-1].strip().split(" ")[-1].strip()

                    if zip.isdigit() is False:
                        zip = "<MISSING>"

                    country_code = "US"

                    store_number = "<MISSING>"
                    phone = "".join(
                        store_sel.xpath('//div[@class="salon-phonenumber"]/a/text()')
                    ).strip()
                    location_type = "<MISSING>"
                    latitude = "<MISSING>"
                    longitude = "<MISSING>"

                    hours_of_operation = "; ".join(
                        store_sel.xpath(
                            '//div[@class="salon-hours font-body1"]/div/text()'
                        )
                    ).strip()

                    if phone == "":
                        phone = "<MISSING>"

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
        else:
            location_name = "".join(store_sel.xpath('//h1[@class="h3"]/text()')).strip()
            address = "".join(
                store_sel.xpath('//div[@class="salon-address"]/text()')
            ).strip()

            street_address = ", ".join(address.split(",")[:-2]).strip()
            city = address.rsplit(",")[-2].strip()
            state = address.rsplit(",")[-1].strip().split(" ")[0].strip()
            zip = address.rsplit(",")[-1].strip().split(" ")[-1].strip()

            if zip.isdigit() is False:
                zip = "<MISSING>"

            country_code = "US"
            store_number = "<MISSING>"
            phone = "".join(
                store_sel.xpath('//div[@class="salon-phonenumber"]/a/text()')
            ).strip()
            location_type = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"

            hours_of_operation = "; ".join(
                store_sel.xpath('//div[@class="salon-hours font-body1"]/div/text()')
            ).strip()

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

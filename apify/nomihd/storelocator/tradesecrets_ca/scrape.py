# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "tradesecrets.ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    search_url = "https://info.tradesecrets.ca/"
    with SgRequests() as session:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(
            stores_req.text.split("Glamour Secrets Locations")[0].strip()
        )
        stores = stores_sel.xpath(
            '//div[contains(@class,"fusion-text fusion-text-")]/p/a/@href'
        )
        for store_url in stores:
            page_url = store_url
            locator_domain = website
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)

            location_name = (
                "".join(
                    store_sel.xpath('//div[@class="fusion-text fusion-text-1"]//text()')
                )
                .strip()
                .replace("Welcome to", "")
                .strip()
            )

            address = "".join(
                store_sel.xpath(
                    '//div[@class="fusion-text fusion-text-2"]/h4[1]//text()'
                )
            ).strip()
            if len(address) <= 0:
                address = "".join(
                    store_sel.xpath(
                        '//div[@class="fusion-text fusion-text-2"]/h3[1]//text()'
                    )
                ).strip()
            phone = "".join(
                store_sel.xpath(
                    '//div[@class="fusion-text fusion-text-2"]//h4[2]//text()'
                )
            ).strip()
            if len(phone) <= 0:
                phone = "".join(
                    store_sel.xpath(
                        '//div[@class="fusion-text fusion-text-2"]//h3[2]//text()'
                    )
                ).strip()
            if len(phone) <= 0:
                address = "".join(
                    store_sel.xpath(
                        '//div[@class="fusion-text fusion-text-2"]/h4[1]//text()'
                    )
                ).strip()
                if "|" in address:
                    phone = address.split("|")[-1].strip()
                    address = address.split("|")[0].strip()

            if "or" in phone:
                phone = phone.split("or")[0].strip()

            if len(phone) <= 0:
                phone = "".join(
                    store_sel.xpath(
                        '//div[@class="fusion-text fusion-text-2"]/div/div/h4//text()'
                    )
                ).strip()
            formatted_addr = parser.parse_address_intl(address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode
            if "75 Centennial Parkway North On" == street_address:
                street_address = "75 Centennial Parkway North"
                state = "ON"

            country_code = "CA"

            if zip is None:
                try:
                    address = (
                        store_req.text.split('addresses: [{"address":"')[1]
                        .strip()
                        .split('",')[0]
                        .strip()
                    )
                    formatted_addr = parser.parse_address_intl(address)
                    zip = formatted_addr.postcode
                except:
                    pass

            store_number = "<MISSING>"
            location_type = "<MISSING>"

            hours_of_operation = (
                "; ".join(
                    store_sel.xpath(
                        '//div[@class="fusion-text fusion-text-3"]/h4/text()'
                    )
                )
                .encode("ascii", "replace")
                .decode("utf-8")
                .replace("?", "-")
                .strip()
            )

            if "We are OPEN." in hours_of_operation:
                hours_of_operation = (
                    "; ".join(
                        store_sel.xpath(
                            '//div[@class="fusion-text fusion-text-3"]/p/strong/text()'
                        )
                    )
                    .encode("ascii", "replace")
                    .decode("utf-8")
                    .replace("?", "")
                    .strip()
                    .replace("Operating Hours", "")
                    .strip()
                )
            latitude = "<MISSING>"
            try:
                latitude = (
                    store_req.text.split('"latitude":"')[1]
                    .strip()
                    .split('",')[0]
                    .strip()
                )
            except:
                pass
            longitude = "<MISSING>"
            try:
                longitude = (
                    store_req.text.split('"longitude":"')[1]
                    .strip()
                    .split('"')[0]
                    .strip()
                )
            except:
                pass

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
                raw_address=address,
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

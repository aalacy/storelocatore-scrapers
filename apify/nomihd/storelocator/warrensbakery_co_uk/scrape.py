# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "warrensbakery.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "warrensbakery.co.uk",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://warrensbakery.co.uk/find-our-stores/"
    with SgRequests(dont_retry_status_codes=([404])) as session:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath('//div[@class="marker"]')

        for store in stores:
            page_url = "".join(
                store.xpath('.//a[contains(text(),"Visit Store")]/@href')
            ).strip()
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)
            locator_domain = website
            location_name = "".join(store_sel.xpath("//div/h1/text()")).strip()
            store_info = store_sel.xpath("//address/text()")
            add_list = []
            for st in store_info:
                if len("".join(st).strip()) > 0:
                    add_list.append("".join(st).strip())

            zip = "<MISSING>"
            phone = "<MISSING>"
            raw_address = ""
            if (
                add_list[-1]
                .replace("Tel:", "")
                .strip()
                .replace("Tel.", "")
                .strip()
                .replace(" ", "")
                .strip()
                .replace("O", "0")
                .strip()
                .isdigit()
            ):
                phone = (
                    add_list[-1]
                    .replace("Tel:", "")
                    .strip()
                    .replace("Tel.", "")
                    .strip()
                    .replace(" ", "")
                    .strip()
                    .replace("O", "0")
                    .strip()
                )
                zip = add_list[-2].strip()
                raw_address = ", ".join(add_list[:-1]).strip()
            else:
                phone = "<MISSING>"
                zip = add_list[-1]
                raw_address = ", ".join(add_list).strip()

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city
            if street_address:
                street_address = street_address.replace(
                    "Market Square St Just Penzance Tr19 7Hd", "Market Square St Just"
                )
                if city is None:
                    city = "Penzance"

            state = formatted_addr.state

            country_code = "GB"

            store_number = "<MISSING>"
            location_type = "<MISSING>"
            hours_of_operation = (
                "; ".join(
                    store_sel.xpath(
                        '//div[@class="markup"]/p[contains(.//text(),"Opening Hours") or contains(.//text(),"Opening Times")]/following-sibling::p//text()'
                    )
                )
                .strip()
                .replace("\n", "")
                .strip()
                .split("; Boxing Day")[0]
                .strip()
                .split("; Christmas Day")[0]
                .strip()
                .split("18th")[0]
                .strip()
                .split("23/12/18")[0]
                .strip()
                .replace("; ;", ";")
                .strip()
            )

            latitude = "".join(store.xpath("@data-lat")).strip()
            longitude = "".join(store.xpath("@data-lng")).strip()

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

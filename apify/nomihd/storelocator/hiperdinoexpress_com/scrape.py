# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser

website = "hiperdinoexpress.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "hiperdinoexpress.com",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://hiperdinoexpress.com/en/island-stores?isla=All"
    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)
        search_sel = lxml.html.fromstring(search_res.text)
        stores = search_sel.xpath(
            '//div[@class="views-view-grid horizontal cols-3 clearfix"]/div[contains(@class,"views-row clearfix")]/div'
        )
        for store in stores:

            page_url = search_url
            locator_domain = website

            location_name = "".join(store.xpath("div[1]/h2/text()")).strip()

            raw_address = ", ".join(
                list(
                    filter(
                        str,
                        [
                            x.strip()
                            for x in store.xpath('.//div[@class="direccion"]//text()')
                        ],
                    )
                )
            ).strip()

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if street_address:
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )
            else:
                if formatted_addr.street_address_2:
                    street_address = formatted_addr.street_address_2

            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode

            country_code = "ES"

            store_number = "<MISSING>"

            phone = store.xpath('.//div[@class="telefono"]//text()')
            if len(phone) > 0:
                phone = phone[0]
            else:
                phone = "<MISSING>"

            location_type = "<MISSING>"

            hours_of_operation = "; ".join(
                store.xpath('.//div[@class="horario"]/ul/li/text()')
            ).strip()

            latitude, longitude = (
                "".join(store.xpath('.//meta[@property="latitude"]/@content')).strip(),
                "".join(store.xpath('.//meta[@property="longitude"]/@content')).strip(),
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
                raw_address=raw_address,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

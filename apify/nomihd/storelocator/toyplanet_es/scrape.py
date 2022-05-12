# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html

website = "toyplanet.es"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "www.toyplanet.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.toyplanet.com/es/ver-todas-tiendas.html"
    with SgRequests() as session:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        sections = stores_sel.xpath(
            '//div[@class="row"][./div[@class="card-body col-md-6 col-lg-4"]]'
        )
        for section in sections:
            stores = section.xpath('div[@class="card-body col-md-6 col-lg-4"]')
            for store in stores:
                city = "".join(
                    section.xpath("./preceding-sibling::div[.//h3][1]//h3//text()")
                ).strip()
                state = "".join(
                    section.xpath("./preceding-sibling::div[.//h2][1]//h2//text()")
                ).strip()
                store_number = "".join(store.xpath("@id")).strip()
                page_url = search_url
                locator_domain = website
                location_name = "".join(
                    store.xpath('.//span[@class="form-check-label"]/text()')
                ).strip()

                raw_address = (
                    "".join(
                        list(
                            filter(
                                str,
                                [
                                    x.strip()
                                    for x in store.xpath(
                                        './/div[@class="store-address"]/text()'
                                    )
                                ],
                            )
                        )
                    )
                    .strip()
                    .replace("\n", "")
                    .strip()
                    .replace("\r", "")
                    .replace("\t", "")
                    .strip()
                )
                street_address = raw_address.rsplit(" ", 1)[0].strip()
                zip = raw_address.rsplit(" ", 1)[-1].strip()
                country_code = "ES"
                raw_address = street_address + " " + zip
                phone = store.xpath('.//a[@class="storelocator-phone"]/text()')
                if len(phone) > 0:
                    phone = "".join(phone[0]).strip().replace("+", "").strip()
                else:
                    phone = "<MISSING>"
                location_type = "<MISSING>"

                hours_of_operation = (
                    "".join(
                        store.xpath(
                            './/div[@class="store-hours"]//p[@class="hours-container"]/text()'
                        )
                    )
                    .strip()
                    .replace("\n", ";")
                    .strip()
                    .split("FESTIVOS")[0]
                    .strip()
                )

                latitude, longitude = "<MISSING>", "<MISSING>"

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
                    SgRecord.Headers.RAW_ADDRESS,
                    SgRecord.Headers.LOCATION_NAME,
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

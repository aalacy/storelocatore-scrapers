# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "moss.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    base = "https://www.moss.co.uk"
    search_url = "https://www.moss.co.uk/storefinder"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)
        stores = search_sel.xpath('//div[contains(@class,"listStore ")]')

        for no, store in enumerate(stores, 1):

            locator_domain = website

            location_name = location_name = "".join(
                store.xpath(
                    './/div[@class="storeAddress"]//span[@itemprop="name"]//text()'
                )
            ).strip()

            location_type = "".join(
                store.xpath('.//div[@class="stores-closed-covid"]//text()')
            ).strip()
            page_url = base + "".join(
                store.xpath(
                    './/div[@class="storeAddress"]//a[contains(@href,"/store/")]/@href'
                )
            )

            raw_address = "<MISSING>"

            street_address = (
                " ".join(
                    list(
                        filter(
                            str,
                            [
                                x.strip()
                                for x in store.xpath(
                                    './/div[@class="storeAddress"]//span[@itemprop="streetAddress"]//text()'
                                )
                            ],
                        )
                    )
                )
                .strip()
                .replace(",,", ",")
                .replace(" ,", ",")
                .strip(", ")
            )

            city = "".join(
                store.xpath(
                    './/div[@class="storeAddress"]//span[@itemprop="addressLocality"]//text()'
                )
            ).strip()
            if len(street_address) <= 0 and len(city) <= 0:
                continue
            state = "".join(
                store.xpath(
                    './/div[@class="storeAddress"]//span[@itemprop="addressRegion"]//text()'
                )
            ).strip()

            zip = "".join(
                store.xpath(
                    './/div[@class="storeAddress"]//span[@itemprop="postalCode"]//text()'
                )
            ).strip()

            country_code = "GB"

            phone = "".join(
                store.xpath(
                    './/div[@class="storeAddress"]//a[@itemprop="telephone"]//text()'
                )
            ).strip()

            hours = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store.xpath('.//span[@class="storeOpening"]//text()')
                    ],
                )
            )
            hours_of_operation = (
                "; ".join(hours)
                .replace("day;", "day:")
                .replace("day ", "day:")
                .replace("Fri;", "Fri:")
                .replace("Sat;", "Sat:")
                .replace("Sun;", "Sun:")
                .replace("Thurs;", "Thurs:")
                .replace("<br />", "; ")
                .strip()
                .replace("Please contact the store for more details", "")
                .strip()
            )

            store_number = "".join(store.xpath('.//span[@class="storeNumber"]//text()'))

            latitude, longitude = "".join(store.xpath("./@data-latitude")), "".join(
                store.xpath("./@data-longitude")
            )
            if latitude == "0":
                latitude = "<MISSING>"
            if longitude == "0":
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

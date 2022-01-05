# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "national.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.national.co.uk/branches"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)
        stores = search_sel.xpath('//form[@id="branchsearch"]//select/option')
        for store in stores:

            locator_domain = website

            location_name = "".join(store.xpath(".//text()")).strip()

            page_url = (
                search_url.replace("branches", "branch")
                + "/"
                + "".join(store.xpath("./@value"))
                + "/"
            )

            log.info(page_url)
            store_res = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_res.text)
            location_type = "<MISSING>"

            raw_address = (
                " ".join(
                    list(
                        filter(
                            str,
                            [
                                x.strip()
                                for x in store_sel.xpath(
                                    '//span[@itemprop="streetAddress"]//text()'
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

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                if street_address:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )
                else:
                    street_address = formatted_addr.street_address_2

            if street_address is not None:
                street_address = street_address.replace("Ste", "Suite")

            if street_address and street_address.isdigit():
                street_address = raw_address.split(",")[0].strip()

            city = formatted_addr.city
            if not city:
                city = location_name
            state = formatted_addr.state

            zip = "".join(
                store_sel.xpath('//span[@itemprop="postalCode"]//text()')
            ).strip()

            country_code = "".join(
                store_sel.xpath('//span[@itemprop="addressCountry"]//text()')
            ).strip()
            if country_code == "UK":
                country_code = "GB"
            phone = "".join(
                store_sel.xpath('//span[@itemprop="telephone"]//text()')
            ).strip()

            hours = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            '//*[@itemprop="openingHours"]/@content'
                        )
                    ],
                )
            )
            hours_of_operation = (
                "; ".join(hours)
                .replace("day;", "day:")
                .replace("Fri;", "Fri:")
                .replace("Sat;", "Sat:")
                .replace("Sun;", "Sun:")
                .replace("Thurs;", "Thurs:")
            )

            store_number = (
                page_url.replace(search_url.replace("branches", "branch"), "")
                .split("/")[1]
                .strip()
            )

            latitude, longitude = "".join(
                store_sel.xpath(
                    '//div[@itemprop="geo"]/div[@itemprop="geo"]//meta[@itemprop="latitude"]/@content'
                )
            ), "".join(
                store_sel.xpath(
                    '//div[@itemprop="geo"]/div[@itemprop="geo"]//meta[@itemprop="longitude"]/@content'
                )
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

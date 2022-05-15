# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import us
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "vinovolo.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://vinovolo.com/locations/"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)

        stores = search_sel.xpath(
            '//nav[not(@style) and not(@migrated)]/ul//a[contains(@href,"locations-")]'
        )

        for no, store in enumerate(stores, 1):

            locator_domain = website

            page_url = "".join(store.xpath("./@href"))
            log.info(page_url)

            store_res = session.get(page_url, headers=headers)

            store_sel = lxml.html.fromstring(store_res.text)

            locations = store_sel.xpath(
                '//div[@class="elementor-widget-wrap elementor-element-populated" and .//h2[not(contains(text(),"Locations"))]]/div[.//p]'
            )
            city_state = "".join(
                store_sel.xpath(
                    '//div[@class="elementor-widget-wrap elementor-element-populated" and .//h2[not(contains(text(),"Locations"))]]/div[.//h2]//h2//text()'
                )
            ).strip()
            for location in locations:

                location_name = "".join(location.xpath(".//p//text()")).strip()
                location_type = "<MISSING>"

                location_info_sel = location.xpath(
                    "./following-sibling::section[.//p][1]//div[p]"
                )

                raw_address = (
                    location_name.replace("– NOW OPEN!", "") + " " + city_state
                )

                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                if street_address is not None:
                    street_address = street_address.replace("Ste", "Suite")
                city = formatted_addr.city
                if not city:
                    if "," in city_state:
                        city = city_state.split(",")[0].strip()
                    else:
                        city = city_state.split("/")[1].strip()

                state = formatted_addr.state
                if not state:
                    if "," in city_state:
                        state = city_state.split(",")[1].strip()
                    else:
                        state = city_state.split("/")[0].strip()
                zip = formatted_addr.postcode
                if us.states.lookup(state):
                    country_code = "US"
                else:
                    country_code = "CA"
                if city == "Washington":
                    country_code = "CA"

                store_number = "<MISSING>"
                phone = (
                    "".join(location_info_sel[1].xpath("./p[1]//text()"))
                    .replace("Phone:", "")
                    .strip()
                )
                if (
                    not phone.replace("(", "")
                    .replace(")", "")
                    .replace("-", "")
                    .replace(" ", "")
                    .strip()
                    .isdigit()
                ):
                    phone = "<MISSING>"
                hours = list(
                    filter(
                        str,
                        [x.strip() for x in location_info_sel[0].xpath("./p//text()")],
                    )
                )

                hours_of_operation = (
                    "; ".join(hours[1:])
                    .replace("day;", "day:")
                    .replace("b;", "b:")
                    .replace("Dia:; ", "")
                    .replace("Hora:; ", "")
                    .strip()
                )
                if "Temporarily Closed" in hours_of_operation:
                    location_type = "Temporarily Closed"

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

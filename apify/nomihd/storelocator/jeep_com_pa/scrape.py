# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "jeep.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    for search_url in [
        "https://www.jeep.com.pa/concesionarios/",
        "https://www.jeep.com.co/concesionarios/",
    ]:

        with SgRequests() as session:
            search_res = session.get(search_url, headers=headers)

            search_sel = lxml.html.fromstring(search_res.text)

            stores = search_sel.xpath("//h1/following-sibling::h3")

            for no, store in enumerate(stores, 1):

                locator_domain = website

                page_url = search_url

                store_info = list(
                    filter(
                        str,
                        [
                            x.strip()
                            for x in search_sel.xpath(
                                f"//h1//following-sibling::*[count(following-sibling::h3)={no-1}][self::p or self::h3]//text()"
                            )
                        ],
                    )
                )

                location_name = store_info[0]
                location_type = "<MISSING>"

                raw_address = store_info[1].strip()

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
                    city = "".join(
                        search_sel.xpath(
                            f"//h1//following-sibling::h3[count(following-sibling::h3)={no-1}]/preceding-sibling::h2[1]//text()"
                        )
                    ).strip()

                state = formatted_addr.state
                zip = formatted_addr.postcode

                country_code = (
                    search_url.replace("https://www.jeep.com.", "")
                    .split("/")[0]
                    .upper()
                )

                store_number = "<MISSING>"

                phone = store_info[-1].lower()
                if "phone" in phone or "tel" in phone:
                    phone = phone.replace("phone:", "").replace("tel:", "").strip()
                else:
                    phone = "<MISSING>"

                hours_of_operation = "<MISSING>"

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

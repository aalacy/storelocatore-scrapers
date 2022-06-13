# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "britanniapharmacy.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.britanniapharmacy.com/branches/index.htm"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)

        area_list = search_sel.xpath('//table//a[contains(@href,".htm")]')

        for area in area_list:

            area_url = "https://www.britanniapharmacy.com/branches/" + "".join(
                area.xpath("./@href")
            )
            log.info(area_url)

            area_res = session.get(area_url, headers=headers)
            area_sel = lxml.html.fromstring(area_res.text)

            stores = area_sel.xpath('//table//tr[./td/a[contains(@href,".htm")]]')
            for no, store in enumerate(stores, 1):

                locator_domain = website
                store_number = "<MISSING>"

                page_url = "https://www.britanniapharmacy.com/branches/" + "".join(
                    store.xpath(".//a/@href")
                )

                if "index.htm" in page_url:
                    continue

                log.info(page_url)

                store_res = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_res.text)

                location_type = "<MISSING>"

                store_info = list(
                    filter(
                        str,
                        [x.strip() for x in store.xpath(".//p//text()")],
                    )
                )

                location_name = (
                    store_info[0].strip().strip(" ,").strip().replace("\n", "")
                )
                location_name = " ".join(
                    list(filter(str, [x.strip() for x in location_name.split(" ")]))
                )

                phone = (
                    store_info[-1]
                    .replace("Tel", "")
                    .replace("Fax", "")
                    .replace("/", "")
                    .replace(":", "")
                    .replace(".", "")
                    .strip()
                )

                raw_address = " ".join(store_info).strip().split("Tel")[0].strip()
                raw_address = " ".join(
                    list(filter(str, [x.strip() for x in raw_address.split(" ")]))
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
                if (
                    not city
                ):  # Hardcoded for two three locations as I am getting MISSING
                    city = "Barking"

                if city:
                    city = city.replace(".", "").strip()

                state = formatted_addr.state
                zip = formatted_addr.postcode
                if not zip:
                    zip = raw_address.split("Essex")[1].strip(" ,.")

                if zip:
                    zip = zip.replace(".", "").strip()
                country_code = "GB"

                hours = list(
                    filter(
                        str,
                        [
                            x.strip()
                            for x in store_sel.xpath(
                                '//table[./tr/td="Monday"]//text()'
                            )
                        ],
                    )
                )

                hours_of_operation = (
                    "; ".join(hours)
                    .replace("day; ", "day: ")
                    .replace("day:;", "day:")
                    .replace("OPEN FOR BUSINESS!", "")
                    .replace("NOW OPEN!", "")
                    .replace("; -;", " -")
                    .strip(";! ")
                )

                latitude, longitude = "<MISSING>", "<MISSING"

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

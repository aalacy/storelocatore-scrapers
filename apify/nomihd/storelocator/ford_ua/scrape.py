# -*- coding: utf-8 -*-
from sgrequests import SgRequests, SgRequestError
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
import lxml.html
import json
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "ford.ua"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_urls = [
        "https://ford.ua/dealerships",
        "https://ford.si/prodajno_servisna_mreza",
        "https://ford.md/dealerships",
        "https://ford.rs/dealerships",
        "https://ford.sk/dealerships",
        "https://www.ford.com.al/dealerships",
        "https://ford.am/dealerships",
        "https://ford.ba/dealerships",
        "https://www.ford.bg/dealerships",
        "https://fordcyprus.com/dealerships",
        "https://ford.com.ge/dealerships",
        "https://www.ford.lv/parstavji",
        "https://www.ford.lt/dealerships",
        "https://ford.mk/dealerships",
        "https://www.ford.com.mt/dealerships",
    ]

    with SgRequests() as session:

        for search_url in search_urls:
            log.info(search_url)

            search_res = session.get(search_url, headers=headers)
            if isinstance(search_res, SgRequestError):
                log.error(f"URL is not working: {search_url}")
                continue
            search_sel = lxml.html.fromstring(search_res.text)
            stores = search_sel.xpath("//div[h4]")
            locator_domain = website
            country_code = (
                search_url.split("//")[1]
                .split("/")[0]
                .replace("www", "")
                .replace(".", "")
                .replace("com", "")
                .replace("ford", "")
                .strip()
                .upper()
            )

            for no, store in enumerate(stores, 1):

                location_type = "".join(store.xpath("p/strong/text()")).strip()

                page_url = search_url

                location_name = "".join(store.xpath("./h4//text()")).strip()

                if not location_name:
                    continue

                if country_code == "RS" and "-" in location_name:
                    location_type = location_name.split("-")[-1].strip()
                store_info = list(
                    filter(
                        str,
                        [
                            x.strip()
                            for x in store.xpath(".//p[@class='address']//text()")
                        ],
                    )
                )
                raw_address = " ".join(store_info)

                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                if street_address is not None:
                    street_address = street_address.replace("Ste", "Suite")

                city = store.xpath("./preceding::h3//text()")[-1].strip()
                if len(city) <= 0:
                    city = formatted_addr.city

                state = formatted_addr.state
                zip = formatted_addr.postcode

                phone = (
                    "".join(store.xpath('./a[contains(@href,"tel:")]//text()'))
                    .replace("Call", "")
                    .strip()
                    .split(",")[0]
                    .strip()
                    .split("Mob.")[0]
                    .strip()
                    .replace("Tel.:", "")
                    .strip()
                    .split(";")[0]
                    .strip()
                    .split("&")[0]
                    .strip()
                    .replace("Phone Main:", "")
                    .strip()
                    .replace("Service:", "")
                    .strip()
                    .replace("Tel:", "")
                    .strip()
                )

                hours_str = "".join(store.xpath(".//p/@data-openings")).strip()
                if hours_str:
                    hours_json = json.loads(hours_str)

                    hour_list = []
                    for day, time in hours_json.items():
                        time = time.split("E-mail")[0]
                        hour_list.append(f"{day}: {time}")

                    hours_of_operation = "; ".join(hour_list)
                else:
                    hours_of_operation = "<MISSING>"

                store_number = "<MISSING>"

                latitude, longitude = (
                    "".join(store.xpath(".//button/@data-latitude")),
                    "".join(store.xpath(".//button/@data-longitude")),
                )

                if latitude == longitude:
                    latitude = longitude = "<MISSING>"
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
                    SgRecord.Headers.COUNTRY_CODE,
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

# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "mcdonaldsindia.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    base = "https://mcdonaldsindia.com"
    search_url = "https://mcdonaldsindia.com/convenience.html?v=6"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)
        search_sel = lxml.html.fromstring(search_res.text)

        states = search_sel.xpath(
            '//div[./div/p/text()="Locate Us"]//div[contains(@class,"india_mp")]/a'
        )
        for state in states:

            state_url = base + "/" + "".join(state.xpath("./@href"))
            log.info(state_url)
            state_res = session.get(state_url, headers=headers)
            state_sel = lxml.html.fromstring(state_res.text)

            stores = state_sel.xpath('//ul/li[@class="viewmap map_menu"]')

            for store in stores:

                page_url = state_url + "".join(store.xpath(".//text()")).strip()

                locator_domain = website

                location_name = "".join(store.xpath(".//text()")).strip()
                store_info_str = "".join(store.xpath("./@contain"))
                store_sel = lxml.html.fromstring(store_info_str)

                store_info = store_sel.xpath('//div[@class="addres_box"]//text()')

                raw_address = (
                    ", ".join(store_info[1:2])
                    .replace("\n", " ")
                    .strip()
                    .replace("\r", "")
                    .strip()
                    .split("Tel No")[0]
                    .strip()
                    .encode("ascii", "replace")
                    .decode("utf-8")
                    .replace("?", " - ")
                    .strip()
                )
                try:
                    temp_add = (
                        raw_address.rsplit("-", 1)[-1].strip().replace(" ", "").strip()
                    )
                    if temp_add.isdigit():
                        raw_address = (
                            raw_address.rsplit("-", 1)[0].strip() + ", " + temp_add
                        )
                except:
                    pass
                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                if street_address is not None:
                    street_address = street_address.replace("Ste", "Suite")
                city = formatted_addr.city
                state = state_url.split("state=")[-1].strip()
                zip = formatted_addr.postcode
                if zip:
                    zip = zip.split("-")[-1].strip()

                if not zip:
                    try:
                        temp_zip = (
                            raw_address.split(",")[-1].strip().replace(" ", "").strip()
                        )
                        if temp_zip.isdigit() and len(temp_zip) == 6:
                            zip = temp_zip
                    except:
                        pass

                if not zip:
                    try:
                        temp_zip = (
                            raw_address.split(" ")[-1]
                            .strip()
                            .replace(" ", "")
                            .strip()
                            .replace(".", "")
                            .strip()
                        )
                        if temp_zip.isdigit():
                            zip = temp_zip
                            if len(zip) == 3:
                                zip = raw_address.split(" ")[-2].strip() + zip
                                if len(zip) != 6:
                                    zip = "<MISSING>"
                            else:
                                zip = "<MISSING>"
                    except:
                        pass

                if city and "-413001" in city:
                    city = "<MISSING>"
                    zip = "413001"

                country_code = "IN"

                store_number = "<MISSING>"

                phone = "<MISSING>"

                location_type = "<MISSING>"

                hours_of_operation = "<MISSING>"

                latitude, longitude = (
                    "".join(store.xpath("./@lat")),
                    "".join(store.xpath("./@long")),
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

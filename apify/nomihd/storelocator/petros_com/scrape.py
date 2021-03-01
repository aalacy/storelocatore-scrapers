# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape import sgpostal as parser
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

website = "petros.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    loc_list = []

    search_url = "https://www.petros.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath(
        '//div[@class="entry"]/div[contains(@class,"one_fourth")]/p'
    )
    for store in stores:
        page_url = search_url
        if len(store.xpath("a/@href")) > 0:
            page_url = "".join(store.xpath("a/@href")).strip()

        location_type = "<MISSING>"
        location_name = "".join(store.xpath("strong/text()")).strip()

        locator_domain = website

        address = store.xpath("text()")
        add_list = []
        temp_hours = []
        for index in range(0, len(address)):
            if len("".join(address[index]).strip()) > 0:
                if (
                    "(" not in "".join(address[index]).strip()
                    and ")" not in "".join(address[index]).strip()
                ):
                    if "Mondays" in "".join(address[index]).strip():
                        temp_hours = address[index:]
                        break
                    else:
                        add_list.append("".join(address[index]).strip())

        print(add_list)
        raw_address = " ".join(add_list).strip()
        formatted_addr = parser.parse_address_usa(raw_address)
        street_address = formatted_addr.street_address_1
        if street_address and formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        if street_address:
            street_address = street_address.replace("Loves Travel Center", "").strip()

        city = formatted_addr.city
        state = formatted_addr.state
        zip = formatted_addr.postcode
        country_code = formatted_addr.country

        if len(location_name) <= 0:
            location_name = city

        phone = "".join(store.xpath("span/text()")).strip()

        if len(temp_hours) <= 0:
            temp_hours = store.xpath("em/text()")

        hours_list = []
        for hour in temp_hours:
            if (
                len("".join(hour).strip()) > 0
                and "Open on Game and Special Event Days" not in "".join(hour).strip()
            ):
                hours_list.append("; ".join("".join(hour).strip().split("\n")))

        hours_of_operation = (
            "; ".join(hours_list)
            .strip()
            .encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", "-")
            .strip()
        )
        store_number = "<MISSING>"

        latitude = "<MISSING>"
        longitude = "<MISSING>"

        if "coming" not in location_name.lower():
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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

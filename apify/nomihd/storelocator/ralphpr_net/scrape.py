# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape import sgpostal as parser


website = "ralphpr.net"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "ralphpr.net",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://ralphpr.net/localidades/"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    store_list = search_sel.xpath("//div[./h4]")

    for store in store_list:

        page_url = search_url

        locator_domain = website

        store_info = list(
            filter(
                str,
                [x.strip() for x in store.xpath(".//p//text()")],
            )
        )

        location_name = "".join(store.xpath("./h4/text()")).strip()

        store_info = " | ".join(store_info)

        raw_address = " ".join(store_info.split("Dirección:")[1:]).strip("| ").strip()

        formatted_addr = parser.parse_address_intl(raw_address)
        street_address = ", ".join(raw_address.split(",")[:-1]).strip()

        city = location_name.replace("Ralph's", "").strip()
        if city == "Del Este Humacao":
            city = "Humacao"

        try:
            street_address = street_address.rsplit(city, 1)[0].strip()
        except:
            pass

        if street_address[-1] == ",":
            street_address = "".join(street_address[:-1]).strip()

        state = formatted_addr.state
        zip = formatted_addr.postcode
        if not state:
            state = "Puerto Rico"

        country_code = "US"

        phone = (
            store_info.split("Dirección:")[0]
            .split("Horarios de atención:")[0]
            .split("Teléfono:")[1]
            .strip(" |")
            .strip()
        )

        store_number = "<MISSING>"

        location_type = "<MISSING>"
        hours = (
            store_info.split("Dirección:")[0]
            .split("Horarios de atención:")[1]
            .strip("| ")
            .split(" | ")
        )
        hours_of_operation = "; ".join(hours)

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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

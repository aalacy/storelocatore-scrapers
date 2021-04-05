# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape import sgpostal as parser
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as BS

website = "kookai.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "authority": "kookai.co.uk",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://kookai.co.uk/pages/boutique-locator"
    stores_req = session.get(search_url, headers=headers)
    stores = (
        stores_req.text.split("var locations = [")[1]
        .strip()
        .split("];")[0]
        .strip()
        .split("index:")
    )
    for index in range(1, len(stores)):
        page_url = search_url
        store_data = stores[index]
        location_type = "<MISSING>"
        location_name = (
            store_data.split("name:")[1]
            .strip()
            .split(",")[0]
            .strip()
            .replace('"', "")
            .strip()
        )

        locator_domain = website

        raw_address = BS(
            store_data.split("address:")[1]
            .strip()
            .split('",')[0]
            .strip()
            .replace('"', "")
            .strip()
            .replace("\\u003c", "<")
            .replace("\\u003e", ">")
            .replace("\\u0026nbsp;", " ")
            .replace("\\/", "/"),
            "lxml",
        ).get_text()

        formatted_addr = parser.parse_address_intl(raw_address)
        street_address = formatted_addr.street_address_1
        if formatted_addr.street_address_2:
            street_address = street_address + ", " + formatted_addr.street_address_2

        city = formatted_addr.city
        state = formatted_addr.state
        zip = formatted_addr.postcode
        country_code = formatted_addr.country

        phone = (
            store_data.split("phone:")[1]
            .strip()
            .split(",")[0]
            .strip()
            .replace('"', "")
            .strip()
        )

        temp_hours = (
            store_data.split("trading:")[1]
            .strip()
            .split(",")[0]
            .strip()
            .replace('"', "")
            .strip()
            .strip()
            .replace("\\u003c", "<")
            .replace("\\u003e", ">")
            .replace("\\u0026nbsp;", " ")
            .replace("\\/", "/")
            .strip()
        )

        hours_sel = lxml.html.fromstring(temp_hours)
        hours = hours_sel.xpath("//p")
        hours_list = []
        hours_of_operation = ""
        for hour in hours:
            temp_hours = hour.xpath("text()")
            for temp_text in temp_hours:
                if len("".join(temp_text).strip()) > 0:
                    if "Standard Trading Hours" in "".join(temp_text).strip():
                        continue
                    else:
                        hours_list.append("".join(temp_text).strip())

        hours_of_operation = "; ".join(hours_list).strip()

        store_number = "<MISSING>"

        latlng = store_data.split("position:")[1].strip().split("),")[0].strip()
        latitude = (
            latlng.split("[")[1].strip().split(",")[0].strip().replace('"', "").strip()
        )
        longitude = (
            latlng.split("[")[1]
            .strip()
            .split(",")[1]
            .strip()
            .split("]")[0]
            .strip()
            .replace('"', "")
            .strip()
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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

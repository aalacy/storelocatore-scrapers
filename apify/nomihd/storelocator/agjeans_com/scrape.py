# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

website = "agjeans.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.agjeans.com/locations.html"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)

    stores = stores_sel.xpath('//li[@id="store-info"]')
    for store in stores:
        page_url = search_url
        location_type = "<MISSING>"
        locator_domain = website

        raw_info = "".join(store.xpath("a/p/text()")).strip().split("\n")
        add_list = []
        for add in raw_info:
            if len("".join(add).strip()) > 0:
                add_list.append("".join(add).strip())

        location_name = add_list[0].strip()
        street_address = ", ".join(add_list[1:-1])
        city_state_zip = add_list[-1].strip()
        city = city_state_zip.split(",")[0].strip()
        state = city_state_zip.split(",")[1].strip().split(" ")[0].strip()
        zip = city_state_zip.split(",")[1].strip().split(" ")[1].strip()
        country_code = "US"

        temp_phone = store.xpath('p[contains(text(),"Phone:")]/text()')
        phone = ""
        if len(temp_phone) > 0:
            phone = temp_phone[0].strip().replace("Phone:", "").strip()

        hours_list = []
        hours = store.xpath('p[contains(text(),"STORE HOURS")]/text()')
        for hour in hours:
            if len("".join(hour).strip()) > 0:
                if "STORE HOURS" not in "".join(hour).strip():
                    hours_list.append(
                        "; ".join("".join(hour).strip().split("\n")).strip()
                    )

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

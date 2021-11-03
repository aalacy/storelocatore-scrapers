# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

website = "cinentreprise.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.cinentreprise.com/nousjoindre"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath("//table//tr")
    for index in range(2, len(stores), 2):

        page_url = search_url
        location_name = "".join(stores[index].xpath("td[1]/h3/strong/text()")).strip()
        location_type = "<MISSING>"
        locator_domain = website

        raw_info = stores[index + 1].xpath("td[1]/p[1]/text()")
        if len(raw_info) <= 0:
            raw_info = stores[index + 1].xpath("td[1]/text()")
        street_address = raw_info[1].strip()

        city = raw_info[2].strip().split(",")[0].strip()
        state = raw_info[2].strip().split(",")[1].strip().split(" ", 1)[0].strip()
        zipp = raw_info[2].strip().split(",")[1].strip().split(" ", 1)[-1].strip()
        phone = (
            raw_info[0]
            .strip()
            .replace(":", "")
            .strip()
            .replace("Info horaire", "")
            .strip()
        )

        hours_of_operation = "<MISSING>"

        country_code = "CA"
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
            zip_postal=zipp,
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

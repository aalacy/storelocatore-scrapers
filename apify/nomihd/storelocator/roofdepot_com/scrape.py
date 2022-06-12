# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import us

website = "roofdepot.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.roofdepot.com/contact/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="col-sm-3 "]/p[position()>1]')
    for index in range(0, len(stores), 2):
        page_url = search_url
        location_type = "<MISSING>"
        locator_domain = website
        location_name = "".join(stores[index].xpath("strong[1]/text()")).strip()
        if location_name == "":
            location_name = "Georgia"

        raw_info = stores[index].xpath("text()")
        raw_list = []
        for raw in raw_info:
            if len("".join(raw).strip()) > 0:
                raw_list.append("".join(raw).strip())

        street_address = (
            ", ".join(raw_list[:-2])
            .strip()
            .replace("Roof Depot National Support Center,", "")
            .strip()
        )
        city = raw_list[-2].split(",")[0].strip()
        state = raw_list[-2].split(",")[1].strip().split(" ")[0].strip()
        zip = raw_list[-2].split(",")[1].strip().split(" ")[-1].strip()
        country_code = "<MISSING>"
        if us.states.lookup(state):
            country_code = "US"

        phone = raw_list[-1].strip().replace("Phone:", "").strip()

        hours_of_operation = (
            "".join(
                ":".join(stores_sel.xpath('//div[@class="col-sm-3 "]/p[1]/text()'))
                .strip()
                .split("\n")
            )
            .encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", "-")
            .strip()
        )

        store_number = "<MISSING>"

        latitude = "<MISSING>"
        longitude = "<MISSING>"

        map_link = "".join(stores[index].xpath("iframe/@src")).strip()
        if len(map_link) <= 0:
            map_link = "".join(stores[index + 1].xpath("iframe/@src")).strip()

        if len(map_link) > 0:
            latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
            longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()

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

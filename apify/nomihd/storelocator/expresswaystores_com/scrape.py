# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import us

website = "expresswaystores.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "http://expresswaystores.com/gas-stations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="locations_wrapper"]/ul/li')
    for store in stores:
        page_url = "".join(store.xpath("span/a/@href")).strip()
        location_type = "<MISSING>"
        locator_domain = website
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        location_name = (
            "".join(store_sel.xpath('//h1[@class="main-title entry-title "]//text()'))
            .strip()
            .encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", "-")
            .strip()
        )

        address = store_sel.xpath('//div[@class="avia_textblock  "]/p[1]/text()')[1:]
        street_address = ", ".join(address[:-1]).strip().replace("\n", "").strip()
        if "," in street_address:
            street_address = street_address.split(",")[0].strip()
        city = address[-1].strip().split(",")[0].strip()
        state = address[-1].strip().split(",")[1].strip().split(" ")[0].strip()
        zip = address[-1].strip().split(",")[1].strip().split(" ")[-1].strip()
        country_code = "<MISSING>"
        if us.states.lookup(state):
            country_code = "US"

        phone = "".join(
            store_sel.xpath(
                '//div[@class="avia_textblock  "]/p[2]/a[contains(@href,"tel:")]/text()'
            )
        ).strip()

        hours_of_operation = "".join(
            store_sel.xpath('//div[@class="avia-promocontent"]/p[1]/text()')
        ).strip()
        store_number = "<MISSING>"

        latitude = ""
        try:
            latitude = (
                store_req.text.split("['lat'] = ")[1].strip().split(";")[0].strip()
            )
        except:
            pass
        longitude = ""
        try:
            longitude = (
                store_req.text.split("['long'] = ")[1].strip().split(";")[0].strip()
            )
        except:
            pass

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

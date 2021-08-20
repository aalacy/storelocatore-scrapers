# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html

website = "consolidatedtheatres.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.consolidatedtheatres.com/sitemap.xml"
    stores_req = session.get(search_url, headers=headers)
    stores = stores_req.text.split("<loc>")
    for index in range(1, len(stores)):
        page_url = "".join(stores[index].split("</loc>")[0].strip()).strip()
        if "/cinema-info" in page_url:
            if "https://www.consolidatedtheatres.com/cinema-info" in page_url:
                continue

            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)

            locator_domain = website
            location_name = "".join(
                store_sel.xpath('//section[@aria-label="Cinema Title"]//text()')
            ).strip()
            if len(location_name) <= 0:
                continue
            raw_list = store_sel.xpath('//div[@class="address"]/ul/li/text()')

            street_address = ", ".join(raw_list[1:-3]).strip()
            city_state_zip = raw_list[-3]
            city = city_state_zip.split(",")[0].strip()
            state = city_state_zip.split(",")[1].strip()
            zip = city_state_zip.split(",")[-1].strip()

            country_code = "US"

            store_number = "<MISSING>"
            location_type = "<MISSING>"

            phone = raw_list[-2].strip()
            hours_of_operation = "<MISSING>"

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

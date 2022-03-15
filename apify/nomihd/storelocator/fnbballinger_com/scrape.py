# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html

website = "fnbballinger.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.fnbballinger.com/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)

    stores = stores_sel.xpath(
        '//div[@class="locations-container"]//div[@class="col-md-6"]'
    )

    for store in stores:

        page_url = search_url
        location_name = "".join(store.xpath("h4/text()")).strip()
        locator_domain = website

        raw_info = store.xpath("p/text()")
        address = raw_info[0].strip().split("|")
        street_address = address[0].strip()
        city = address[1].strip().split(",")[0].strip()
        state = address[1].strip().split(",")[-1].strip().split(" ")[0].strip()
        zip = address[1].strip().split(",")[-1].strip().split(" ")[-1].strip()
        country_code = "US"
        store_number = "<MISSING>"
        phone = raw_info[2].strip().replace("- Banking", "").strip()

        location_type = "<MISSING>"

        hours_list = []
        hours = store.xpath("table/tbody/tr/td[1]")
        for hour in hours:
            day = "".join(hour.xpath("strong/text()")).strip()
            if len(day) > 0:
                time = "".join(hour.xpath("text()")).strip()
                hours_list.append(day + ":" + time)

        hours_of_operation = "; ".join(hours_list).strip()

        map_link = "".join(
            store.xpath('p/a[contains(text(),"View Map")]/@href')
        ).strip()
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if "/@" in map_link:
            latitude = map_link.split("/@")[1].strip().split(",")[0].strip()
            longitude = map_link.split("/@")[1].strip().split(",")[1]

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

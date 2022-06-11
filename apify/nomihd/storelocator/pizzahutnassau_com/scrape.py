# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
import lxml.html

website = "pizzahutnassau.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Referer": "https://www.pizzahutnassau.com/our-location/",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.pizzahutnassau.com/our-location/"
    search_res = session.get(
        "https://www.pizzahutnassau.com/?ajax=true&action=map_locations",
        headers=headers,
    )
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    addresses = stores_sel.xpath('//article[@id="thecontent"]//p[1]')
    add_list = []
    for add in addresses:
        add_list.append(
            "".join(add.xpath(".//text()"))
            .strip()
            .split("\n")[0]
            .strip()
            .split("(")[0]
            .strip()
        )

    stores = json.loads(search_res.text)

    index = 0
    for store in stores:
        store_number = "<MISSING>"
        page_url = search_url
        locator_domain = website
        if "pizza hut" not in store["title"].lower():
            location_name = "PIZZA HUT " + store["title"]
        else:
            location_name = store["title"]

        street_address = add_list[index]
        city = "Nassau Bahamas"
        state = "<MISSING>"
        zip = "<MISSING>"

        country_code = "Bahamas"
        phone = store["phone"]

        location_type = "<MISSING>"

        hours_of_operation = store["hours"]

        latitude, longitude = (
            store["latitude"],
            store["longitude"],
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
        )
        index = index + 1


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

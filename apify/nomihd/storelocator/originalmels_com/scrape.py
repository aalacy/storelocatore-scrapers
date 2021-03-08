# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import us
import lxml.html

website = "originalmels.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://originalmels.com/wp-admin/admin-ajax.php"

    data = {
        "action": "get_all_stores",
        "lat": "",
        "lng": "",
    }

    stores_req = session.post(search_url, data=data, headers=headers)
    stores = json.loads(stores_req.text)

    for key in stores.keys():
        latitude = stores[key]["lat"]
        longitude = stores[key]["lng"]
        page_url = stores[key]["gu"]
        log.info(page_url)
        locator_domain = website
        location_name = stores[key]["na"]
        if location_name == "":
            location_name = "<MISSING>"

        street_address = stores[key]["st"]
        city = stores[key]["ct"]
        state = stores[key]["rg"]
        zip = ""
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        address = store_sel.xpath('//div[@class="store_locator_single_address"]/text()')
        zip = address[-1].split(",")[1].strip().split(" ")[-1].strip()

        country_code = "<MISSING>"
        if us.states.lookup(state):
            country_code = "US"

        store_number = str(stores[key]["ID"])
        location_type = "<MISSING>"

        phone = "<MISSING>"
        hours = stores[key]["op"]
        hours_of_operation = ""
        if len(hours["0"].strip()) > 0:
            hours_of_operation = (
                hours_of_operation + "Monday:" + hours["0"] + "-" + hours["1"] + ";"
            )

        if len(hours["2"].strip()) > 0:
            hours_of_operation = (
                hours_of_operation + "Tuesday:" + hours["2"] + "-" + hours["3"] + ";"
            )

        if len(hours["4"].strip()) > 0:
            hours_of_operation = (
                hours_of_operation + "Wednesday:" + hours["4"] + "-" + hours["5"] + ";"
            )

        if len(hours["6"].strip()) > 0:
            hours_of_operation = (
                hours_of_operation + "Thursday:" + hours["6"] + "-" + hours["7"] + ";"
            )
        if len(hours["8"].strip()) > 0:
            hours_of_operation = (
                hours_of_operation + "Friday:" + hours["8"] + "-" + hours["9"] + ";"
            )

        if len(hours["10"].strip()) > 0:
            hours_of_operation = (
                hours_of_operation + "Saturday:" + hours["10"] + "-" + hours["11"] + ";"
            )

        if len(hours["12"].strip()) > 0:
            hours_of_operation = (
                hours_of_operation + "Sunday:" + hours["12"] + "-" + hours["13"]
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

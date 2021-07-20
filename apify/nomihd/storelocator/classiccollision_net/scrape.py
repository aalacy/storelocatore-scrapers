# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import lxml.html


website = "classiccollision.net"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "classiccollision.net",
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
    api_url = "https://classiccollision.net/wp-admin/admin-ajax.php?action=store_search&lat=21.958&lng=-114.388&max_results=50000&search_radius=1000&autoload=1"
    api_res = session.get(api_url, headers=headers)

    json_res = json.loads(api_res.text)

    stores_list = json_res

    for store in stores_list:

        page_url = store["permalink"]

        store_number = store["id"]
        locator_domain = website

        location_name = store["store"].strip()
        street_address = store["address"].strip()
        if "," in street_address:
            street_address = street_address.split(",")[0].strip()

        city = store["city"].strip()
        state = store["state"].strip()

        zip = store["zip"].strip()

        country_code = store["country"]
        phone = store["phone"]

        if not phone:
            log.info(page_url)
            page_res = session.get(page_url, headers=headers)
            page_sel = lxml.html.fromstring(page_res.text)

            phone = (
                "".join(page_sel.xpath('//*[contains(text(),"Phone")]//text()'))
                .replace("Phone:", "")
                .strip()
            )

        phone = phone.split("(call hours")[0]
        location_type = "<MISSING>"

        if store["hours"]:
            hours_info = store["hours"]
            hours_sel = lxml.html.fromstring(hours_info)

            hours = list(filter(str, [x.strip() for x in hours_sel.xpath("//text()")]))

            hours_of_operation = "; ".join(hours).replace("day; ", "day: ")

        latitude = store["lat"]
        longitude = store["lng"]

        raw_address = "<MISSING>"
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

# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import lxml.html


website = "charmdiamondcentres.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "charmdiamondcentres.com",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "accept": "*/*",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://www.kellysroastbeef.com",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.kellysroastbeef.com/locations/",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here
    base = "https://charmdiamondcentres.com"
    api_url = "https://charmdiamondcentres.com/store-locator/json"
    api_res = session.get(api_url, headers=headers)

    json_res = json.loads(api_res.text)

    stores_list = json_res["features"]

    for store in stores_list:

        page_url = base
        store_sel = lxml.html.fromstring(store["properties"]["name"])
        store_info = list(
            filter(
                str,
                [x.strip() for x in store_sel.xpath("//text()")],
            )
        )

        page_url = page_url + "".join(store_sel.xpath("//@href"))

        store_number = store["properties"]["Nid"]
        locator_domain = website

        location_name = "".join(store_info).strip()
        store_sel = lxml.html.fromstring(store["properties"]["description"])

        street_address = " ".join(
            store_sel.xpath('//*[@class="thoroughfare"]//text()')
        ).strip()
        city = " ".join(store_sel.xpath('//*[@class="locality"]//text()')).strip()
        state = " ".join(store_sel.xpath('//*[@class="state"]//text()')).strip()

        zip = " ".join(store_sel.xpath('//*[@class="postal-code"]//text()')).strip()

        country_code = " ".join(
            store_sel.xpath('//*[@class="country"]//text()')
        ).strip()
        phone = store["properties"]["gsl_props_phone_rendered"]

        location_type = "<MISSING>"

        hours_of_operation = "<MISSING>"

        latitude = store["geometry"]["coordinates"][1]
        longitude = store["geometry"]["coordinates"][0]

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

# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
import lxml.html

website = "advhomehealth.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "advhomehealth.com",
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
    base = "https://advhomehealth.com/locations/"
    api_url = "https://locations.brightspringhealth.com/wp-json/advhh/v1/locations/all"
    api_res = session.get(api_url, headers=headers)

    json_res = json.loads(api_res.text)

    store_list = json_res["data"]["locations"]

    stores_req = session.get(base, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)

    for store in store_list:

        page_url = (
            base
            + store["state"].replace(" ", "-")
            + "/"
            + store["city"].replace(" ", "-")
            + "/"
            + str(store["ID"])
        )
        locator_domain = website

        location_name = store["post_title"].replace("&#8211;", "-")

        street_address = store["address_line_1"]
        if "address_line_2" in store and store["address_line_2"]:
            street_address = (
                (street_address + ", " + store["address_line_2"]).strip(", ").strip()
            )

        city = store["city"]
        state = store["state"]
        zip = store["zip"]

        country_code = store["country"]

        store_number = store["ID"]

        phone = store["phone"]

        location_type = "<MISSING>"

        hours_of_operation = "<MISSING>"
        raw_text = stores_sel.xpath('//div[@class="heading"]/p')
        for raw in raw_text:
            if "All offices are open " in "".join(raw.xpath("text()")).strip():
                try:
                    hours_of_operation = (
                        "".join(raw.xpath("text()"))
                        .strip()
                        .split("All offices are open")[1]
                        .strip()
                        .split("(")[0]
                        .strip()
                    )
                except:
                    pass

        latitude, longitude = store["latitude"], store["longitude"]
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

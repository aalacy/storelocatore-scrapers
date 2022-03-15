# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json

website = "furla.com/ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.furla.com/ca/en/"
    home_page_req = session.get(search_url, headers=headers)
    home_page_sel = lxml.html.fromstring(home_page_req.text)
    home_page_id = "".join(
        home_page_sel.xpath('//div[@id="destination2"]/div/@data-id')
    ).strip()

    stores_req = session.get(
        "https://api.livestory.io/front/v4/wallgroup/{}?store_code=STORE_ID&lang_code=en".format(
            home_page_id
        ),
        headers=headers,
    )
    stores = json.loads(stores_req.text)["walls"][0]["layout"]["grid"][0]["text"].split(
        "<h3 style"
    )

    for index in range(1, len(stores)):
        page_url = search_url
        location_type = "<MISSING>"
        locator_domain = website
        store_data = stores[index]
        store_sel = lxml.html.fromstring(store_data)
        location_name = "".join(store_sel.xpath("//strong[1]/text()")).strip()

        address = (
            "".join(store_sel.xpath("//h4[1]/text()")).replace(", Canada", "").strip()
        )
        street_address = address.split(",")[0].strip()
        city = address.split(",")[1].strip()
        state_zip = address.split(",")[-1].strip()
        state = state_zip.split(" ", 1)[0].strip()
        zip = state_zip.split(" ", 1)[-1].strip()
        country_code = "CA"
        phone = ""
        raw_text = store_sel.xpath("//h4/text()")
        for temp in raw_text:
            if "Phone Number:" in "".join(temp).strip():
                phone = (
                    "".join(temp)
                    .strip()
                    .replace("Phone Number:", "")
                    .strip()
                    .replace("+1-", "")
                    .strip()
                )

        hours_of_operation = "<MISSING>"
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

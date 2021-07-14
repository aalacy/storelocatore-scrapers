# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html

website = "ubburger.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.ubburger.com",
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
    search_url = "https://www.ubburger.com/locations/"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    store_list = search_sel.xpath('//div[@id="locations"]//li')

    for store in store_list:

        page_url = search_url

        locator_domain = website

        store_info = list(
            filter(
                str,
                [x.strip() for x in store.xpath("./p//text()")],
            )
        )

        for mail_idx, x in enumerate(store_info):
            if "EMAIL" in x.upper():
                break

        full_address = store_info[:mail_idx]
        store_info = " ".join(store_info)

        street_address = ", ".join(full_address[:-1]).strip()

        city = full_address[-1].split(",")[0].strip()
        state = full_address[-1].split(",")[-1].strip().split(" ")[0].strip()
        zip = " ".join(full_address[-1].split(",")[-1].strip().split(" ")[1:]).strip()
        country_code = "CA"

        if not street_address:
            street_address = " ".join(city.split(" ")[:-1]).strip("., ").strip()
            city = city.split(" ")[-1].strip()

        location_name = "".join(store.xpath("./h5/text()")).strip()

        phone = store_info.split("Fax:")[0].split("Hours")[0].split("Phone:")[1].strip()

        store_number = "<MISSING>"

        location_type = "<MISSING>"

        hours_of_operation = "<MISSING>"

        map_link = "".join(store.xpath("./@onclick"))

        latitude, longitude = (
            map_link.split("(")[1].split(",")[0],
            map_link.split("(")[1].split(",")[1].split(");")[0].strip(),
        )

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

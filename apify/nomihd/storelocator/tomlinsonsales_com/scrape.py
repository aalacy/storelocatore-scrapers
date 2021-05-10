# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html

website = "tomlinsonsales.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    base = "https://www.tomlinsonsales.com"
    search_url = "https://www.tomlinsonsales.com/pages/locations"
    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)

    stores_list = search_sel.xpath('//div[@class="rte"]//span/a/@href')

    for store in stores_list:

        page_url = base + store
        log.info(page_url)
        page_res = session.get(page_url, headers=headers)
        page_sel = lxml.html.fromstring(page_res.text)
        locator_domain = website

        location_name = "".join(page_sel.xpath("//h1/text()")).strip()

        address_info = page_sel.xpath(
            '//div[@class="rte"]/div[not(./img) and not(.//a) and contains(@style,"center")]//text()'
        )
        address_info = list(filter(bool, [x.strip(" \n") for x in address_info]))

        phone_index = [
            idx for idx, element in enumerate(address_info) if "-" in element
        ]
        if len(address_info) < 4:
            city = page_url.split("-")[0].split("/")[-1].capitalize()
            state = page_url.split("-")[1].upper()
            zip = "<MISSING>"
            street_address = (
                " ".join(address_info[: phone_index[0]])
                .replace("\n", " ")
                .replace("  ", " ")
                .strip()
            )
            hours_of_operation = "<MISSING>"
        else:

            street_address = (
                " ".join(address_info[: phone_index[0] - 1])
                .replace("\n", " ")
                .replace("  ", " ")
                .replace("Biggs Park Mall", "")
                .strip()
            )

            cty_st_zip = address_info[phone_index[0] - 1]
            city = cty_st_zip.split(",")[0].strip()
            state = cty_st_zip.split(",")[1].strip().split(" ")[0].strip()
            zip = cty_st_zip.split(",")[1].strip().split(" ")[1].strip()
            hours_of_operation = "; ".join(address_info[phone_index[0] + 1 :]).strip()

        country_code = "US"

        store_number = "<MISSING>"

        phone = address_info[phone_index[0]].strip()

        location_type = "<MISSING>"

        latitude = "<MISSING>"
        longitude = "<MISSING>"
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

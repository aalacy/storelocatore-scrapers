# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html


website = "cactussalon.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://cactussalon.com/"
    search_res = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_res.text)

    stores_list = search_sel.xpath(
        '//li[contains(.//text(), "Locations")]//ul[@class="sub-menu"]/li/a[contains(@href,"https")]/@href'
    )

    for store in stores_list:

        page_url = store
        log.info(page_url)
        page_res = session.get(page_url, headers=headers)
        page_sel = lxml.html.fromstring(page_res.text)
        locator_domain = website

        location_name = "".join(page_sel.xpath("//section[2]//h2/text()")).strip()

        address_info = page_sel.xpath(
            '//section[3]//div[@class="elementor-row"]/div[1]//p//text()'
        )
        address_info = list(filter(bool, [x.strip(" \n") for x in address_info]))

        phone_index = [
            idx for idx, element in enumerate(address_info) if "-" in element
        ]

        street_address = (
            ", ".join(address_info[: phone_index[0] - 1])
            .replace("\n", " ")
            .replace("  ", " ")
            .strip()
        )

        cty_st_zip = address_info[phone_index[0] - 1]
        city = cty_st_zip.split(",")[0].strip()
        state = cty_st_zip.split(",")[1].strip().split(" ")[0].strip()
        zip = cty_st_zip.split(",")[1].strip().split(" ")[1].strip()
        country_code = "US"

        store_number = "<MISSING>"

        phone = address_info[phone_index[0]].strip()

        location_type = "<MISSING>"

        hours_info = page_sel.xpath(
            '//section[3]//div[@class="elementor-row"]/div[2]//p//text()'
        )
        hours_info = list(filter(bool, [x.strip(" \n") for x in hours_info]))

        hours_of_operation = "; ".join(hours_info).replace("day", "day:")

        lat_lng_href = "".join(
            page_sel.xpath('//section[3]//div[@class="elementor-row"]/div[1]//a/@href')
        )
        if "z/data" in lat_lng_href:
            lat_lng = lat_lng_href.split("/@")[1].split("z/data")[0]

            latitude = lat_lng.split(",")[0].strip()
            longitude = lat_lng.split(",")[1].strip()
        else:
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

# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html

website = "heffins.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.heffins.com/about-us/locations"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    sections = stores_sel.xpath('//div[@class="col-lg-4 col-sm-4 col-xs-12"]')
    for sec in sections:
        names = sec.xpath("h5/strong/text()")
        raw_info = sec.xpath("p")
        raw_info_index = 0
        for index in range(0, len(names)):
            page_url = search_url
            locator_domain = website

            location_name = names[index]

            if len("".join(raw_info[raw_info_index].xpath(".//text()")).strip()) <= 0:
                raw_info_index = raw_info_index + 1

            address = raw_info[raw_info_index].xpath(".//text()")

            street_address = ""
            city = ""
            state = ""
            zip = ""
            country_code = ""

            if location_name == "London, UK":
                street_address = address[1].strip()
                city = address[-1].strip().split(",")[0].strip()
                state = "<MISSING>"
                zip = address[-1].strip().split(",")[-1].strip()
                country_code = "GB"

            else:
                street_address = address[0].strip()
                city = address[-1].strip().split(",")[0].strip()
                state = address[-1].strip().split(",")[-1].strip().split(" ")[0].strip()
                zip = address[1].strip().split(",")[-1].strip().split(" ")[-1].strip()
                country_code = "US"

            store_number = "<MISSING>"

            if len("".join(raw_info[raw_info_index + 1].xpath("text()")).strip()) <= 0:
                raw_info_index = raw_info_index + 1

            phone = "".join(raw_info[raw_info_index + 1].xpath("text()")).strip()

            if "or" in phone:
                phone = phone.split("or")[0].strip()
            location_type = "<MISSING>"

            hours_of_operation = "<MISSING>"

            latitude = "<MISSING>"
            longitude = "<MISSING>"

            raw_info_index = raw_info_index + 3
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

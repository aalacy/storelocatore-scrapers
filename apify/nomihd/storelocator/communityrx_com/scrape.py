# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html

website = "communityrx.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.communityrx.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="entry-the-content"]/h3/a/@href')

    for store_url in stores:
        page_url = store_url
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        locator_domain = website
        location_name = "".join(
            store_sel.xpath('//h3[@class="widget-title"]/span/text()')
        ).strip()

        raw_info = store_sel.xpath('//div[@class="textwidget"]/p//text()')
        raw_list = []
        for raw in raw_info:
            if len("".join(raw).strip()) > 0:
                raw_list.append("".join(raw).strip())

        add_list = ""
        phone = ""
        hours_of_operation = ""
        for index in range(0, len(raw_list)):
            if "harmacy:" in "".join(raw_list[index]).strip():
                phone = raw_list[index + 1]
                add_list = raw_list[: index - 1]
            if "Pharmacy:" in "".join(raw_list[index]).strip():
                phone = raw_list[index + 1]
                add_list = raw_list[:index]
            if "Store Hours:" in "".join(raw_list[index]).strip():
                hours_of_operation = (
                    "; ".join(raw_list[index + 1 :])
                    .strip()
                    .replace(":;", ":")
                    .encode("ascii", "replace")
                    .decode("utf-8")
                    .replace("?", "-")
                    .strip()
                    .replace("; Copyright - 2010-2021 Community Pharmacies", "")
                    .strip()
                )

        street_address = add_list[0].strip()
        city = add_list[-1].strip().split(",")[0].strip()
        state = add_list[-1].strip().split(",")[1].strip().split(" ")[0].strip()
        zip = add_list[-1].strip().split(",")[1].strip().split(" ")[-1].strip()

        country_code = "US"

        store_number = "<MISSING>"
        location_type = "<MISSING>"

        latitude = "<MISSING>"
        longitude = "<MISSING>"
        map_link = "".join(
            store_sel.xpath('//iframe[contains(@src,"/maps/embed?")]/@src')
        ).strip()
        if len(map_link) > 0:
            latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
            longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()

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

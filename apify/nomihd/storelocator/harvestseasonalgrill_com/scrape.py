# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import json

website = "harvestseasonalgrill.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    search_url = "https://harvestseasonal.com/menus-locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath(
        '//div[contains(@class,"fusion_builder_column_1_3 1_3 fusion-one-third")]'
    )

    for store in stores:
        page_url = "".join(store.xpath(".//h4/a/@href")).strip()
        locator_domain = website

        location_name = "".join(store.xpath(".//h4//text()")).strip()

        phone = "".join(
            store.xpath(
                './/p[@class="location-address--text"]//a[contains(@href,"tel:")]/text()'
            )
        ).strip()

        store_number = "<MISSING>"
        location_type = "<MISSING>"
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        json_list = store_sel.xpath('//script[@type="application/ld+json"]/text()')

        for js in json_list:
            if "streetAddress" in js:
                try:
                    store_json = json.loads(js)
                except:
                    store_json = json.loads(js.rsplit("}", 1)[0].strip())
                street_address = store_json["address"]["streetAddress"]
                city = store_json["address"]["addressLocality"]
                state = store_json["address"]["addressRegion"]
                zip = store_json["address"]["postalCode"]
                country_code = store_json["address"]["addressCountry"]

        hours_of_operation = ""
        try:
            hours_of_operation = (
                (
                    store_req.text.split("<strong>Hours of Operation</strong><br />")[1]
                    .strip()
                    .split("</div>")[0]
                    .strip()
                    .replace("</p>", "; ")
                    .strip()
                    .replace("<p>", "")
                    .strip()
                    .replace("\n", "")
                    .strip()
                    .replace("&#8211;", "-")
                    .strip()
                )
                .encode("ascii", "replace")
                .decode("utf-8")
                .replace("?", "-")
                .strip()
            )
        except:
            pass

        if hours_of_operation == "" or len(hours_of_operation.strip()) <= 0:
            sections = store_sel.xpath(
                '//div[@class="fusion-column-content-centered"]//p'
            )
            hours_list = []
            for sec in range(0, len(sections)):
                if (
                    "Hours of Operation"
                    in "".join(sections[sec].xpath(".//text()")).strip()
                ):
                    hours = sections[sec + 1 :]
                    for hour in hours:
                        if (
                            "happy hour"
                            in "".join(hour.xpath(".//text()")).strip().lower()
                        ):
                            break
                        hours_list.append("".join(hour.xpath("text()")).strip())

            hours_of_operation = (
                "; ".join(hours_list)
                .strip()
                .encode("ascii", "replace")
                .decode("utf-8")
                .replace("?", "-")
                .strip()
            )

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

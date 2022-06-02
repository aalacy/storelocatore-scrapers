# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import us
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "bargainhunt.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.bargainhunt.com/store-locator"
    stores_req = session.get(search_url, headers=headers)
    stores = stores_req.text.split("var marker_")
    for index in range(1, len(stores)):
        store_info = (
            stores[index].split("content: '")[1].strip().split("</div>'")[0].strip()
        )
        store_sel = lxml.html.fromstring(store_info)
        location_name = "".join(store_sel.xpath(".//h4/text()")).strip()
        page_url = search_url
        locator_domain = website

        street_address = "".join(
            store_sel.xpath('//div[@class="address"]/div/div/text()[1]')
        ).strip()

        city_state_zip = "".join(
            store_sel.xpath('//div[@class="address"]/div/div/text()[2]')
        ).strip()
        if ", " not in city_state_zip:
            city_state_zip = "".join(
                store_sel.xpath('//div[@class="address"]/div/div/text()[3]')
            ).strip()

            phone = "".join(
                store_sel.xpath('//div[@class="address"]/div/div/text()[4]')
            ).strip()
            hours_of_operation = "".join(
                store_sel.xpath('//div[@class="address"]/div/div/text()[6]')
            ).strip()
        else:
            phone = "".join(
                store_sel.xpath('//div[@class="address"]/div/div/text()[3]')
            ).strip()
            hours_of_operation = "".join(
                store_sel.xpath('//div[@class="address"]/div/div/text()[5]')
            ).strip()

        city = city_state_zip.split(",")[0].strip()
        state = city_state_zip.split(",")[1].strip().split(" ")[0].strip()
        zip = city_state_zip.split(",")[1].strip().split(" ")[1].strip()

        country_code = "<MISSING>"
        if us.states.lookup(state):
            country_code = "US"

        store_number = "<MISSING>"

        location_type = "<MISSING>"

        latitude = (
            "".join(stores[index]).split("lat: ")[1].strip().split(",")[0].strip()
        )
        longitude = (
            "".join(stores[index])
            .split("lng: ")[1]
            .strip()
            .split(",")[0]
            .strip()
            .replace("}", "")
            .strip()
        )

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
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

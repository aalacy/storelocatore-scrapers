# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import us

website = "hbtbank.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.hbtbank.com/locations"
    stores_req = session.get(search_url, headers=headers)
    stores = stores_req.text.split("https://www.hbtbank.com/locations/")
    stores_list = []
    for index in range(1, len(stores)):
        stores_list.append(
            "https://www.hbtbank.com/locations/" + stores[index].split('">')[0].strip()
        )
    stores_list = list(set(stores_list))

    for store_url in stores_list:
        page_url = store_url
        locator_domain = website
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        location_name = "".join(store_sel.xpath("//h1/text()")).strip()

        address = store_sel.xpath(
            '//div[@class="col-sm-12 col-md-6 col-lg-5"]/p/text()'
        )
        add_list = []
        for add in address:
            add_list.append("".join(add).strip())

        street_address = add_list[0]
        city = add_list[1].split(",")[0].strip()
        state = add_list[1].split(",")[1].strip().split(" ")[0].strip()
        zip = add_list[1].split(",")[1].strip().split(" ")[1].strip()
        country_code = "<MISSING>"
        if us.states.lookup(state):
            country_code = "US"

        store_number = "<MISSING>"
        phone = add_list[2].strip().replace("Phone:", "").strip()

        location_type = "<MISSING>"
        temp_hours = store_sel.xpath('//div[@class="col"]')
        hours_of_operation = ""
        hours_list = []
        for temp in temp_hours:
            if "Lobby Hours" in "".join(temp.xpath("h2/text()")).strip():
                hours = "".join(temp.xpath("p/text()")).strip().split("\n")
                for hour in hours:
                    if len("".join(hour).strip()) > 0:
                        hours_list.append("".join(hour).strip())

        hours_of_operation = " ".join(hours_list).strip()

        latitude = (
            store_req.text.split("map2_map.setCenter(new google.maps.LatLng(")[1]
            .strip()
            .split(",")[0]
            .strip()
        )
        longitude = (
            store_req.text.split("map2_map.setCenter(new google.maps.LatLng(")[1]
            .strip()
            .split(",")[1]
            .strip()
            .split(")")[0]
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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import us

website = "lwsupply.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
}


def fetch_data():
    # Your scraper here
    search_url = "https://lwsupply.com/locations-map/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[@class="col-sm-12 col-md-4 col-lg-3"]')
    for store in stores:
        page_url = "".join(store.xpath(".//strong/a/@href")).strip()
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)
        locator_domain = website
        location_name = (
            "".join(store_sel.xpath('//h1[@class="page-title"]/text()'))
            .strip()
            .encode("ascii", "replace")
            .decode("utf-8")
            .replace("?", "-")
            .strip()
        )

        address = store_sel.xpath('//div[@class="content-text-block"]')
        for add in address:
            if "address-block" in "".join(add.xpath("div/@class")).strip():
                temp_text = add.xpath('div[@class="address-block"]/text()')
                raw_text = []
                for t in temp_text:
                    if len("".join(t.strip())) > 0:
                        raw_text.append("".join(t.strip()))

                if raw_text[0] == ",":
                    street_address = "<MISSING>"
                    city = location_name.split("-")[1].strip().split(",")[0].strip()
                    state = location_name.split("-")[1].strip().split(",")[-1].strip()
                    zip = "<MISSING>"
                else:
                    street_address = raw_text[0].strip()
                    city_state_zip = raw_text[1]
                    city = city_state_zip.split(",")[0].strip()
                    state = (
                        city_state_zip.split(",")[1].strip().rsplit(" ", 1)[0].strip()
                    )
                    zip = city_state_zip.split(",")[1].strip().rsplit(" ", 1)[1].strip()

                country_code = "<MISSING>"
                if us.states.lookup(state):
                    country_code = "US"

                store_number = "<MISSING>"
                phone = "".join(add.xpath('div[@class="address-block"]/a/text()'))

                location_type = "<MISSING>"
                hours_of_operation = (
                    " ".join(add.xpath("p[1]//text()"))
                    .strip()
                    .replace("\xa0", "")
                    .strip()
                    .encode("ascii", errors="replace")
                    .decode()
                    .replace("?", "-")
                    .strip()
                    .replace("\n", "")
                    .strip()
                )
                latitude = ""
                longitude = ""
                try:
                    latitude = (
                        store_req.text.split("lat: ")[1].strip().split(",")[0].strip()
                    )
                except:
                    pass

                try:
                    longitude = (
                        store_req.text.split("lng: ")[1].strip().split("}")[0].strip()
                    )
                except:
                    pass

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

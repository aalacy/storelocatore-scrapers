# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import lxml.html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "tex-mex.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    search_url = "https://tex-mex.com/locations/"
    with SgRequests() as session:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath(
            '//div[@class="col-lg-11 col-md-11 col-sm-10 col-xs-10 location-txt"]'
        )
        for store in stores:
            page_url = store.xpath('.//a[@class="readmore-btn"]/@href')
            if len(page_url) > 0:
                page_url = page_url[0]

                locator_domain = website

                location_name = "".join(store.xpath("h3//text()")).strip()
                if "coming soon" in location_name.lower():
                    continue
                address = store.xpath('p/a[contains(@href,"/maps/")]/text()')
                if len(address) <= 0:
                    address = store.xpath("p/text()")
                add_list = []
                for add in address:
                    if len("".join(add).strip()) > 0:
                        add_list.append("".join(add).strip())

                street_address = add_list[0].strip()
                city = add_list[1].split(",")[-2].strip()
                state = add_list[1].split(",")[-1].strip().split(" ")[0].strip()
                zip = add_list[1].split(",")[-1].strip().split(" ")[-1].strip()
                try:
                    street_address = (
                        street_address
                        + " "
                        + " ".join(add_list[1].split(",")[:-2]).strip()
                    )
                except:
                    pass

                country_code = "US"

                store_number = "<MISSING>"
                phone = "".join(
                    store.xpath('p/a[contains(@href,"tel:")]/text()')
                ).strip()

                location_type = "<MISSING>"
                log.info(page_url)
                store_req = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_req.text)

                hours = store_sel.xpath(
                    '//div[@class="col-lg-9 col-md-9 col-sm-12 col-xs-12 no-padding address"]/p/text()'
                )
                hours_list = []
                for hour in hours:
                    if len("".join(hour).strip()) > 0:
                        hours_list.append("".join(hour).strip())

                hours_of_operation = (
                    "; ".join(hours_list).strip().replace("Hours: ", "").strip()
                )

                latitude = ""
                longitude = ""
                try:
                    latitude = (
                        "".join(store.xpath("p/a[1]/@href"))
                        .strip()
                        .split("/@")[1]
                        .strip()
                        .split(",")[0]
                        .strip()
                    )
                except:
                    pass

                try:
                    longitude = (
                        "".join(store.xpath("p/a[1]/@href"))
                        .strip()
                        .split("/@")[1]
                        .strip()
                        .split(",")[1]
                        .strip()
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

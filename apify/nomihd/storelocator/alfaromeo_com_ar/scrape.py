# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "alfaromeo.com.ar"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def get_latlng(map_link):
    if "z/data" in map_link:
        lat_lng = map_link.split("@")[1].split("z/data")[0]
        latitude = lat_lng.split(",")[0].strip()
        longitude = lat_lng.split(",")[1].strip()
    elif "ll=" in map_link:
        lat_lng = map_link.split("ll=")[1].split("&")[0]
        latitude = lat_lng.split(",")[0]
        longitude = lat_lng.split(",")[1]
    elif "!2d" in map_link and "!3d" in map_link:
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
    elif "/@" in map_link:
        latitude = map_link.split("/@")[1].split(",")[0].strip()
        longitude = map_link.split("/@")[1].split(",")[1].strip()
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    # Your scraper here
    search_url = "http://alfaromeo.com.ar/concesionarios/"
    with SgRequests() as session:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath(
            '//div[@class="elementor-row"][./div[1]//img[@src="https://alfaromeo.com.ar/wp-content/uploads/2018/06/PIn-Alfa-Romeo.png"]]'
        )

        for store in stores:

            page_url = search_url
            locator_domain = website

            loc_city_state = store.xpath("div[2]//h2/text()")
            if len(loc_city_state) > 0:
                location_name = loc_city_state[0]
                address = store.xpath(
                    './/li[./a[contains(@href,"maps")]]/a[contains(@href,"maps")]/span[@class="elementor-icon-list-text"]/text()'
                )
                street_address = "".join(address).strip()
                if "," in street_address:
                    street_address = street_address.split(",")[0].strip()

                city = loc_city_state[-1]
                state = "<MISSING>"
                zip = "<MISSING>"

                country_code = "AR"

                store_number = "<MISSING>"

                phone = "".join(
                    store.xpath(
                        './/li[./a[contains(@href,"tel:")]]/a[contains(@href,"tel:")]/span[@class="elementor-icon-list-text"]/text()'
                    )
                ).strip()
                location_type = "<MISSING>"
                hours_of_operation = "; ".join(store.xpath(".//p/text()")).strip()

                map_link = "".join(
                    store.xpath(
                        './/li[./a[contains(@href,"maps")]]/a[contains(@href,"maps")]/@href'
                    )
                ).strip()
                latitude, longitude = get_latlng(map_link)

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
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.PHONE,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import us
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "bankoftennessee.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def split_fulladdress(address_info):
    street_address = " ".join(address_info[0:-1]).strip(" ,.")

    city_state_zip = (
        address_info[-1].replace(",", " ").replace(".", " ").replace("  ", " ").strip()
    )

    city = " ".join(city_state_zip.split(" ")[:-2]).strip()
    state = city_state_zip.split(" ")[-2].strip()
    zip = city_state_zip.split(" ")[-1].strip()

    if not city or us.states.lookup(zip):
        city = city + " " + state
        state = zip
        zip = "<MISSING>"

    if city and state:
        if not us.states.lookup(state):
            city = city + " " + state
            state = "<MISSING>"

    country_code = "US"
    return street_address, city, state, zip, country_code


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
    elif "destination=" in map_link:
        latitude = map_link.split("destination=")[1].split(",")[0].strip()
        longitude = map_link.split("destination=")[1].split(",")[1].strip()
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    # Your scraper here

    search_url = "https://www.bankoftennessee.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath(
        '//a[@href="https://www.bankoftennessee.com/locations/"]/..//ul[@class="dropdown-list"]/li'
    )
    for store_url in stores:
        page_url = "".join(store_url.xpath("./a/@href"))
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        sub_stores = store_sel.xpath('//div[@class="branch-card"]')

        for idx, sub_store in enumerate(sub_stores, 1):
            location_name = "".join(sub_store.xpath(".//h2/text()")).strip()

            location_type = "<MISSING>"
            locator_domain = website
            raw_address = "<MISSING>"

            full_address = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in sub_store.xpath(
                            './/div[@class="card-location col-icon icon-location"]/p//text()'
                        )
                    ],
                )
            )

            street_address, city, state, zip, country_code = split_fulladdress(
                full_address
            )

            phone = "".join(sub_store.xpath('.//a[contains(@href,"tel:")]//text()'))

            hours = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in sub_store.xpath(
                            './/div[@class="card-location col-icon icon-lobby"]/p//text()'
                        )
                    ],
                )
            )
            hours_of_operation = (
                "; ".join(hours).replace("Thu;", "Thu:").replace("Fri;", "Fri:").strip()
            )

            store_number = "<MISSING>"

            latitude = "<MISSING>"
            longitude = "<MISSING>"
            map_link = "".join(
                sub_store.xpath('.//a[contains(@href,"maps")]/@href')
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
                raw_address=raw_address,
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

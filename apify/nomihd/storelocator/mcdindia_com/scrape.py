# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "mcdindia.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
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

    search_url = "https://mcdindia.com/"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)
        log.info(search_res)
        search_sel = lxml.html.fromstring(search_res.text)

        stores = search_sel.xpath('//div[contains(@class,"store-item")]')

        for store in stores:

            locator_domain = website

            location_name = "MC-" + "".join(store.xpath("./@id")).strip("post- ")
            page_url = search_url + location_name

            full_address = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store.xpath(
                            './/div[@class="location-text para-text"]//text()'
                        )
                    ],
                )
            )

            raw_address = ", ".join(full_address)
            try:
                temp_add = (
                    raw_address.rsplit("-", 1)[-1].strip().replace(" ", "").strip()
                )
                if temp_add.isdigit():
                    raw_address = (
                        raw_address.rsplit("-", 1)[0].strip() + ", " + temp_add
                    )
            except:
                pass
            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            if street_address is not None:
                street_address = street_address.replace("Ste", "Suite")

            if street_address:
                try:
                    temp_add = (
                        street_address.rsplit("-", 1)[-1]
                        .strip()
                        .replace(" ", "")
                        .strip()
                    )
                    if temp_add.isdigit():
                        street_address = full_address.rsplit("-", 1)[0].strip()
                except:
                    pass

            if street_address and street_address.isdigit():
                street_address = ", ".join(raw_address.split(",")[:-2]).strip()

            city = "".join(store.xpath("./@data-city")).strip()
            state = formatted_addr.state
            zip = formatted_addr.postcode
            if zip:
                zip = zip.split("-")[-1].strip()

            if not zip:
                try:
                    temp_zip = (
                        raw_address.split(",")[-1].strip().replace(" ", "").strip()
                    )
                    if temp_zip.isdigit() and len(temp_zip) == 6:
                        zip = temp_zip
                except:
                    pass

            if not zip:
                try:
                    temp_zip = (
                        raw_address.split(" ")[-1]
                        .strip()
                        .replace(" ", "")
                        .strip()
                        .replace(".", "")
                        .strip()
                    )
                    if temp_zip.isdigit():
                        zip = temp_zip
                        if len(zip) == 3:
                            zip = raw_address.split(" ")[-2].strip() + zip
                            if len(zip) != 6:
                                zip = "<MISSING>"
                        else:
                            zip = "<MISSING>"
                except:
                    pass

            country_code = "IN"

            store_number = "".join(store.xpath("./@id")).strip().replace("post-", "")

            phone = "".join(
                store.xpath('.//p/a[contains(@href,"tel:")]//text()')
            ).strip()

            location_type = "<MISSING>"

            hours_of_operation = "<MISSING>"
            map_link = "".join(store.xpath('.//a[contains(@href,"maps")]/@href'))
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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

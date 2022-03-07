# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "wendys-firstkitchen.co.jp"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    base = "https://wendys-firstkitchen.co.jp"
    search_url = "https://wendys-firstkitchen.co.jp/shop/"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)
        search_sel = lxml.html.fromstring(search_res.text)

        area_ids = search_sel.xpath('//select[@name="areaid"]/option/@value')
        for area_id in area_ids:
            if not area_id:
                continue

            area_url = (
                f"https://wendys-firstkitchen.co.jp/shop/result.php?areaid={area_id}"
            )
            log.info(area_url)
            area_res = session.get(area_url, headers=headers)
            area_sel = lxml.html.fromstring(area_res.text)

            stores = area_sel.xpath("//tr[.//h4]")

            for store in stores:

                page_url = (
                    base
                    + "".join(store.xpath('.//ul[@class="shop-info"]//a/@href')).strip()
                )
                log.info(page_url)
                page_res = session.get(page_url, headers=headers)

                locator_domain = website

                location_name = "".join(store.xpath(".//th/h4//text()")).strip()

                full_address = list(
                    filter(
                        str,
                        [
                            x.strip()
                            for x in store.xpath(
                                './/ul[@class="shop-info"]/li[1]//text()'
                            )
                        ],
                    )
                )
                raw_address = full_address[0].strip()

                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                if street_address is not None:
                    street_address = street_address.replace("Ste", "Suite")
                city = area_id
                state = formatted_addr.state
                zip = formatted_addr.postcode

                country_code = "JP"

                store_number = page_url.split("shopid=")[-1].strip()

                phone = full_address[-1].replace("TEL:", "").strip()

                location_type = "<MISSING>"

                hours = list(
                    filter(
                        str,
                        [
                            x.strip()
                            for x in store.xpath(
                                './/ul[@class="biz-hours"]/li[1]//text()'
                            )
                        ],
                    )
                )
                hours_of_operation = "; ".join(hours)
                map_link = page_res.text.split("google.maps.LatLng(")[1].split(")")[0]
                latitude, longitude = (
                    map_link.split(",")[0].strip(" '").strip(),
                    map_link.split(",")[1].strip(" '").strip(),
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
                    raw_address=raw_address,
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

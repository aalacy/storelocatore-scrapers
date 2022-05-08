# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "dyson.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
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
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    # Your scraper here
    base = "https://www.dyson.com"
    search_url = "https://www.dyson.com/demo-stores"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)

        stores = search_sel.xpath("//p/u/a")

        for no, store in enumerate(stores, 1):

            locator_domain = website

            page_url = base + "".join(store.xpath("./@href"))
            log.info(page_url)
            if "/locations" in page_url:
                continue

            store_res = session.get(page_url, headers=headers)

            store_sel = lxml.html.fromstring(store_res.text)

            location_name = "".join(
                store_sel.xpath("//title[not(@id)]//text()")
            ).strip()

            location_type = "<MISSING>"

            store_info = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            '//h2[text()="Where to find us"]/../div//text()'
                        )
                    ],
                )
            )

            raw_address = ""
            for idx, x in enumerate(store_info, 0):
                if x in ["View on Google Maps", "Store hours:*", "Contact"]:
                    break
                raw_address = (raw_address + ", " + x).strip(", ").strip()

            street_address = ", ".join(raw_address.split(", ")[:-2])

            if street_address is not None and street_address[0] == ",":
                street_address = "".join(street_address[1:]).strip()

            city = raw_address.split(", ")[-2]

            state = raw_address.split(", ")[-1].split(" ")[0]
            zip = raw_address.split(", ")[-1].split(" ")[1]

            country_code = "US"
            raw_address = "<MISSING>"

            store_number = "<MISSING>"
            phone = store_sel.xpath('//a[contains(@href,"tel:")]//text()')
            if len(phone) > 0:
                phone = phone[0]

            hours = store_info[idx + 1 :]

            hours_of_operation = (
                "; ".join(hours[1:])
                .replace("day;", "day:")
                .replace("b;", "b:")
                .replace("Dia:; ", "")
                .replace("Hora:; ", "")
                .strip()
                .split("Contact")[0]
                .strip(" ;")
            )
            map_link = "".join(store_sel.xpath('//a[contains(@href,"map")]/@href'))

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

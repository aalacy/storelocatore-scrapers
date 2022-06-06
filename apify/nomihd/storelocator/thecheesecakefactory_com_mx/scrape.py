# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "thecheesecakefactory.com.mx"
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

    search_url = "https://thecheesecakefactory.com.mx/mapa"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)
        search_sel = lxml.html.fromstring(search_res.text)

        stores = search_sel.xpath(
            '//div[@id="locations"]//div[contains(@id,"panel-categories")]'
        )

        for _, store in enumerate(stores, 1):

            page_url = "https://thecheesecakefactory.com.mx/ubicaciones/"
            locator_domain = website

            location_name = "".join(store.xpath(".//h3//text()")).strip()

            store_info = list(
                filter(
                    str,
                    [x.strip() for x in store.xpath(".//p//text()")],
                )
            )

            raw_address = (
                " ".join(store_info).split("Teléfono:")[0].split("Horarios:")[0].strip()
            )
            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            if street_address is not None:
                street_address = street_address.replace("Ste", "Suite")
            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode
            if zip:
                zip = zip.rsplit(" ", 1)[-1].strip()

            country_code = "MX"

            store_number = "<MISSING>"

            phone = (
                " ".join(store_info)
                .split("Teléfono:")[1]
                .split("Horarios:")[0]
                .split("Delivery:")[0]
                .strip()
                .replace("Restaurante:", "")
                .strip()
            )
            try:
                if phone.count("(55)") == 2:
                    phone = phone.rsplit("(55)", 1)[0].strip()
            except:
                pass

            location_type = "<MISSING>"

            hours_of_operation = (
                "; ".join(store_info).split("Horarios:")[1].strip().strip("; ").strip()
            )

            map_link = "".join(
                search_sel.xpath(
                    f'//p[./strong/text()="{location_name}"]//a[@class="linkwaze"]/@href'
                )
            )

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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

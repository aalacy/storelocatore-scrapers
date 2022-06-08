# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "chrysler.cr"
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

    search_url = "http://www.chrysler.cr/Sucursales/"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)
        search_sel = lxml.html.fromstring(search_res.text)

        stores = search_sel.xpath('//div[@class="mapas"]')

        for store in stores:

            page_url = search_url

            locator_domain = website

            location_name = "".join(
                store.xpath('.//span[@class="titulos2"]//text()')
            ).strip()
            page_url = search_url
            store_info = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store.xpath(
                            './/li[1][@class="textodescripcion"]//text()'
                        )
                    ],
                )
            )
            raw_address = " ".join(store_info).strip().split(":")[1].strip()
            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            if street_address is not None:
                street_address = street_address.replace("Ste", "Suite")
            if not street_address:
                street_address = raw_address
            city = formatted_addr.city
            if not city:
                city = (
                    location_name.split("de ")[1]
                    if "de " in location_name
                    else "<MISSING>"
                )

            if not city or city == "<MISSING>":
                city = "San Pedro"
                street_address = street_address.replace("San Pedro", "").strip()
            state = formatted_addr.state
            zip = formatted_addr.postcode

            country_code = "CR"

            store_number = "<MISSING>"

            phone = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store.xpath(
                            './/li[2][@class="textodescripcion"]//text()'
                        )
                    ],
                )
            )
            phone = "".join(phone).strip().split(":")[1].strip()
            location_type = "<MISSING>"
            hours = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store.xpath(
                            './/span[@class="textodescripcion"]//text()'
                        )
                    ],
                )
            )
            hours_of_operation = " ".join(hours).strip().split("Showroom:")[0].strip()

            if "Horario de atención:" in hours_of_operation:
                hours_of_operation = hours_of_operation.split("Taller de Servicio ")[
                    0
                ].strip()
            else:
                hours_of_operation = hours_of_operation.split("do:")[1].strip()

            hours_of_operation = (
                hours_of_operation.replace("Taller de servicio:", "")
                .replace("Horario de atención:", "")
                .strip()
            )

            map_link = "".join(store.xpath('.//iframe[contains(@src,"maps")]/@src'))
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
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.RAW_ADDRESS,
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

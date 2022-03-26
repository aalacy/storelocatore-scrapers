# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "jeeppr.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
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
    search_url = "https://jeeppr.com/concesionarios.html"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)
        stores = search_sel.xpath("//div[@style='margin: 20px;']")

        for store in stores:

            locator_domain = website

            location_type = "<MISSING>"

            store_info = list(
                filter(str, [x.strip() for x in store.xpath("div[1]/p//text()")])
            )

            location_name = "".join(store.xpath("div[1]/h4//a/text()")).strip()
            raw_address = ", ".join(store_info[:2]).strip()

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            if street_address is not None:
                street_address = street_address.replace("Ste", "Suite")
            city = formatted_addr.city

            state = formatted_addr.state
            if not state:
                state = "PR"
            zip = formatted_addr.postcode

            if "PR00680" in raw_address:
                state = "PR"
                zip = "00680"

            country_code = "PR"
            phone = "".join(
                store.xpath("div[1]/p/strong[contains(text(),'Tel:')]/span/text()")
            ).strip()
            if not phone:
                phone = store.xpath("div[1]/p//span/text()")
                if len(phone) > 0:
                    phone = "".join(phone[0]).strip()

            page_url = "".join(store.xpath("div[1]/h4//a/@href")).strip()

            hours_of_operation = store.xpath(
                "div[1]/p[./strong[contains(text(),'Horarios:')]]//text()"
            )
            hours_of_operation = (
                "; ".join(hours_of_operation)
                .strip()
                .replace("Horarios:;", "")
                .replace("Horarios:", "")
                .strip()
                .replace(":;", ":")
                .strip()
                .split("; Horario de")[0]
                .strip()
            )
            if len(hours_of_operation) > 0 and hours_of_operation[-1] == ";":
                hours_of_operation = "".join(hours_of_operation[:-1]).strip()

            log.info(hours_of_operation)
            store_number = "<MISSING>"

            map_link = "".join(
                store.xpath(".//iframe[contains(@src,'maps/embed')]//@href")
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
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
